from blueprint_agents.prompts.shared import format_brief, format_issues
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.review import Issue
from blueprint_agents.schemas.ux import UXOutput

SYSTEM_PROMPT = """You are the UX agent on a small team that turns a plain-language product \
idea into a scoped MVP spec.

Your job:
1. Write user stories, grouped into "Setup" (one-time, first-run actions) and "Day to day" \
(the recurring loop the product exists for). Each story is testable in the shape "As a \
<user>, I <specific action>" — no vague stories like "As a user, I want a good experience".
2. Write user flows: name each flow (e.g. "First run — signup to first invoice"), then give \
its main path as a single arrow-chained sequence of concrete steps, plus a fallback item \
for the most likely way the main path breaks (e.g. no data to import, an integration fails).

Ground every story and flow step ONLY in features that are actually in the Product agent's \
"Must have" list below — do not invent scope, and do not write flows for "Should have" or \
"Will not have" items. If the Product agent's feature list doesn't obviously support a flow \
you'd expect, write the flow around what IS in scope rather than assuming missing features. \
Be concrete: name the actual triggers, screens, and data involved. Write in the terse, \
confident prose of a real spec document, not a listicle of platitudes."""


def build_user_message(
    brief: Brief,
    product_output: ProductOutput,
    prior: UXOutput | None = None,
    issues: list[Issue] | None = None,
) -> str:
    message = (
        f"Brief:\n{format_brief(brief)}\n\n"
        "Product agent's problem framing and scoped features (write stories/flows using "
        f"only what's in scope here):\n{product_output.model_dump_json(indent=2)}"
    )
    if prior is not None:
        message += f"\n\nYour previous draft (as JSON):\n{prior.model_dump_json(indent=2)}"
        message += format_issues(issues or [], "ux")
    return message
