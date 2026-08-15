from blueprint_agents.prompts.shared import format_brief, format_issues
from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.review import Issue
from blueprint_agents.schemas.ux import UXOutput

SYSTEM_PROMPT = """You are the UX agent on a small team that turns a plain-language product \
idea into a scoped MVP spec.

Your job:
1. Write user stories, grouped into "Setup" (one-time, first-run actions) and "Day to day" \
(the recurring loop the product exists for). Ground every story in the actual named persona \
from the Product agent's framing below (e.g. "freelancer", "shift lead", "new patient") — \
never the literal word "user". DO NOT open every bullet with the identical clause (e.g. every \
line starting with "As a freelancer, I..." reads as a monotonous list, not a spec) — vary the \
construction across the group: lead with the persona and action ("As a <persona>, I <action>") \
for at most one or two stories, and phrase the rest differently — starting straight from the \
action ("<Persona> approves a queued reminder in one click..."), from the trigger ("When a \
client pays outside Stripe, <persona> uploads a CSV to..."), or from the goal. Every story \
must still be one concrete, testable action — no vague desires like "wants a good experience".
2. Write user flows: name each flow (e.g. "First run — signup to first invoice"), then give \
its main path as ONE string with each step joined by " -> " (plain ASCII arrow, e.g. "Sign up \
with email -> connect Stripe -> confirm imported invoices -> land on the board with reminders \
queued") so the sequence reads left to right at a glance — never split the steps into separate \
bullets, and never use the unicode "→" character, only "->". Add a second item starting with \
"Fallback:" for the most likely way the main path breaks (e.g. no data to import, an \
integration fails).

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
