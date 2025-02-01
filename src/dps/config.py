from dataclasses import dataclass


@dataclass
class DpsConfig:
    include: set[str]
    watch_path: str
    poll_rate: float
