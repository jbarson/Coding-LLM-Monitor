"""
Tests for JSON and HTML parsing functions.
These tests use mocked data and don't make real HTTP requests.
"""
import pytest
from status import (
    _parse_statuspage_json,
    _parse_github_json,
    _parse_gcp_html,
    StatusResult,
    STATUS_OPERATIONAL,
    STATUS_DEGRADED,
    STATUS_OUTAGE,
    STATUS_MAINTENANCE,
    STATUS_UNKNOWN,
    STATUS_ERROR,
)


class TestParseStatuspageJson:
    """Tests for _parse_statuspage_json() function."""
    
    @pytest.mark.asyncio
    async def test_operational_status(self):
        """Test parsing operational status."""
        data = {
            "status": {
                "indicator": "operational"
            }
        }
        result = await _parse_statuspage_json(data, "Test Service", "https://status.example.com/")
        
        assert isinstance(result, StatusResult)
        assert result.service_name == "Test Service"
        assert result.indicator == "operational"
        assert result.display_status == "✅"
        assert result.status_url == "https://status.example.com/"
    
    @pytest.mark.asyncio
    async def test_degraded_status(self):
        """Test parsing degraded status."""
        data = {
            "status": {
                "indicator": "degraded_performance"
            }
        }
        result = await _parse_statuspage_json(data, "Test Service", "https://status.example.com/")
        
        assert result.indicator == "degraded_performance"
        assert result.display_status == "⚠️"
    
    @pytest.mark.asyncio
    async def test_major_outage(self):
        """Test parsing major outage status."""
        data = {
            "status": {
                "indicator": "major_outage"
            }
        }
        result = await _parse_statuspage_json(data, "Test Service", "https://status.example.com/")
        
        assert result.indicator == "major_outage"
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_missing_status(self):
        """Test parsing when status is missing."""
        data = {}
        result = await _parse_statuspage_json(data, "Test Service", "https://status.example.com/")
        
        assert result.indicator == STATUS_UNKNOWN
        assert result.display_status == "❓"
    
    @pytest.mark.asyncio
    async def test_missing_indicator(self):
        """Test parsing when indicator is missing."""
        data = {
            "status": {}
        }
        result = await _parse_statuspage_json(data, "Test Service", "https://status.example.com/")
        
        assert result.indicator == STATUS_UNKNOWN


class TestParseGithubJson:
    """Tests for _parse_github_json() function."""
    
    @pytest.mark.asyncio
    async def test_find_component(self):
        """Test finding a component by name."""
        data = {
            "components": [
                {"name": "API", "status": "operational"},
                {"name": "Copilot", "status": "operational"},
                {"name": "Git Operations", "status": "degraded_performance"},
            ]
        }
        result = await _parse_github_json(data, "Copilot", "GitHub Copilot", "https://www.githubstatus.com/")
        
        assert result.service_name == "GitHub Copilot"
        assert result.indicator == "operational"
        assert result.display_status == "✅"
    
    @pytest.mark.asyncio
    async def test_component_not_found(self):
        """Test when component is not found."""
        data = {
            "components": [
                {"name": "API", "status": "operational"},
            ]
        }
        result = await _parse_github_json(data, "Copilot", "GitHub Copilot", "https://www.githubstatus.com/")
        
        assert result.indicator == STATUS_UNKNOWN
        assert result.display_status == "❓"
    
    @pytest.mark.asyncio
    async def test_case_insensitive_match(self):
        """Test that component matching is case-insensitive."""
        data = {
            "components": [
                {"name": "GitHub Copilot", "status": "operational"},
            ]
        }
        result = await _parse_github_json(data, "copilot", "GitHub Copilot", "https://www.githubstatus.com/")
        
        assert result.indicator == "operational"
    
    @pytest.mark.asyncio
    async def test_partial_match(self):
        """Test that partial component name matching works."""
        data = {
            "components": [
                {"name": "GitHub Copilot", "status": "operational"},
            ]
        }
        result = await _parse_github_json(data, "Copilot", "GitHub Copilot", "https://www.githubstatus.com/")
        
        assert result.indicator == "operational"
    
    @pytest.mark.asyncio
    async def test_missing_component_name(self):
        """Test when component_name is not provided."""
        data = {
            "components": []
        }
        result = await _parse_github_json(data, "", "GitHub Copilot", "https://www.githubstatus.com/")
        
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_degraded_component(self):
        """Test parsing degraded component status."""
        data = {
            "components": [
                {"name": "Copilot", "status": "degraded_performance"},
            ]
        }
        result = await _parse_github_json(data, "Copilot", "GitHub Copilot", "https://www.githubstatus.com/")
        
        assert result.indicator == "degraded_performance"
        assert result.display_status == "⚠️"


