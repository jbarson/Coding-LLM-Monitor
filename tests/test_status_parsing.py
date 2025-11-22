"""
Unit tests for status parsing functions.
These test pure functions that don't require external dependencies.
"""
import pytest
from status import (
    get_status_emoji,
    get_status_style,
    _is_operational_status,
    _is_degraded_status,
    _is_outage_status,
    STATUS_OPERATIONAL,
    STATUS_DEGRADED,
    STATUS_OUTAGE,
    STATUS_MAINTENANCE,
    STATUS_ERROR,
    STATUS_UNKNOWN,
    STATUS_MANUAL,
)


class TestStatusEmoji:
    """Tests for get_status_emoji() function."""
    
    def test_operational_statuses(self):
        """Test that operational statuses return ✅."""
        operational_statuses = [
            STATUS_OPERATIONAL,
            "none",
            "resolved",
            "up",
            "available",
            "OPERATIONAL",  # Case insensitive
            "None",
        ]
        for status in operational_statuses:
            assert get_status_emoji(status) == "✅"
    
    def test_degraded_statuses(self):
        """Test that degraded statuses return ⚠️."""
        degraded_statuses = [
            STATUS_DEGRADED,
            "partial_outage",
            "performance_issues",
            "warn",
            "degraded",
            "DEGRADED_PERFORMANCE",  # Case insensitive
        ]
        for status in degraded_statuses:
            assert get_status_emoji(status) == "⚠️"
    
    def test_outage_statuses(self):
        """Test that outage statuses return ❌."""
        outage_statuses = [
            STATUS_OUTAGE,
            "down",
            "error",
            "disruption",
            "MAJOR_OUTAGE",  # Case insensitive
        ]
        for status in outage_statuses:
            assert get_status_emoji(status) == "❌"
    
    def test_maintenance_status(self):
        """Test that maintenance status returns 🔧."""
        assert get_status_emoji(STATUS_MAINTENANCE) == "🔧"
        assert get_status_emoji("MAINTENANCE") == "🔧"
    
    def test_manual_status(self):
        """Test that manual status returns 🔍."""
        assert get_status_emoji(STATUS_MANUAL) == "🔍"
    
    def test_unknown_status(self):
        """Test that unknown status returns ❓."""
        assert get_status_emoji(STATUS_UNKNOWN) == "❓"
        assert get_status_emoji("random_status") == "❓"
        assert get_status_emoji("") == "❓"


class TestStatusStyle:
    """Tests for get_status_style() function."""
    
    def test_operational_style(self):
        """Test that operational statuses return green style."""
        assert get_status_style(STATUS_OPERATIONAL) == "bold green"
        assert get_status_style("operational") == "bold green"
        assert get_status_style("available") == "bold green"
    
    def test_degraded_style(self):
        """Test that degraded statuses return yellow style."""
        assert get_status_style(STATUS_DEGRADED) == "bold yellow"
        assert get_status_style("degraded_performance") == "bold yellow"
    
    def test_outage_style(self):
        """Test that outage statuses return red style."""
        assert get_status_style(STATUS_OUTAGE) == "bold red"
        assert get_status_style("error") == "bold red"
    
    def test_maintenance_style(self):
        """Test that maintenance status returns cyan style."""
        assert get_status_style(STATUS_MAINTENANCE) == "bold cyan"
    
    def test_manual_style(self):
        """Test that manual status returns blue style."""
        assert get_status_style(STATUS_MANUAL) == "bold blue"
    
    def test_unknown_style(self):
        """Test that unknown status returns grey style."""
        assert get_status_style(STATUS_UNKNOWN) == "bold grey50"
        assert get_status_style("random") == "bold grey50"


class TestStatusHelpers:
    """Tests for status helper functions."""
    
    def test_is_operational_status(self):
        """Test _is_operational_status() function."""
        assert _is_operational_status("operational") is True
        assert _is_operational_status("OPERATIONAL") is True
        assert _is_operational_status("available") is True
        assert _is_operational_status("error") is False
        assert _is_operational_status("degraded") is False
    
    def test_is_degraded_status(self):
        """Test _is_degraded_status() function."""
        assert _is_degraded_status("degraded_performance") is True
        assert _is_degraded_status("DEGRADED_PERFORMANCE") is True
        assert _is_degraded_status("partial_outage") is True
        assert _is_degraded_status("operational") is False
        assert _is_degraded_status("error") is False
    
    def test_is_outage_status(self):
        """Test _is_outage_status() function."""
        assert _is_outage_status("major_outage") is True
        assert _is_outage_status("MAJOR_OUTAGE") is True
        assert _is_outage_status("down") is True
        assert _is_outage_status("error") is True
        assert _is_outage_status("operational") is False
        assert _is_outage_status("degraded") is False

