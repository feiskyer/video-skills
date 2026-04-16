#!/usr/bin/env python3
"""Check narration provider environment variables without revealing secrets.

Usage:
    python3 check_env.py [azure|gemini|all]
"""

import os
import sys

ENV_FILE = os.path.expanduser("~/.narrate_video.env")
REQUIRED_VARS = {
    "azure": ["AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"],
    "gemini": ["GEMINI_API_KEY"],
}
OPTIONAL_VARS = {
    "gemini": ["GEMINI_TTS_MODEL"],
}


def load_present_vars():
    found = {}
    if not os.path.isfile(ENV_FILE):
        return found

    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            name, value = line.split("=", 1)
            name = name.strip()
            value = value.strip()
            if value:
                found[name] = True
    return found


def print_template(provider):
    print(f"  Create or update {ENV_FILE} with:")
    if provider in ("azure", "all"):
        print("  AZURE_SPEECH_KEY=your-key-here")
        print("  AZURE_SPEECH_REGION=your-region-here")
    if provider in ("gemini", "all"):
        print("  GEMINI_API_KEY=your-key-here")
        print("  # Optional override")
        print("  GEMINI_TTS_MODEL=gemini-3.1-flash-tts-preview")


def check_provider(provider, found):
    ok = True
    print(f"[{provider}]")
    for var in REQUIRED_VARS[provider]:
        if var in found:
            print(f"OK: {var} is set")
        else:
            print(f"MISSING: {var}")
            ok = False
    for var in OPTIONAL_VARS.get(provider, []):
        if var in found:
            print(f"OK: {var} is set")
        else:
            print(f"INFO: {var} is not set (optional)")
    return ok


def check_env(provider):
    found = load_present_vars()
    if not os.path.isfile(ENV_FILE):
        print(f"MISSING: {ENV_FILE} not found")
        print_template(provider)
        return False

    ok = True
    providers = ["azure", "gemini"] if provider == "all" else [provider]
    for item in providers:
        provider_ok = check_provider(item, found)
        ok = ok and provider_ok
        if item != providers[-1]:
            print()

    if not ok:
        print(f"\nAdd missing vars to {ENV_FILE}")
    return ok


def main():
    provider = sys.argv[1].lower() if len(sys.argv) > 1 else "azure"
    if provider not in {"azure", "gemini", "all"}:
        print("Usage: python3 check_env.py [azure|gemini|all]")
        return 1
    return 0 if check_env(provider) else 1


if __name__ == "__main__":
    raise SystemExit(main())
