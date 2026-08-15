from blueprint_agents.schemas.events import NodeEvent

# The real node sequence (product -> {ux, technical} -> reviewer -> assemble|revise) doesn't
# map 1:1 to the frontend's 6 fake-timer labels (`GEN_LABELS`), so this collapses it onto the
# same 0-6 step range: product's single call covers 3 conceptual labels ("reading idea",
# "framing problem", "cutting features"), ux+technical together cover the next 2, and
# assemble is the final step. Deliberately monotonic — callers should take
# `max(previous_step, compute_step(events))` so a revision loop sending agents back for
# another round never un-ticks an already-checked step.


def compute_step(events: list[NodeEvent]) -> int:
    if any(event.node == "assemble" for event in events):
        return 6

    ux_rounds = [event.revision_round for event in events if event.node == "ux"]
    technical_rounds = [event.revision_round for event in events if event.node == "technical"]
    if ux_rounds and technical_rounds and max(ux_rounds) == max(technical_rounds):
        return 5

    if any(event.node == "product" for event in events):
        return 3

    return 0
