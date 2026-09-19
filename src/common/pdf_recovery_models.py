"""Lightweight, serializable provenance models for PDF recovery.

These models deliberately contain plain Python values only.  They are a
sidecar to the existing PDF-to-Excel rows and are not an abstraction over
fitz, pdfplumber, or an OCR engine.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple


BBox = Tuple[float, float, float, float]


def _plain(value: Any) -> Any:
    """Return a JSON-friendly representation of a model or value."""
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


@dataclass
class RouteDecision:
    page_number: int
    selected_method: str = "unknown"
    reasons: List[str] = field(default_factory=list)
    candidate_count: int = 0
    used_ocr: bool = False
    used_layout_fallback: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))

@dataclass
class SourcePage:
    page_number: int
    width: float = 0.0
    height: float = 0.0
    has_text_layer: bool = False
    text_char_count: int = 0
    image_count: int = 0
    native_table_candidate_count: int = 0
    routing_decision: Optional[RouteDecision] = None

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class SourceDocument:
    source_path: str
    source_name: str = ""
    file_size: int = 0
    page_count: int = 0
    pages: List[SourcePage] = field(default_factory=list)
    file_fingerprint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class RecoveryCell:
    row_index: int
    column_index: int
    value: Any = None
    source_page: Optional[int] = None
    source_bbox: Optional[BBox] = None
    original_text: Optional[str] = None
    method: str = "unknown"
    ocr_confidence: Optional[float] = None
    issue_codes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class RecoveryBlock:
    block_id: str
    page_number: int
    region_bbox: Optional[BBox] = None
    block_type: str = "table"
    method: str = "unknown"
    rows: List[List[Any]] = field(default_factory=list)
    cells: List[RecoveryCell] = field(default_factory=list)
    structural_confidence: Optional[float] = None
    candidate_metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class RecoveryIssue:
    code: str
    severity: str = "warning"
    page_number: Optional[int] = None
    block_id: Optional[str] = None
    row_index: Optional[int] = None
    column_index: Optional[int] = None
    message: str = ""
    evidence: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))


@dataclass
class RecoveryResult:
    source_document: SourceDocument
    blocks: List[RecoveryBlock] = field(default_factory=list)
    issues: List[RecoveryIssue] = field(default_factory=list)
    structural_confidence: Optional[float] = None
    review_required: bool = False
    output_path: Optional[str] = None
    reliability_band: Optional[str] = None
    review_reason_codes: List[str] = field(default_factory=list)
    review_summaries: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return _plain(asdict(self))
