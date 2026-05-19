from __future__ import annotations

import shutil
import tempfile
from dataclasses import asdict
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from voiceclinic.agent import ClinicAgent
from voiceclinic.config import Settings, load_settings
from voiceclinic.db import init_db, reset_db, seed_demo_data
from voiceclinic.guardrails import ClinicalPolicyObserver
from voiceclinic.scheduling import Scheduler
from voiceclinic.voice.stt import LocalWhisperSTT, VoiceDependencyError
from voiceclinic.voice.tts import PiperTTS


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    patient_phone: str = "+34600111222"
    session_id: str | None = None


class ChatResponse(BaseModel):
    text: str
    action: str
    data: dict
    session_id: str


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    init_db(settings.db_path)
    seed_demo_data(settings.db_path)
    policy_observer = ClinicalPolicyObserver()

    app = FastAPI(title="VoiceClinic Local", version="0.1.0")
    app.state.policy_observer = policy_observer
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    web_dir = Path(__file__).resolve().parents[2] / "web"
    if web_dir.exists():
        app.mount("/demo", StaticFiles(directory=web_dir, html=True), name="demo")

    @app.get("/health")
    def health() -> dict:
        return {"ok": True, "db": str(settings.db_path)}

    @app.post("/demo/reset")
    def reset_demo() -> dict:
        reset_db(settings.db_path)
        policy_observer.clear()
        return {"ok": True}

    @app.get("/patients")
    def patients() -> list[dict]:
        return [asdict(patient) for patient in Scheduler(settings.db_path).list_patients()]

    @app.get("/appointments")
    def appointments(phone: str = "+34600111222") -> list[dict]:
        return [
            asdict(item)
            for item in Scheduler(settings.db_path).list_patient_appointments(phone)
        ]

    @app.get("/slots")
    def slots(specialty: str | None = None, limit: int = 5) -> list[dict]:
        return [
            asdict(item)
            for item in Scheduler(settings.db_path).list_available_slots(
                specialty=specialty,
                limit=max(1, min(limit, 25)),
            )
        ]

    @app.post("/agent/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        session_id = request.session_id or str(uuid4())
        agent = ClinicAgent(
            settings.db_path,
            settings=settings,
            policy_observer=policy_observer,
        )
        reply = await agent.handle_text(
            request.message,
            patient_phone=request.patient_phone,
            session_id=session_id,
        )
        return ChatResponse(
            text=reply.text,
            action=reply.action,
            data=reply.data,
            session_id=session_id,
        )

    @app.post("/voice/turn")
    async def voice_turn(
        audio: Annotated[UploadFile, File()],
        patient_phone: Annotated[str, Form()] = "+34600111222",
        session_id: Annotated[str | None, Form()] = None,
    ) -> dict:
        artifact_dir = Path(tempfile.gettempdir()) / "voiceclinic"
        artifact_dir.mkdir(parents=True, exist_ok=True)
        source = artifact_dir / f"{uuid4()}-{audio.filename or 'turn.webm'}"
        with source.open("wb") as handle:
            shutil.copyfileobj(audio.file, handle)

        try:
            transcript = LocalWhisperSTT(settings.whisper_model).transcribe(source)
        except VoiceDependencyError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        turn_session_id = session_id or str(uuid4())
        agent = ClinicAgent(
            settings.db_path,
            settings=settings,
            policy_observer=policy_observer,
        )
        reply = await agent.handle_text(
            transcript,
            patient_phone=patient_phone,
            session_id=turn_session_id,
        )

        audio_url = None
        try:
            wav_path = PiperTTS(settings).synthesize(
                reply.text,
                artifact_dir / f"{uuid4()}.wav",
            )
            audio_url = f"/voice/audio/{wav_path.name}"
        except VoiceDependencyError:
            audio_url = None

        return {
            "session_id": turn_session_id,
            "transcript": transcript,
            "text": reply.text,
            "action": reply.action,
            "data": reply.data,
            "audio_url": audio_url,
        }

    @app.get("/voice/audio/{name}")
    def voice_audio(name: str) -> FileResponse:
        path = Path(tempfile.gettempdir()) / "voiceclinic" / name
        if not path.exists() or path.suffix.lower() != ".wav":
            raise HTTPException(status_code=404, detail="Audio not found")
        return FileResponse(path, media_type="audio/wav")

    return app


app = create_app()
