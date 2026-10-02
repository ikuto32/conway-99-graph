"""A fixed deadline for ONE command invocation, including its children/retries.

Independent commands get independent allowances. This module has no persistent
or cumulative task budget. It does not launch, stop, or supervise processes.
The caller must enforce the returned deadlines and observe/reap all children.
In particular, this is not an OS hard-real-time guarantee.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import math
from numbers import Real
from threading import RLock
import time
from typing import Callable

MAX_COMMAND_SECONDS = 21_600.0
MAX_REVIEW_SECONDS = 1_800.0


class DeadlineError(RuntimeError):
    pass


class DeadlineExceeded(DeadlineError):
    pass


class ReviewRequired(DeadlineError):
    pass


class ClockError(DeadlineError):
    pass


def _finite(value: Real, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite real number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{label} must be finite") from exc
    if not math.isfinite(result) or (result <= 0 if positive else result < 0):
        raise ValueError(f"{label} must be finite and {'positive' if positive else 'nonnegative'}")
    return result


def _reason(value: str, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


@dataclass(frozen=True, init=False)
class CommandDeadline:
    """Immutable invocation limit, with separately renewable review timing.

    Create this once before the command's preparation/work. Share this SAME
    instance/deadline with its child/retry orchestration. Do not construct a new
    instance for internal phases. A genuinely separate command constructs its
    own instance and receives its own requested allowance (at most six hours).

    Timely review() permits a long-running child to continue without restarting
    it. It never changes deadline_at. A review after its cadence has elapsed
    fails closed; the caller must stop that command rather than backdate review.
    """
    seconds: float
    allocation_reason: str
    review_interval_seconds: float
    started_at: float
    deadline_at: float
    _clock: Callable[[], float] = field(repr=False, compare=False)
    _lock: RLock = field(repr=False, compare=False)
    _observed: list[float] = field(repr=False, compare=False)
    _reviews: list[dict] = field(repr=False, compare=False)

    def __init__(self, seconds: Real, *, allocation_reason: str,
                 review_interval_seconds: Real = MAX_REVIEW_SECONDS,
                 clock: Callable[[], float] = time.monotonic):
        seconds = _finite(seconds, "seconds", positive=True)
        interval = _finite(review_interval_seconds, "review_interval_seconds", positive=True)
        if seconds > MAX_COMMAND_SECONDS:
            raise ValueError("one command may not exceed 21600 seconds")
        if interval > MAX_REVIEW_SECONDS:
            raise ValueError("review interval may not exceed 1800 seconds")
        reason = _reason(allocation_reason, "allocation_reason")
        if not callable(clock):
            raise ValueError("clock must be callable")
        start = _finite(clock(), "monotonic clock")
        if not math.isfinite(start + seconds) or start + seconds <= start:
            raise ValueError("clock precision cannot represent this deadline")
        for name, value in dict(seconds=seconds, allocation_reason=reason,
                review_interval_seconds=interval, started_at=start,
                deadline_at=start + seconds, _clock=clock, _lock=RLock(),
                _observed=[start], _reviews=[]).items():
            object.__setattr__(self, name, value)

    def _now(self) -> float:
        try:
            now = _finite(self._clock(), "monotonic clock")
        except ValueError as exc:
            raise ClockError(str(exc)) from exc
        if now < self._observed[0]:
            raise ClockError("monotonic clock moved backwards")
        self._observed[0] = now
        return now

    def _snapshot(self, now: float) -> dict:
        last_review = self._reviews[-1]["at"] if self._reviews else self.started_at
        review_deadline = last_review + self.review_interval_seconds
        remaining = max(0.0, self.deadline_at - now)
        due = now >= review_deadline
        return dict(elapsed_seconds=now - self.started_at,
                    remaining_seconds=remaining,
                    review_remaining_seconds=max(0.0, review_deadline - now),
                    review_due=due,
                    review_overdue_seconds=max(0.0, now - review_deadline),
                    deadline_reached=now >= self.deadline_at,
                    stop_required=now >= self.deadline_at or due,
                    deadline_at=self.deadline_at,
                    review_deadline_at=review_deadline,
                    completed_reviews=len(self._reviews))

    def status(self) -> dict:
        """Read elapsed/remaining wall time; idle time inside the command counts."""
        with self._lock:
            return self._snapshot(self._now())

    def child_seconds(self, requested_seconds: Real, *, reserve_seconds: Real = 0) -> float:
        """Check before launch and bound a child/retry by the SAME total deadline.

        Review time is deliberately not a fixed child timeout: the supervisor
        polls status() and can record timely reassessment while the child runs.
        reserve_seconds leaves time for the supervisor's shutdown/reaping.
        """
        requested = _finite(requested_seconds, "requested_seconds", positive=True)
        reserve = _finite(reserve_seconds, "reserve_seconds")
        with self._lock:
            snapshot = self._snapshot(self._now())
            remaining = snapshot["remaining_seconds"] - reserve
            if remaining <= 0:
                raise DeadlineExceeded("no invocation time remains after shutdown reserve")
            if snapshot["review_due"]:
                raise ReviewRequired("review is required before launching more work")
            return min(requested, remaining)

    def review(self, *, evidence: str) -> dict:
        """Record an actual timely reassessment; no estimated success probability.

        The caller supplies a concrete observation/decision or an evidence
        reference. This helper checks timing, not the truth of that evidence.
        Exact-boundary review is accepted; late review cannot renew the cadence.
        """
        evidence = _reason(evidence, "review evidence")
        with self._lock:
            now = self._now()
            before = self._snapshot(now)
            if before["deadline_reached"]:
                raise DeadlineExceeded("review cannot extend an expired invocation")
            if before["review_overdue_seconds"] > 0:
                raise ReviewRequired("review is overdue; deadline cannot be backdated")
            self._reviews.append(dict(at=now, evidence=evidence,
                                      elapsed_seconds=now - self.started_at))
            return self._snapshot(now)

    @property
    def reviews(self) -> tuple[dict, ...]:
        with self._lock:
            return tuple(dict(item) for item in self._reviews)
