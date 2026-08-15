import operator
from typing import Annotated, Optional

from typing_extensions import TypedDict

from blueprint_agents.schemas.brief import Brief
from blueprint_agents.schemas.common import Spec
from blueprint_agents.schemas.events import NodeEvent
from blueprint_agents.schemas.product import ProductOutput
from blueprint_agents.schemas.review import ReviewVerdict
from blueprint_agents.schemas.technical import TechnicalOutput
from blueprint_agents.schemas.ux import UXOutput


class GraphState(TypedDict, total=False):
    brief: Brief

    product_output: Optional[ProductOutput]
    ux_output: Optional[UXOutput]
    technical_output: Optional[TechnicalOutput]

    review: Optional[ReviewVerdict]
    revision_round: int
    max_revision_rounds: int

    spec: Optional[Spec]

    # Append-only debug log ("node X ran, verdict Y"), surfaced via `--verbose`. Not part of
    # the frontend-facing output.
    trace: Annotated[list[str], operator.add]

    # Append-only structured log of the same node completions, for the API layer to compute
    # polling progress from (see api/progress.py) without parsing `trace` strings.
    events: Annotated[list[NodeEvent], operator.add]
