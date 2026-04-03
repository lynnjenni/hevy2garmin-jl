"""Tests for SQLite tracking database."""

from __future__ import annotations

from pathlib import Path

from hevy2garmin.db import get_recent_synced, get_synced_count, is_synced, mark_synced


class TestSyncTracking:
    def test_not_synced_initially(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        assert is_synced("unknown-id", db_path=db_path) is False

    def test_mark_then_check(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        mark_synced("w1", garmin_activity_id="123", title="Push", db_path=db_path)
        assert is_synced("w1", db_path=db_path) is True

    def test_count(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        assert get_synced_count(db_path=db_path) == 0
        mark_synced("w1", title="Push", db_path=db_path)
        mark_synced("w2", title="Pull", db_path=db_path)
        assert get_synced_count(db_path=db_path) == 2

    def test_recent_ordering(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        mark_synced("w1", title="First", db_path=db_path)
        import time; time.sleep(1.1)  # ensure different timestamp
        mark_synced("w2", title="Second", db_path=db_path)
        recent = get_recent_synced(limit=2, db_path=db_path)
        assert len(recent) == 2
        assert recent[0]["title"] == "Second"  # most recent first

    def test_idempotent_mark(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        mark_synced("w1", garmin_activity_id="100", title="Push", db_path=db_path)
        mark_synced("w1", garmin_activity_id="200", title="Push Updated", db_path=db_path)
        assert get_synced_count(db_path=db_path) == 1
        recent = get_recent_synced(limit=1, db_path=db_path)
        assert recent[0]["garmin_activity_id"] == "200"

    def test_db_auto_creates(self, tmp_path: Path) -> None:
        db_path = tmp_path / "nested" / "dir" / "sync.db"
        mark_synced("w1", title="Test", db_path=db_path)
        assert db_path.exists()

    def test_stores_calories_and_hr(self, tmp_path: Path) -> None:
        db_path = tmp_path / "test.db"
        mark_synced("w1", title="Push", calories=250, avg_hr=95, db_path=db_path)
        recent = get_recent_synced(limit=1, db_path=db_path)
        assert recent[0]["calories"] == 250
        assert recent[0]["avg_hr"] == 95
