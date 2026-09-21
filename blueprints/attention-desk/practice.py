"""Create synthetic practice requests; never connect, infer or send."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from jev_relay.schema import validate_request


def build_requests():
    package = json.loads(Path(__file__).with_name("templates.json").read_text())
    requests = {}
    examples = {
        "attention_inbox": "SYNTHETIC. Current time: 2030-01-10 09:00 UTC. Message: Please approve the workshop agenda by 17:00 UTC tomorrow so we can print it. No action is required this morning.",
        "waiting_on_someone": "SYNTHETIC. Owner requested: Please send the final workshop agenda. Reply: Thanks, I have seen your request and will send it tomorrow. No attachment or agenda was supplied.",
    }
    for template in package["templates"]:
        request = {"state": examples.get(template["id"], "SYNTHETIC validation fixture; insufficient context."), "questions": {"category": {"type": "choice", "instructions": template["instruction"], "criteria": template["choices"]}}}
        validate_request(request)
        if template["id"] in examples:
            requests[template["id"]] = request
    return requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    requests = build_requests()
    args.output.mkdir(parents=True, exist_ok=True)
    filenames = {"attention_inbox": "inbox-request.json", "waiting_on_someone": "waiting-request.json"}
    outputs = {name: json.dumps(requests[key], indent=2) + "\n" for key, name in filenames.items()}
    outputs["worksheet.md"] = """# Synthetic practice worksheet

Label each request before checking these suggested answers:
- Inbox: important. Explicit request due tomorrow; no immediate action needed.
- Waiting: waiting. Acknowledgment did not supply the agenda.

For each: record your label, evidence, any model's actual provider and status,
whether its advice agrees, and why you accept or correct it.
These two cases are teaching examples, not a quality benchmark.
No model was called by the generator. Review fallback is expected without one.
"""
    for name in outputs:
        if (args.output / name).exists():
            parser.error(f"Refusing to overwrite {args.output / name}; choose a new output directory")
    for name, body in outputs.items():
        (args.output / name).write_text(body)
    print("Validated 8 templates; wrote 2 synthetic requests and a worksheet. No inference or delivery.")


if __name__ == "__main__":
    main()
