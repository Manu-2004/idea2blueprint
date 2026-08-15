from blueprint_agents.api.progress import compute_step
from blueprint_agents.schemas.events import NodeEvent


def _event(node, round_=0):
    return NodeEvent(node=node, revision_round=round_)


def test_no_events_is_step_zero():
    assert compute_step([]) == 0


def test_product_only_is_step_three():
    assert compute_step([_event("product", 0)]) == 3


def test_ux_alone_without_technical_stays_at_three():
    assert compute_step([_event("product", 0), _event("ux", 0)]) == 3


def test_ux_and_technical_same_round_is_step_five():
    events = [_event("product", 0), _event("ux", 0), _event("technical", 0)]
    assert compute_step(events) == 5


def test_stale_ux_from_earlier_round_does_not_count_with_fresh_technical():
    # ux is still on round 0 while technical has already regenerated for round 1 — the
    # revision loop always regenerates both siblings together, so this shouldn't happen in
    # practice, but the function should not falsely report step 5 if it did.
    events = [_event("product", 0), _event("ux", 0), _event("technical", 0), _event("technical", 1)]
    assert compute_step(events) == 3


def test_assemble_is_step_six_regardless_of_other_events():
    events = [_event("product", 0), _event("ux", 0), _event("technical", 0), _event("assemble", 0)]
    assert compute_step(events) == 6


def test_step_is_monotonic_across_a_revision_round():
    # round 0: product -> ux+technical -> (blocker) -> round 1: ux+technical again -> assemble
    events = [_event("product", 0), _event("ux", 0), _event("technical", 0)]
    step_after_round_0 = compute_step(events)
    events += [_event("ux", 1), _event("technical", 1)]
    step_mid_round_1 = compute_step(events)
    events += [_event("assemble", 1)]
    step_after_assemble = compute_step(events)

    assert step_after_round_0 == 5
    assert step_mid_round_1 == 5
    assert step_after_assemble == 6
    assert step_after_round_0 <= step_mid_round_1 <= step_after_assemble
