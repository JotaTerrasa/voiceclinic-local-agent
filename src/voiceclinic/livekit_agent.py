from __future__ import annotations

from voiceclinic.config import load_settings


def build_instructions() -> str:
    return """
    Eres el agente telefonico de una clinica privada.
    Objetivo: gestionar citas, cambios, cancelaciones y consultas sencillas de pacientes.
    Habla en espanol claro, frases cortas y confirma siempre fecha, hora, especialidad y doctor.
    No des diagnosticos. Si el paciente expresa urgencia medica, indica que llame al 112.
    Usa las herramientas de agenda del backend local para cualquier accion sobre citas.
    """


def main() -> None:
    """LiveKit entrypoint placeholder.

    The runnable local demo in this repo is the FastAPI + AudioSocket path. This
    module documents where the same domain agent plugs into LiveKit Agents when
    you want to mirror the video more closely.
    """
    settings = load_settings()
    print("Configura LiveKit Agents con:")
    print("- LIVEKIT_URL=ws://localhost:7880")
    print(f"- Ollama: {settings.ollama_base_url} / {settings.ollama_model}")
    print("- Instrucciones:")
    print(build_instructions())


if __name__ == "__main__":
    main()
