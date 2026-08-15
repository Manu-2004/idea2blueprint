import argparse
import json
import sys
from pathlib import Path

from blueprint_agents.config import get_settings
from blueprint_agents.graph import build_graph
from blueprint_agents.schemas.brief import Brief

EXAMPLES_PATH = Path(__file__).resolve().parents[2] / "examples" / "sample_briefs.json"


def load_brief(args: argparse.Namespace) -> Brief:
    if args.brief:
        data = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        return Brief.model_validate(data)
    if args.template:
        templates = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
        if args.template not in templates:
            available = ", ".join(sorted(templates))
            raise SystemExit(f"Unknown template '{args.template}'. Available: {available}")
        return Brief.model_validate(templates[args.template])
    raise SystemExit("Provide either --brief <path> or --template <key>.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Idea2Blueprint agentic pipeline.")
    parser.add_argument("--brief", help="Path to a JSON file with brief fields.")
    parser.add_argument("--template", help="Key into examples/sample_briefs.json (e.g. 'saas').")
    parser.add_argument("--out", help="Path to write the resulting spec JSON. Defaults to stdout.")
    parser.add_argument(
        "--verbose", action="store_true", help="Print the reviewer/agent trace to stderr after the spec."
    )
    args = parser.parse_args()

    brief = load_brief(args)
    settings = get_settings()
    if not settings.openai_api_key:
        print(
            "Warning: OPENAI_API_KEY is not set — this will fail once an agent node runs. "
            "Copy .env.example to .env and fill it in.",
            file=sys.stderr,
        )

    graph = build_graph()
    result = graph.invoke(
        {
            "brief": brief,
            "revision_round": 0,
            "max_revision_rounds": settings.max_revision_rounds,
            "trace": [],
            "events": [],
        }
    )

    output = result["spec"].model_dump_json(indent=2)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
        print(f"Wrote spec to {args.out}")
    else:
        print(output)

    if args.verbose:
        print("\n--- trace ---", file=sys.stderr)
        for line in result.get("trace", []):
            print(line, file=sys.stderr)


if __name__ == "__main__":
    main()
