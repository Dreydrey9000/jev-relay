"""Offline worker. Launch only through the supervised local provider."""
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-path", required=True)
    args = parser.parse_args()
    from laya_mlx import load
    from laya_mlx.common import render_options, build_prefix, serialize_state
    request = json.load(sys.stdin)
    agent = load(args.model_path, batch_size=1)
    # Upstream truncates state to fit. Reject instead of silently losing evidence.
    for question in request["questions"].values():
        internal = agent._to_internal(question)
        tokenize = lambda text: agent.tok(text.replace(agent.tok.mask_token, " "), add_special_tokens=False)["input_ids"]
        options = [tokenize(" " + text) for text in render_options(internal)]
        head = tokenize(f'{internal["t"]} question: {internal["ins"]}')
        budget = agent.cfg.get("head_max_len", 192) - sum(1 + len(ids) for ids in options)
        if any(len(ids) > 48 for ids in options) or budget < 16 or len(head) > max(8, budget):
            raise ValueError("Input exceeds local question budget")
        prefix, _ = build_prefix(agent.tok, internal, agent.cfg.get("head_max_len", 192))
        if len(prefix) + len(tokenize(serialize_state(request["state"]))) + 1 > agent.cfg["max_len"]:
            raise ValueError("Input exceeds local context budget")
    print(json.dumps(agent.predict(request["state"], request["questions"]), allow_nan=False))


if __name__ == "__main__":
    main()
