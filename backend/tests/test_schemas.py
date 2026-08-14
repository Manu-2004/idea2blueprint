import json
from pathlib import Path

from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.common import Section, SectionGroup, SectionItem, Spec

EXAMPLES_PATH = Path(__file__).resolve().parents[1] / "examples" / "sample_briefs.json"


def test_sample_briefs_validate_against_brief_schema():
    templates = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    assert len(templates) == 6
    for data in templates.values():
        brief = Brief.model_validate(data)
        assert brief.idea
        assert brief.who
        assert brief.problem


def test_spec_round_trips_through_json():
    spec = Spec(
        sections=[
            Section(
                id="problem",
                num="01",
                title="Problem and target user",
                lead="a lead",
                groups=[SectionGroup(label="Primary user", items=[SectionItem(text="a")])],
            )
        ]
    )
    restored = Spec.model_validate_json(spec.model_dump_json())
    assert restored == spec
