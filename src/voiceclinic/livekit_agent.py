from __future__ import annotations

from pathlib import Path

from voiceclinic.agent import ClinicAgent
from voiceclinic.config import load_settings
from voiceclinic.db import init_db, seed_demo_data
from voiceclinic.orchestration import build_livekit_graph


def build_instructions() -> str:
    return """
    Eres el agente telefonico de una clinica privada.
    Objetivo: gestionar citas, cambios, cancelaciones y consultas sencillas de pacientes.
    Habla en espanol claro, frases cortas y confirma siempre fecha, hora, especialidad y doctor.
    No des diagnosticos. Si el paciente expresa urgencia medica, indica que llame al 112.
    Usa las herramientas de agenda del backend local para cualquier accion sobre citas.
    """


def build_langgraph_llm_adapter(db_path: Path | str | None = None):
    """Build a LiveKit LLMAdapter around the local VoiceClinic LangGraph graph."""

    try:
        from livekit.plugins import langchain
    except ImportError as exc:
        raise ImportError(
            "LiveKit LangChain integration requires "
            "`python scripts/dev.py setup-livekit` or `pip install -e .[livekit,orchestration]`."
        ) from exc

    settings = load_settings()
    resolved_db_path = Path(db_path) if db_path else settings.db_path
    init_db(resolved_db_path)
    seed_demo_data(resolved_db_path)

    agent = ClinicAgent(resolved_db_path, settings=settings)
    graph = build_livekit_graph(agent)
    return langchain.LLMAdapter(graph=graph)


def main() -> None:
    """Print the local settings needed by a LiveKit Agents entrypoint.

    The runnable local demo in this repo is the FastAPI + AudioSocket path. For
    LiveKit, use build_langgraph_llm_adapter() as the AgentSession LLM.
    """
    settings = load_settings()
    print("Configura LiveKit Agents con:")
    print("- LIVEKIT_URL=ws://localhost:7880")
    print(f"- LLM provider: {settings.llm_provider}")
    print(f"- Ollama: {settings.ollama_base_url} / {settings.ollama_model}")
    print("- LangGraph adapter: voiceclinic.livekit_agent.build_langgraph_llm_adapter()")
    print("- Instrucciones:")
    print(build_instructions())


if __name__ == "__main__":
    main()
