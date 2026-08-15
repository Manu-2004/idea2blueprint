from typing import Literal

from pydantic import BaseModel


class NodeEvent(BaseModel):
    """One node's completion, appended to `GraphState.events` as the graph runs. Used by
    the API layer to compute polling progress (`api/progress.py`) without depending on the
    human-readable `trace` string format."""

    node: Literal["intake", "product", "ux", "technical", "reviewer", "assemble"]
    revision_round: int
