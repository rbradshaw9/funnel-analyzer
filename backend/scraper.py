"""HTML scraping helpers for extracting funnel steps.

The parser intentionally uses only the Python standard library so that the
project remains lightweight. It looks for elements marked with the
``funnel-step`` class or ``data-funnel-step`` attribute and extracts the
headline and first paragraph as the description.
"""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from typing import List


@dataclass
class FunnelStep:
    """Simple data container describing a single funnel step."""

    title: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {"title": self.title, "description": self.description}


STEP_END_TAGS = {"section", "li", "div", "article"}
HEADLINE_TAGS = {"h1", "h2", "h3", "h4", "strong"}


class FunnelHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.steps: List[FunnelStep] = []
        self._current_title: list[str] | None = None
        self._current_description: list[str] | None = None
        self._explicit_title: str | None = None
        self._active = False
        self._depth = 0
        self._desc_depth = 0

    # Utilities -----------------------------------------------------
    def _start_step(self, attrs: dict[str, str]) -> None:
        self._active = True
        self._depth = 1
        self._explicit_title = attrs.get("data-funnel-step", "").strip() or None
        self._current_title = []
        self._current_description = []
        self._desc_depth = 0

    def _end_step(self, tag: str) -> None:
        if not self._active:
            return
        self._depth -= 1
        if self._depth > 0:
            return

        title_parts = self._current_title or []
        description_parts = self._current_description or []
        title = (self._explicit_title or " ".join(title_parts)).strip()
        description = " ".join(description_parts).strip()
        if title:
            self.steps.append(FunnelStep(title=title, description=description))
        self._active = False
        self._current_title = None
        self._current_description = None
        self._explicit_title = None
        self._desc_depth = 0

    # HTMLParser overrides ------------------------------------------
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {name: value or "" for name, value in attrs}

        if not self._active:
            classes = attrs_dict.get("class", "")
            class_tokens = {token.strip() for token in classes.split()} if classes else set()
            if attrs_dict.get("data-funnel-step") or "funnel-step" in class_tokens:
                self._start_step(attrs_dict)
            return

        # Already inside a step
        self._depth += 1
        if tag in HEADLINE_TAGS and self._current_title is not None:
            self._current_title.append("")  # marker to ensure spacing
        if tag == "p" and self._current_description is not None:
            self._desc_depth += 1
        elif self._current_description is not None and self._desc_depth:
            self._desc_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if not self._active:
            return

        if tag in HEADLINE_TAGS and self._current_title is not None:
            self._current_title.append("")
        if self._current_description is not None and self._desc_depth:
            self._desc_depth -= 1

        if tag in STEP_END_TAGS:
            self._end_step(tag)
        else:
            self._depth = max(self._depth - 1, 0)

    def handle_data(self, data: str) -> None:
        if not self._active:
            return

        text = data.strip()
        if not text:
            return

        if self._desc_depth and self._current_description is not None:
            self._current_description.append(text)
        elif self._current_title is not None:
            self._current_title.append(text)


def extract_funnel_steps(html: str) -> List[dict[str, str]]:
    parser = FunnelHTMLParser()
    parser.feed(html)
    return [step.to_dict() for step in parser.steps]


__all__ = ["FunnelStep", "extract_funnel_steps"]
