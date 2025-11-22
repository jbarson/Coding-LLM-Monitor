"""
Pytest configuration and shared fixtures.
"""
import pytest
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def sample_statuspage_json():
    """Sample statuspage JSON response."""
    return {
        "status": {
            "indicator": "operational",
            "description": "All systems operational"
        },
        "page": {
            "id": "test",
            "name": "Test Service",
            "url": "https://status.example.com"
        }
    }


@pytest.fixture
def sample_github_json():
    """Sample GitHub status JSON response."""
    return {
        "page": {
            "id": "kctbh9vrtdwd",
            "name": "GitHub",
            "url": "https://www.githubstatus.com",
            "updated_at": "2024-01-01T00:00:00.000Z"
        },
        "components": [
            {
                "id": "test1",
                "name": "API",
                "status": "operational",
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-01T00:00:00.000Z"
            },
            {
                "id": "test2",
                "name": "GitHub Copilot",
                "status": "operational",
                "created_at": "2024-01-01T00:00:00.000Z",
                "updated_at": "2024-01-01T00:00:00.000Z"
            }
        ]
    }


@pytest.fixture
def sample_gcp_html():
    """Sample GCP status page HTML."""
    return """
    <html>
        <head><title>Google Cloud Status</title></head>
        <body>
            <table>
                <tr>
                    <th class="j2GwVIZkdLB__product">Gemini Code Assist</th>
                    <td>
                        <svg class="psd__status-icon psd__available" aria-label="Available"></svg>
                    </td>
                </tr>
                <tr>
                    <th class="j2GwVIZkdLB__product">Compute Engine</th>
                    <td>
                        <svg class="psd__status-icon psd__degraded" aria-label="Degraded"></svg>
                    </td>
                </tr>
            </table>
        </body>
    </html>
    """


@pytest.fixture
def valid_service_config():
    """Valid service configuration for testing."""
    return {
        "name": "Test Service",
        "url": "https://status.example.com/api/v2/status.json",
        "status_url": "https://status.example.com/",
        "type": "statuspage_json"
    }

