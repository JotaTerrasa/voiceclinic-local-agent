from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
MIN_PYTHON = (3, 11)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-platform project tasks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("copy-env")
    subparsers.add_parser("setup")
    subparsers.add_parser("setup-voice")
    subparsers.add_parser("setup-orchestration")
    subparsers.add_parser("setup-livekit")
    subparsers.add_parser("setup-all")
    subparsers.add_parser("init-db")
    subparsers.add_parser("reset-db")
    subparsers.add_parser("chat")
    subparsers.add_parser("audiosocket")
    subparsers.add_parser("test")
    subparsers.add_parser("lint")
    subparsers.add_parser("docker-up")
    subparsers.add_parser("docker-down")

    api_parser = subparsers.add_parser("api")
    api_parser.add_argument("--host", default="127.0.0.1")
    api_parser.add_argument("--port", default="8000")

    args = parser.parse_args()

    if args.command == "copy-env":
        copy_env()
    elif args.command == "setup":
        setup()
    elif args.command == "setup-voice":
        setup_voice()
    elif args.command == "setup-orchestration":
        setup_orchestration()
    elif args.command == "setup-livekit":
        setup_livekit()
    elif args.command == "setup-all":
        setup_all()
    elif args.command == "init-db":
        run_voiceclinic("init-db")
    elif args.command == "reset-db":
        run_voiceclinic("reset-db")
    elif args.command == "chat":
        run_voiceclinic("chat")
    elif args.command == "api":
        run_voiceclinic("api", "--host", args.host, "--port", str(args.port))
    elif args.command == "audiosocket":
        run_voiceclinic("audiosocket")
    elif args.command == "test":
        run(venv_python(), "-m", "pytest")
    elif args.command == "lint":
        run(venv_python(), "-m", "ruff", "check", "src", "tests", "scripts")
    elif args.command == "docker-up":
        run("docker", "compose", "up", "--build")
    elif args.command == "docker-down":
        run("docker", "compose", "down")


def copy_env() -> None:
    source = ROOT / ".env.example"
    target = ROOT / ".env"
    if target.exists():
        print(".env already exists; leaving it unchanged.")
        return
    shutil.copyfile(source, target)
    print("Created .env from .env.example.")


def setup() -> None:
    require_supported_python()
    run(sys.executable, "-m", "venv", str(VENV))
    run(venv_python(), "-m", "pip", "install", "-U", "pip")
    run(venv_python(), "-m", "pip", "install", "-e", ".[dev]")


def setup_voice() -> None:
    ensure_venv()
    run(venv_python(), "-m", "pip", "install", "-e", ".[dev,voice]")


def setup_orchestration() -> None:
    ensure_venv()
    run(venv_python(), "-m", "pip", "install", "-e", ".[dev,orchestration]")


def setup_livekit() -> None:
    ensure_venv()
    run(venv_python(), "-m", "pip", "install", "-e", ".[dev,orchestration,livekit]")


def setup_all() -> None:
    ensure_venv()
    run(venv_python(), "-m", "pip", "install", "-e", ".[dev,voice,orchestration,livekit]")


def run_voiceclinic(*args: str) -> None:
    ensure_venv()
    run(venv_python(), "-m", "voiceclinic.cli", *args)


def ensure_venv() -> None:
    if not venv_python().exists():
        raise SystemExit("Missing .venv. Run `python scripts/dev.py setup` first.")


def require_supported_python() -> None:
    if sys.version_info < MIN_PYTHON:
        version = ".".join(str(part) for part in MIN_PYTHON)
        current = ".".join(str(part) for part in sys.version_info[:3])
        raise SystemExit(f"Python {version}+ is required. Current interpreter: {current}.")


def venv_python() -> Path:
    if sys.platform.startswith("win"):
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def run(*command: object) -> None:
    rendered = [str(part) for part in command]
    print("+", " ".join(rendered), flush=True)
    subprocess.run(rendered, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
