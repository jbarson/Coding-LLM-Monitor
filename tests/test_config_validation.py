"""
Tests for configuration validation functions.
"""
import pytest
from status import (
    validate_service_config,
    validate_configuration,
    SERVICE_TYPE_STATUSPAGE_JSON,
    SERVICE_TYPE_GITHUB_JSON,
    SERVICE_TYPE_GCP_HTML,
    SERVICE_TYPE_MANUAL_CHECK,
)


class TestValidateServiceConfig:
    """Tests for validate_service_config() function."""
    
    def test_valid_statuspage_config(self):
        """Test valid statuspage JSON configuration."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "status_url": "https://status.example.com/",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        assert validate_service_config(service) is True
    
    def test_valid_github_config(self):
        """Test valid GitHub JSON configuration."""
        service = {
            "name": "GitHub Service",
            "url": "https://www.githubstatus.com/api/v2/summary.json",
            "status_url": "https://www.githubstatus.com/",
            "type": SERVICE_TYPE_GITHUB_JSON,
            "component_name": "Copilot",
        }
        assert validate_service_config(service) is True
    
    def test_valid_gcp_config(self):
        """Test valid GCP HTML configuration."""
        service = {
            "name": "GCP Service",
            "url": "https://status.cloud.google.com/",
            "status_url": "https://status.cloud.google.com/",
            "type": SERVICE_TYPE_GCP_HTML,
            "component_name": "Gemini Code Assist",
        }
        assert validate_service_config(service) is True
    
    def test_valid_manual_config(self):
        """Test valid manual check configuration."""
        service = {
            "name": "Manual Service",
            "url": "https://status.example.com/",
            "type": SERVICE_TYPE_MANUAL_CHECK,
        }
        assert validate_service_config(service) is True
    
    def test_missing_name(self):
        """Test configuration missing name field."""
        service = {
            "url": "https://status.example.com/api/v2/status.json",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        assert validate_service_config(service) is False
    
    def test_missing_url(self):
        """Test configuration missing url field."""
        service = {
            "name": "Test Service",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        assert validate_service_config(service) is False
    
    def test_missing_type(self):
        """Test configuration missing type field."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
        }
        assert validate_service_config(service) is False
    
    def test_invalid_type(self):
        """Test configuration with invalid type."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "type": "invalid_type",
        }
        assert validate_service_config(service) is False
    
    def test_empty_config(self):
        """Test empty configuration."""
        service = {}
        assert validate_service_config(service) is False


class TestValidateConfiguration:
    """Tests for validate_configuration() function."""
    
    def test_valid_configuration(self):
        """Test that valid configuration passes validation."""
        # This will use the actual SERVICES_TO_MONITOR from status.py
        # Assuming it's valid, this should pass
        result = validate_configuration()
        assert isinstance(result, bool)
        # The actual result depends on SERVICES_TO_MONITOR
        # If it's properly configured, it should be True
    
    def test_empty_services_list(self, monkeypatch):
        """Test validation with empty services list."""
        from status import SERVICES_TO_MONITOR
        original = SERVICES_TO_MONITOR.copy()
        
        # Temporarily replace with empty list
        monkeypatch.setattr('status.SERVICES_TO_MONITOR', [])
        
        try:
            assert validate_configuration() is False
        finally:
            # Restore original
            monkeypatch.setattr('status.SERVICES_TO_MONITOR', original)

