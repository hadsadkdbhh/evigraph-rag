from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class EvidenceNode:
    node_id: str
    node_type: str
    content: str | dict[str, Any]
    source_doc: str | None = None
    page_number: int | None = None
    bbox: list[float] | None = None
    modality: str = "text"
    confidence: float = 1.0
    scores: dict[str, float] = field(default_factory=dict)
    cost: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def text(self) -> str:
        if isinstance(self.content, str):
            return self.content
        return " ".join(f"{k}: {v}" for k, v in self.content.items())


@dataclass
class EvidenceEdge:
    source: str
    target: str
    edge_type: str
    weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceScore:
    relevance: float
    utility: float
    grounding: float
    uncertainty: float
    misleading_risk: float
    contradiction_risk: float
    source_reliability: float
    cost: float
    final_score: float
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Action:
    action_type: str
    target_node_ids: list[str]
    params: dict[str, Any] = field(default_factory=dict)
    estimated_cost: dict[str, float] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Answer:
    text: str
    citations: list[str]
    calculations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
