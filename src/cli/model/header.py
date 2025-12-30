from dataclasses import dataclass
from typing import Optional
import time
import json
from pathlib import Path


@dataclass
class TimerState:
    elapsed: float = 0.0
    last_start: float | None = None
    session_start: float | None = None

    def start(self):
        now = time.time()
        self.last_start = now
        self.session_start = now

    def stop(self):
        if self.last_start is not None:
            self.elapsed += time.time() - self.last_start
            self.last_start = None
    
    def eta(self, progress: float) -> Optional[float]:
        """
        Estimate remaining time in seconds.

        progress: float in [0.0, 1.0]
        Returns None if ETA is not meaningful yet.
        """
        if progress <= 0.0:
            return None
        if progress >= 1.0:
            return 0.0

        elapsed = self.total

        total_estimated = elapsed / progress
        remaining = total_estimated - elapsed

        return max(0.0, remaining)
    
    def avg_per_item(self, amount: int) -> Optional[float]:
        """
        Average time per item in seconds.

        Returns None if amount == 0.
        """
        if amount <= 0:
            return None
        return self.total / amount

    @property
    def total(self) -> float:
        if self.last_start is None:
            return self.elapsed
        return self.elapsed + (time.time() - self.last_start)
    
    @property
    def session(self) -> float:
        if self.session_start is None:
            return 0.0
        return time.time() - self.session_start


def load_timer(file: Path) -> TimerState:
    if file.exists():
        data = json.loads(file.read_text())
        return TimerState(**data)
    return TimerState()


def save_timer(file: Path, timer: TimerState):
    file.write_text(
        json.dumps(
            {
                "elapsed": timer.total,
                "last_start": None,
            }
        )
    )


def format_duration(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"



def eta_confident(progress: float, completed: int) -> bool:
    return progress >= 0.05 or completed >= 50


def format_eta(eta: Optional[float], confident: bool) -> str:
    if eta is None:
        return "ETA: --:--:--"
    if not confident:
        return "ETA: estimating..."
    return f"ETA: {format_duration(eta)}"


def format_avg_and_rate(seconds: Optional[float]) -> str:
    if seconds is None:
        return "avg: --"

    if seconds < 1:
        avg = f"{seconds * 1000:.0f} ms"
    elif seconds < 60:
        avg = f"{seconds:.1f} s"
    else:
        avg = format_duration(seconds)

    rate = int(3600 / seconds) if seconds > 0 else 0
    return f"avg: {avg} (≈{rate}/h)"


def format_remaining(remaining: int, progress: float) -> str:
    return f"{remaining} left ({progress:.3%})"


def format_decisions(decisions: int, skips: int) -> str:
    return f"decisions: {decisions} / skips: {skips}"


def build_header(
    *,
    total_items: int,
    completed: int,
    timer: TimerState,
    decisions: int,
    skips: int,
) -> str:
    remaining = total_items - completed
    progress = completed / total_items if total_items else 0.0

    eta = timer.eta(progress)
    confident = eta_confident(progress, completed)

    parts = [
        format_remaining(remaining, progress),
        format_eta(eta, confident),
        f"⏱ total {format_duration(timer.total)} (+{format_duration(timer.session)})",
        format_avg_and_rate(
            timer.total / completed if completed > 0 else None
        ),
        format_decisions(decisions, skips),
    ]

    return " • ".join(parts)