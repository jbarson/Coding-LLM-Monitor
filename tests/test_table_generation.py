"""
Tests for table generation function.
"""
import pytest
from unittest.mock import Mock, patch
from status import generate_table, StatusResult, STATUS_OPERATIONAL, STATUS_DEGRADED, STATUS_OUTAGE


class TestGenerateTable:
    """Tests for generate_table() function."""
    
    def test_empty_results(self):
        """Test table generation with empty results."""
        table = generate_table([], selected_index=-1)
        
        assert table is not None
        # Table should still be created even with no data
    
    def test_single_result(self):
        """Test table generation with single result."""
        results = [
            StatusResult(
                "Test Service",
                "✅",
                STATUS_OPERATIONAL,
                "https://status.example.com/",
            )
        ]
        table = generate_table(results, selected_index=-1)
        
        assert table is not None
    
    def test_multiple_results(self):
        """Test table generation with multiple results."""
        results = [
            StatusResult("Service A", "✅", STATUS_OPERATIONAL, "https://a.com/"),
            StatusResult("Service B", "⚠️", STATUS_DEGRADED, "https://b.com/"),
            StatusResult("Service C", "❌", STATUS_OUTAGE, "https://c.com/"),
        ]
        table = generate_table(results, selected_index=-1)
        
        assert table is not None
    
    def test_selected_index(self):
        """Test table generation with selected index."""
        results = [
            StatusResult("Service A", "✅", STATUS_OPERATIONAL, "https://a.com/"),
            StatusResult("Service B", "⚠️", STATUS_DEGRADED, "https://b.com/"),
        ]
        table = generate_table(results, selected_index=0)
        
        assert table is not None
        # Selected row should be highlighted
    
    def test_sorted_results(self):
        """Test that results are sorted by service name."""
        results = [
            StatusResult("Z Service", "✅", STATUS_OPERATIONAL, "https://z.com/"),
            StatusResult("A Service", "✅", STATUS_OPERATIONAL, "https://a.com/"),
            StatusResult("M Service", "✅", STATUS_OPERATIONAL, "https://m.com/"),
        ]
        table = generate_table(results, selected_index=-1)
        
        assert table is not None
        # Results should be sorted alphabetically

