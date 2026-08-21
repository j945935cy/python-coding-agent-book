from __future__ import annotations

import asyncio

class AgentCancelled(asyncio.CancelledError):
    """Raised when a caller requests cooperative Agent cancellation."""

    def __init__(self, reason: str = "agent cancelled"):
        super().__init__(reason)
        self.reason = reason


class CancellationToken:
    def __init__(self) -> None:
        self._cancelled = False
        self.reason = "agent cancelled"

    def cancel(self, reason: str = "agent cancelled") -> None:
        self._cancelled = True
        self.reason = reason

    @property
    def is_cancelled(self) -> bool:
        return self._cancelled

    def raise_if_cancelled(self) -> None:
        if self._cancelled:
            raise AgentCancelled(self.reason)
