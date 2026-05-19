from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict

import uvicorn

from voiceclinic.agent import ClinicAgent
from voiceclinic.api import create_app
from voiceclinic.config import load_settings
from voiceclinic.db import init_db, reset_db, seed_demo_data
from voiceclinic.scheduling import Scheduler
from voiceclinic.telephony.audiosocket_server import AudioSocketAgentServer


def main() -> None:
    parser = argparse.ArgumentParser(prog="voiceclinic")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db")
    subparsers.add_parser("reset-db")

    chat_parser = subparsers.add_parser("chat")
    chat_parser.add_argument("--phone", default="+34600111222")

    api_parser = subparsers.add_parser("api")
    api_parser.add_argument("--host", default="127.0.0.1")
    api_parser.add_argument("--port", type=int, default=8000)

    slots_parser = subparsers.add_parser("slots")
    slots_parser.add_argument("--specialty", default=None)

    audiosocket_parser = subparsers.add_parser("audiosocket")
    audiosocket_parser.add_argument("--host", default=None)
    audiosocket_parser.add_argument("--port", type=int, default=None)

    args = parser.parse_args()
    settings = load_settings()

    if args.command == "init-db":
        init_db(settings.db_path)
        seed_demo_data(settings.db_path)
        print(f"Base demo lista en {settings.db_path}")
        return

    if args.command == "reset-db":
        reset_db(settings.db_path)
        print(f"Base demo reiniciada en {settings.db_path}")
        return

    if args.command == "slots":
        init_db(settings.db_path)
        seed_demo_data(settings.db_path)
        scheduler = Scheduler(settings.db_path)
        for slot in scheduler.list_available_slots(specialty=args.specialty, limit=10):
            print(asdict(slot))
        return

    if args.command == "chat":
        init_db(settings.db_path)
        seed_demo_data(settings.db_path)
        asyncio.run(_interactive_chat(settings, args.phone))
        return

    if args.command == "api":
        uvicorn.run(create_app(settings), host=args.host, port=args.port)
        return

    if args.command == "audiosocket":
        init_db(settings.db_path)
        seed_demo_data(settings.db_path)
        server = AudioSocketAgentServer(
            settings=settings,
            host=args.host or settings.audiosocket_host,
            port=args.port or settings.audiosocket_port,
        )
        asyncio.run(server.serve_forever())


async def _interactive_chat(settings, patient_phone: str) -> None:
    agent = ClinicAgent(settings.db_path, settings=settings)
    print("VoiceClinic chat local. Escribe 'salir' para terminar.")
    while True:
        message = input("> ").strip()
        if message.lower() in {"salir", "exit", "quit"}:
            break
        reply = await agent.handle_text(message, patient_phone=patient_phone)
        print(reply.text)


if __name__ == "__main__":
    main()
