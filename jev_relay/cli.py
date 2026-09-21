import argparse
import json
from pathlib import Path
import sys
from .router import route


def main():
    parser = argparse.ArgumentParser(description="Jev Relay: local-first advisory decisions")
    parser.add_argument("--input", help="Request JSON file; defaults to stdin")
    parser.add_argument("--config", default=str(Path.home()/".config/jev-relay/config.json"))
    parser.add_argument("--importance", choices=["routine", "important"], default="routine")
    parser.add_argument("--allow-cloud", action="store_true")
    parser.add_argument("--sanitized", action="store_true", help="Assert input is suitable for third-party processing; not an automatic sanitizer")
    parser.add_argument("--ack-resource-warning", action="store_true", help="Use only after explicit approval of the guard's current warning")
    args = parser.parse_args()
    try:
        with (open(args.input) if args.input else sys.stdin) as stream:
            raw = stream.read(32769)
        if len(raw.encode()) > 32768:
            raise ValueError("Request exceeds 32 KiB")
        config_path = Path(args.config).expanduser()
        config = json.loads(config_path.read_text()) if config_path.exists() else {}
        result = route(json.loads(raw), config, importance=args.importance, cloud_allowed=args.allow_cloud, sensitive=not args.sanitized, warning_ack=args.ack_resource_warning)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "invalid_request", "error": type(exc).__name__, "requires_review": True}))
        return 2
    print(json.dumps(result, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
