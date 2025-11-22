"""
Tests for fetch_status() function with mocked HTTP requests.
"""
import pytest
import aiohttp
from aioresponses import aioresponses
from status import (
    fetch_status,
    StatusResult,
    SERVICE_TYPE_STATUSPAGE_JSON,
    SERVICE_TYPE_GITHUB_JSON,
    SERVICE_TYPE_GCP_HTML,
    SERVICE_TYPE_MANUAL_CHECK,
    STATUS_OPERATIONAL,
    STATUS_ERROR,
    STATUS_MANUAL,
)


class TestFetchStatus:
    """Tests for fetch_status() function."""
    
    @pytest.mark.asyncio
    async def test_statuspage_json_success(self):
        """Test successful fetch for statuspage JSON service."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "status_url": "https://status.example.com/",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        
        with aioresponses() as m:
            m.get(
                "https://status.example.com/api/v2/status.json",
                payload={"status": {"indicator": "operational"}},
                status=200,
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        assert isinstance(result, StatusResult)
        assert result.service_name == "Test Service"
        assert result.indicator == "operational"
        assert result.display_status == "✅"
        assert result.status_url == "https://status.example.com/"
    
    @pytest.mark.asyncio
    async def test_github_json_success(self):
        """Test successful fetch for GitHub JSON service."""
        service = {
            "name": "GitHub Copilot",
            "url": "https://www.githubstatus.com/api/v2/summary.json",
            "status_url": "https://www.githubstatus.com/",
            "type": SERVICE_TYPE_GITHUB_JSON,
            "component_name": "Copilot",
        }
        
        with aioresponses() as m:
            m.get(
                "https://www.githubstatus.com/api/v2/summary.json",
                payload={
                    "components": [
                        {"name": "API", "status": "operational"},
                        {"name": "Copilot", "status": "operational"},
                    ]
                },
                status=200,
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        assert result.indicator == "operational"
        assert result.display_status == "✅"
    
    @pytest.mark.asyncio
    async def test_gcp_html_success(self):
        """Test successful fetch for GCP HTML service."""
        service = {
            "name": "Gemini Code Assist",
            "url": "https://status.cloud.google.com/",
            "status_url": "https://status.cloud.google.com/",
            "type": SERVICE_TYPE_GCP_HTML,
            "component_name": "Gemini Code Assist",
        }
        
        html_content = """
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
        
        with aioresponses() as m:
            m.get(
                "https://status.cloud.google.com/",
                body=html_content,
                status=200,
                content_type="text/html",
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        assert result.indicator == STATUS_OPERATIONAL
        assert result.display_status == "✅"
    
    @pytest.mark.asyncio
    async def test_manual_check(self):
        """Test manual check service type."""
        service = {
            "name": "Manual Service",
            "url": "https://status.example.com/",
            "type": SERVICE_TYPE_MANUAL_CHECK,
        }
        
        async with aiohttp.ClientSession() as session:
            result = await fetch_status(session, service)
        
        assert result.indicator == STATUS_MANUAL
        assert result.display_status == "🔍"
    
    @pytest.mark.asyncio
    async def test_http_error(self):
        """Test handling of HTTP error status."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "status_url": "https://status.example.com/",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        
        with aioresponses() as m:
            m.get(
                "https://status.example.com/api/v2/status.json",
                status=500,
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_connection_error(self):
        """Test handling of connection errors."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "status_url": "https://status.example.com/",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        
        with aioresponses() as m:
            # Simulate a connection error by raising ClientConnectorError
            # We'll use a simple OSError wrapped in ClientConnectorError
            import socket
            try:
                # Create a proper ClientConnectorError
                from aiohttp.connector import ConnectionKey
                from yarl import URL
                key = ConnectionKey(
                    host="status.example.com",
                    port=443,
                    is_ssl=True,
                    ssl=None,
                    proxy=None,
                    proxy_auth=None,
                    proxy_headers_hash=None,
                )
                os_error = socket.gaierror("Name or service not known")
                connector_error = aiohttp.ClientConnectorError(key, os_error)
            except Exception:
                # Fallback: use a generic exception
                connector_error = Exception("Connection error")
            
            m.get(
                "https://status.example.com/api/v2/status.json",
                exception=connector_error,
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_timeout_error(self):
        """Test handling of timeout errors."""
        import asyncio
        
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "status_url": "https://status.example.com/",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        
        with aioresponses() as m:
            m.get(
                "https://status.example.com/api/v2/status.json",
                exception=asyncio.TimeoutError(),
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_missing_url(self):
        """Test handling of missing URL."""
        service = {
            "name": "Test Service",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        
        async with aiohttp.ClientSession() as session:
            result = await fetch_status(session, service)
        
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_invalid_json(self):
        """Test handling of invalid JSON response."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "status_url": "https://status.example.com/",
            "type": SERVICE_TYPE_STATUSPAGE_JSON,
        }
        
        with aioresponses() as m:
            m.get(
                "https://status.example.com/api/v2/status.json",
                body="invalid json",
                status=200,
                content_type="application/json",
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        # Should handle the error gracefully
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"
    
    @pytest.mark.asyncio
    async def test_unknown_service_type(self):
        """Test handling of unknown service type."""
        service = {
            "name": "Test Service",
            "url": "https://status.example.com/api/v2/status.json",
            "status_url": "https://status.example.com/",
            "type": "unknown_type",
        }
        
        with aioresponses() as m:
            m.get(
                "https://status.example.com/api/v2/status.json",
                payload={"status": {"indicator": "operational"}},
                status=200,
            )
            
            async with aiohttp.ClientSession() as session:
                result = await fetch_status(session, service)
        
        assert result.indicator == STATUS_ERROR
        assert result.display_status == "❌"

