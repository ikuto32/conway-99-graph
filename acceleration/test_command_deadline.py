"""Pure fake-clock controls: no processes, waits, research, or six-hour run."""
from dataclasses import FrozenInstanceError
import unittest

from acceleration.command_deadline import (
    ClockError, CommandDeadline, DeadlineExceeded, ReviewRequired,
)


class FakeClock:
    def __init__(self):
        self.value = 100.0

    def __call__(self):
        return self.value

    def advance(self, seconds):
        self.value += seconds


class CommandDeadlineTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()

    def make(self, seconds=21600, **kwargs):
        return CommandDeadline(seconds, allocation_reason="synthetic control",
                               clock=self.clock, **kwargs)

    def test_required_allocation_and_finite_cap(self):
        for value in [0, -1, 21600.001, float("inf"), float("nan"), True, "60", 10**1000]:
            with self.subTest(value=repr(value)[:40]), self.assertRaises(ValueError):
                self.make(value)
        with self.assertRaises(TypeError):
            CommandDeadline()
        with self.assertRaises(ValueError):
            CommandDeadline(60, allocation_reason=" ")
        self.assertEqual(self.make().seconds, 21600)

    def test_review_interval_validation(self):
        for value in [0, -1, 1801, float("inf"), float("nan"), False, "1800"]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.make(review_interval_seconds=value)

    def test_parallel_children_count_elapsed_not_sum(self):
        deadline = self.make(100, review_interval_seconds=50)
        self.assertEqual(deadline.child_seconds(90), 90)
        self.assertEqual(deadline.child_seconds(80), 80)
        self.clock.advance(10)
        self.assertEqual(deadline.status()["elapsed_seconds"], 10)
        self.assertEqual(deadline.status()["remaining_seconds"], 90)
        self.assertEqual(deadline.child_seconds(100), 90)

    def test_retry_and_internal_idle_share_same_deadline(self):
        deadline = self.make(100, review_interval_seconds=100)
        end = deadline.deadline_at
        self.clock.advance(70)
        self.assertEqual(deadline.child_seconds(100, reserve_seconds=5), 25)
        self.clock.advance(25)
        with self.assertRaises(DeadlineExceeded):
            deadline.child_seconds(10, reserve_seconds=5)
        self.clock.advance(5)
        self.assertTrue(deadline.status()["deadline_reached"])
        with self.assertRaises(DeadlineExceeded):
            deadline.child_seconds(1)
        self.assertEqual(deadline.deadline_at, end)

    def test_new_command_has_fresh_non_cumulative_allowance(self):
        first = self.make(100, review_interval_seconds=100)
        self.clock.advance(100)
        self.assertEqual(first.status()["remaining_seconds"], 0)
        second = self.make(21600)
        self.assertEqual(second.status()["remaining_seconds"], 21600)
        self.assertEqual(second.started_at, first.deadline_at)
        self.assertEqual(first.status()["remaining_seconds"], 0)

    def test_reviews_renew_only_review_not_command(self):
        deadline = self.make()
        end = deadline.deadline_at
        # No initial 1800-second cap on a useful long child.
        self.assertEqual(deadline.child_seconds(21600), 21600)
        for _ in range(11):
            self.clock.advance(1800)
            self.assertTrue(deadline.status()["review_due"])
            deadline.review(evidence="observed progress; continue within same deadline")
            self.assertFalse(deadline.status()["review_due"])
            self.assertEqual(deadline.deadline_at, end)
        self.clock.advance(1800)
        with self.assertRaises(DeadlineExceeded):
            deadline.review(evidence="must not grant a seventh hour")
        self.assertEqual(deadline.status()["remaining_seconds"], 0)

    def test_overdue_review_and_no_backdating(self):
        deadline = self.make(100, review_interval_seconds=10)
        self.clock.advance(11)
        with self.assertRaises(ReviewRequired):
            deadline.review(evidence="late observation")
        with self.assertRaises(ReviewRequired):
            deadline.child_seconds(10)
        self.assertEqual(deadline.reviews, ())
        self.assertTrue(deadline.status()["stop_required"])
        self.assertEqual(deadline.status()["remaining_seconds"], 89)

    def test_evidence_required_and_defensive_review_copy(self):
        deadline = self.make()
        with self.assertRaises(ValueError):
            deadline.review(evidence=" ")
        deadline.review(evidence="observed counters in receipt")
        copy = deadline.reviews[0]
        copy["at"] = 99999999
        self.assertEqual(deadline.reviews[0]["at"], 100)

    def test_deadline_cannot_be_reassigned(self):
        deadline = self.make()
        for name in ["seconds", "started_at", "deadline_at", "review_interval_seconds"]:
            with self.subTest(name=name), self.assertRaises(FrozenInstanceError):
                setattr(deadline, name, 999999)

    def test_clock_failure_is_rejected(self):
        deadline = self.make()
        self.clock.advance(10)
        deadline.status()
        self.clock.advance(-1)
        with self.assertRaises(ClockError):
            deadline.status()
        self.clock.value = float("nan")
        with self.assertRaises(ClockError):
            deadline.status()

    def test_interval_validation_and_expired_elapsed(self):
        deadline = self.make(10)
        for bad in [0, -1, float("inf"), float("nan"), True]:
            with self.subTest(request=bad), self.assertRaises(ValueError):
                deadline.child_seconds(bad)
        for bad in [-1, float("inf"), float("nan"), True]:
            with self.subTest(reserve=bad), self.assertRaises(ValueError):
                deadline.child_seconds(1, reserve_seconds=bad)
        self.clock.advance(12)
        self.assertEqual(deadline.status()["elapsed_seconds"], 12)
        self.assertEqual(deadline.status()["remaining_seconds"], 0)


if __name__ == "__main__":
    unittest.main()