class TestParseGcpHtml:
    """Tests for _parse_gcp_html() function."""
    
    @pytest.mark.asyncio
    async def test_parse_available_status(self):
        """Test parsing available status from GCP HTML."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th class="j2GwVIZkdLB__product">Gemini Code Assist</th>
                        <td>
                            <svg class="psd__status-icon psd__available" aria-label="Available"></svg>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        result = await _parse_gcp_html(html, "Gemini Code Assist", "GCP Service", "https://status.cloud.google.com/")
        
        assert result.indicator == STATUS_OPERATIONAL
        assert result.display_status == "✅"
    
    @pytest.mark.asyncio
    async def test_parse_degraded_status(self):
        """Test parsing degraded status from GCP HTML."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th class="j2GwVIZkdLB__product">Gemini Code Assist</th>
                        <td>
                            <svg class="psd__status-icon psd__degraded" aria-label="Degraded"></svg>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        result = await _parse_gcp_html(html, "Gemini Code Assist", "GCP Service", "https://status.cloud.google.com/")
        
        assert result.indicator == STATUS_DEGRADED
        assert result.display_status == "⚠️"
    
    @pytest.mark.asyncio
    async def test_parse_outage_status(self):
        """Test parsing outage status from GCP HTML."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th class="j2GwVIZkdLB__product">Gemini Code Assist</th>
                        <td>
                            <svg class="psd__status-icon" aria-label="Service Disruption"></svg>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        result = await _parse_gcp_html(html, "Gemini Code Assist", "GCP Service", "https://status.cloud.google.com/")
        
        assert result.indicator == STATUS_OUTAGE
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_component_not_found(self):
        """Test when component is not found in HTML."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th class="j2GwVIZkdLB__product">Other Service</th>
                    </tr>
                </table>
            </body>
        </html>
        """
        result = await _parse_gcp_html(html, "Gemini Code Assist", "GCP Service", "https://status.cloud.google.com/")
        
        assert result.indicator == STATUS_UNKNOWN
        assert result.display_status == "❓"
    
    @pytest.mark.asyncio
    async def test_missing_component_name(self):
        """Test when component_name is not provided."""
        html = "<html><body></body></html>"
        result = await _parse_gcp_html(html, "", "GCP Service", "https://status.cloud.google.com/")
        
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_case_insensitive_match(self):
        """Test that component matching is case-insensitive."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th class="j2GwVIZkdLB__product">GEMINI CODE ASSIST</th>
                        <td>
                            <svg class="psd__status-icon psd__available"></svg>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """
        result = await _parse_gcp_html(html, "gemini code assist", "GCP Service", "https://status.cloud.google.com/")
        
        assert result.indicator == STATUS_OPERATIONAL
    
    @pytest.mark.asyncio
    async def test_no_status_icon(self):
        """Test when no status icon is found (assumes operational)."""
        html = """
        <html>
            <body>
                <table>
                    <tr>
                        <th class="j2GwVIZkdLB__product">Gemini Code Assist</th>
                        <td></td>
                    </tr>
                </table>
            </body>
        </html>
        """
        result = await _parse_gcp_html(html, "Gemini Code Assist", "GCP Service", "https://status.cloud.google.com/")
        
        # Should default to operational when no icon found
        assert result.indicator == STATUS_OPERATIONAL

