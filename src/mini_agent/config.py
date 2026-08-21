from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    max_turns: int = 8
    tool_timeout_seconds: float = 10.0
    tool_execution: str = "sequential"

    def __post_init__(self) -> None:
        if self.max_turns < 1:
            raise ValueError("max_turns must be at least 1")
        if self.tool_timeout_seconds <= 0:
            raise ValueError("tool_timeout_seconds must be positive")
        if self.tool_execution not in {"sequential", "parallel"}:
            raise ValueError("tool_execution must be sequential or parallel")
