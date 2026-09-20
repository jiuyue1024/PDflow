"""Small in-memory review session for one recovered table block.

This module intentionally has no PySide6 dependency.  It provides the safe
working-copy boundary used by the Slice 4A review dialog; export and the
original recovery sidecar remain untouched.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


Coordinate = Tuple[int, int]


@dataclass
class ReviewSession:
    block_id: str
    original_rows: List[List[Any]]
    source_pages: Dict[Coordinate, Optional[int]] = field(default_factory=dict)
    issue_markers: Dict[Coordinate, List[str]] = field(default_factory=dict)
    working_rows: List[List[Any]] = field(init=False)
    changed_cells: set[Coordinate] = field(default_factory=set, init=False)
    applied: bool = field(default=False, init=False)
    cancelled: bool = field(default=False, init=False)
    reviewed_data: Optional[Dict[str, Any]] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.original_rows = deepcopy(self.original_rows)
        self.working_rows = deepcopy(self.original_rows)
        self.source_pages = dict(self.source_pages)
        self.issue_markers = {
            coordinate: list(messages)
            for coordinate, messages in self.issue_markers.items()
        }

    @property
    def dirty(self) -> bool:
        return bool(self.changed_cells)

    @property
    def changed_cell_count(self) -> int:
        return len(self.changed_cells)

    @property
    def row_count(self) -> int:
        return len(self.original_rows)

    @property
    def column_count(self) -> int:
        return max((len(row) for row in self.original_rows), default=0)

    def value_at(self, row: int, column: int) -> Any:
        return self.working_rows[row][column]

    def set_value(self, row: int, column: int, value: Any) -> None:
        """Edit content only; table dimensions and provenance are immutable."""
        if row < 0 or row >= self.row_count:
            raise IndexError("row outside recovered table")
        if column < 0 or column >= len(self.original_rows[row]):
            raise IndexError("column outside recovered row")
        self.working_rows[row][column] = value
        coordinate = (row, column)
        if value == self.original_rows[row][column]:
            self.changed_cells.discard(coordinate)
        else:
            self.changed_cells.add(coordinate)
        self.cancelled = False

    def source_page_at(self, row: int, column: int) -> Optional[int]:
        return self.source_pages.get((row, column))

    def cancel(self) -> None:
        if self.applied and self.reviewed_data is not None:
            self.working_rows = deepcopy(self.reviewed_data["rows"])
        else:
            self.working_rows = deepcopy(self.original_rows)
        self.changed_cells = {
            (row, column)
            for row, values in enumerate(self.working_rows)
            for column, value in enumerate(values)
            if row < len(self.original_rows)
            and column < len(self.original_rows[row])
            and value != self.original_rows[row][column]
        }
        self.cancelled = True

    def apply(self) -> Dict[str, Any]:
        """Store a separate reviewed payload and leave source data untouched."""
        self.reviewed_data = {
            "block_id": self.block_id,
            "rows": deepcopy(self.working_rows),
            "changed_cells": sorted(self.changed_cells),
            "source_pages": {
                f"{row},{column}": page
                for (row, column), page in self.source_pages.items()
            },
            "issue_markers": {
                f"{row},{column}": list(messages)
                for (row, column), messages in self.issue_markers.items()
            },
            "reviewed": True,
            "edited": self.dirty,
        }
        self.applied = True
        self.cancelled = False
        return deepcopy(self.reviewed_data)


def _issue_message(issue: Dict[str, Any]) -> str:
    message = str(issue.get("message") or "").strip()
    return message or "A recovery issue was recorded for this table."


def _issue_applies(issue: Dict[str, Any], block_id: str, page_number: Any,
                   row: int, column: int) -> bool:
    issue_block = issue.get("block_id")
    if issue_block is not None and issue_block != block_id:
        return False
    issue_page = issue.get("page_number")
    if issue_page is not None and page_number is not None and issue_page != page_number:
        return False
    issue_row = issue.get("row_index")
    issue_column = issue.get("column_index")
    if issue_row is not None and issue_row != row:
        return False
    if issue_column is not None and issue_column != column:
        return False
    return any(value is not None for value in (issue_row, issue_column, issue_page, issue_block))


def create_review_session(recovery_result: Any, block_index: int = 0) -> Optional[ReviewSession]:
    """Create a session for one usable serialized recovery block, if present."""
    if not isinstance(recovery_result, dict):
        return None
    blocks = recovery_result.get("blocks")
    if not isinstance(blocks, list) or block_index < 0 or block_index >= len(blocks):
        return None
    block = blocks[block_index]
    if not isinstance(block, dict) or not isinstance(block.get("rows"), list) or not block["rows"]:
        return None
    rows = [row for row in block["rows"] if isinstance(row, list)]
    if not rows or not any(rows):
        return None
    block_id = str(block.get("block_id") or f"block-{block_index + 1}")
    page_number = block.get("page_number")
    source_pages: Dict[Coordinate, Optional[int]] = {}
    for cell in block.get("cells") or []:
        if not isinstance(cell, dict):
            continue
        row = cell.get("row_index")
        column = cell.get("column_index")
        if isinstance(row, int) and isinstance(column, int):
            source_pages[(row, column)] = cell.get("source_page")

    issue_markers: Dict[Coordinate, List[str]] = {}
    for issue in recovery_result.get("issues") or []:
        if not isinstance(issue, dict):
            continue
        for row in range(len(rows)):
            for column in range(len(rows[row])):
                if _issue_applies(issue, block_id, page_number, row, column):
                    issue_markers.setdefault((row, column), []).append(_issue_message(issue))

    return ReviewSession(
        block_id=block_id,
        original_rows=rows,
        source_pages=source_pages,
        issue_markers=issue_markers,
    )
