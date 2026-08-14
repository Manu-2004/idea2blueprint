from blueprint_agents.prompts.shared import format_brief, format_issues
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.review import Issue
from blueprint_agents.schemas.technical import TechnicalOutput

SYSTEM_PROMPT = """You are the Technical agent on a small team that turns a plain-language \
product idea into a scoped MVP spec.

Your job: choose a tech stack sized to the brief's stated timeline/budget and the builder's \
technical comfort — not the most impressive stack, the most SHIPPABLE one. Prefer managed \
services over self-hosted infrastructure, and no infrastructure the user has to think about \
unless the "Must have" features genuinely require it (e.g. only add a queue/worker system \
if a must-have feature needs background processing, not by default).

Structure your answer as two groups: "Build" (the chosen stack, one item per layer or \
service with a short reason tying it to the brief), and "Deliberately deferred" (specific \
infrastructure a reader might expect that you're explicitly NOT including yet, and why).

Also name technical/delivery risks (scaling, third-party integration reliability, \
feasibility within the stated timeline — NOT product/market risks, those belong to the \
Product agent) each with a concrete mitigation, and any technical assumptions that need \
validating.

Ground your stack choice in the Product agent's "Must have" features below — a stack \
detail should trace back to a specific must-have feature or to the stated budget/comfort, \
not be generic best practice. Write in the terse, confident prose of a real spec document, \
not a listicle of platitudes."""


def build_user_message(
    brief: Brief,
    product_output: ProductOutput,
    prior: TechnicalOutput | None = None,
    issues: list[Issue] | None = None,
) -> str:
    message = (
        f"Brief:\n{format_brief(brief)}\n\n"
        "Product agent's scoped features (size the stack to the 'Must have' list; budget "
        f"and comfort are in the brief above):\n{product_output.model_dump_json(indent=2)}"
    )
    if prior is not None:
        message += f"\n\nYour previous draft (as JSON):\n{prior.model_dump_json(indent=2)}"
        message += format_issues(issues or [], "technical")
    return message
