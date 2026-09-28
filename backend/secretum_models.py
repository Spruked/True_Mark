"""Account, Sanctum, project, and authority-boundary contracts.

These contracts are intentionally separate from the legacy token issuance
records. A draft project belongs to the account's mutable Sanctum; only a
sealed project may produce a canonical certificate manifest.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ProjectState(str, Enum):
    WORKING_COPY = "WORKING_COPY"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    COMMIT_PENDING = "COMMIT_PENDING"
    COMMITTED = "COMMITTED"
    SEALED = "SEALED"
    RELEASED = "RELEASED"
    DELETED = "DELETED"
    EXPIRED = "EXPIRED"


class EvidenceState(str, Enum):
    STAGED = "STAGED"
    ATTACHED = "ATTACHED"
    COMMIT_PENDING = "COMMIT_PENDING"
    COMMITTED = "COMMITTED"
    SEALED = "SEALED"
    RELEASED = "RELEASED"
    DELETED = "DELETED"
    EXPIRED = "EXPIRED"


ALLOWED_TRANSITIONS = {
    ProjectState.WORKING_COPY: {ProjectState.READY_FOR_REVIEW, ProjectState.DELETED, ProjectState.EXPIRED},
    ProjectState.READY_FOR_REVIEW: {ProjectState.WORKING_COPY, ProjectState.COMMIT_PENDING},
    ProjectState.COMMIT_PENDING: {ProjectState.READY_FOR_REVIEW, ProjectState.COMMITTED},
    ProjectState.COMMITTED: {ProjectState.SEALED},
    ProjectState.SEALED: {ProjectState.RELEASED},
    ProjectState.RELEASED: set(),
    ProjectState.DELETED: set(),
    ProjectState.EXPIRED: set(),
}


class EvidenceItem(BaseModel):
    id: str
    filename: str
    sha256: str
    state: EvidenceState = EvidenceState.STAGED
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectRecord(BaseModel):
    id: str
    account_id: str
    sanctum_id: str
    title: str
    object_type: str
    state: ProjectState = ProjectState.WORKING_COPY
    evidence: List[EvidenceItem] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    ownership: Dict[str, Any] = Field(default_factory=dict)
    notes: str = ""


class CommitRequest(BaseModel):
    project_id: str
    confirmation: str


class CanonicalCertificateManifest(BaseModel):
    """Canonical representation derived from an authoritative sealed record."""

    manifest_version: str = "1.0"
    authority_event_id: str
    project_id: str
    certificate_profile: str
    layer_count: int
    canonical_facts: Dict[str, Any]
    evidence_hashes: List[str]


def can_transition(current: ProjectState, target: ProjectState) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, set())


def require_transition(current: ProjectState, target: ProjectState) -> None:
    if not can_transition(current, target):
        raise ValueError(f"Project cannot transition from {current.value} to {target.value}.")
