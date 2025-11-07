from __future__ import annotations

import argparse
from typing import Callable

from .verbose import build_verbose_hooks


def parse_common_args(
    description: str | None = None,
    configure: Callable[[argparse.ArgumentParser], None] | None = None,
) -> argparse.Namespace:
    """
    Parse shared CLI flags used by runnable scripts.
    Adds a ``--verbose`` flag that streams agent lifecycle events.
    """

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Stream agent lifecycle events (tools, handoffs, and LLM calls).",
    )
    if configure:
        configure(parser)
    return parser.parse_args()


__all__ = ["parse_common_args", "build_verbose_hooks"]
