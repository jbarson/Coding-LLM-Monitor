import asyncio
import aiohttp
import time
import webbrowser
import sys
import select
import tty
import termios
import logging
from typing import NamedTuple, Optional
from bs4 import BeautifulSoup
from rich.console import Console, Group
from rich.table import Table, Column
from rich.live import Live
from rich.text import Text
from rich.box import ROUNDED
from rich.align import Align

# --- Configuration ---
# Constants
REFRESH_INTERVAL = 600  # 10 minutes
REQUEST_TIMEOUT = 10  # seconds
KEYBOARD_POLL_INTERVAL = 0.1  # seconds
UI_REFRESH_INTERVAL = 0.1  # seconds

# Status indicators
STATUS_OPERATIONAL = "operational"
STATUS_DEGRADED = "degraded_performance"
STATUS_OUTAGE = "major_outage"
STATUS_MAINTENANCE = "maintenance"
STATUS_ERROR = "error"
STATUS_UNKNOWN = "unknown"
STATUS_MANUAL = "manual"

# Service types
SERVICE_TYPE_STATUSPAGE_JSON = "statuspage_json"
SERVICE_TYPE_GITHUB_JSON = "github_json"
SERVICE_TYPE_GCP_HTML = "gcp_html"
SERVICE_TYPE_MANUAL_CHECK = "manual_check"

# List of services to monitor.
# 'type' determines how to check the status.
#    - 'statuspage_json': Standard Atlassian Statuspage API
#    - 'github_json': GitHub's specific status API
#    - 'gcp_html': GCP status page HTML parsing
#    - 'manual_check': For services with complex dashboards (e.g., AWS)
SERVICES_TO_MONITOR = [
    {
        "name": "GitHub Copilot",
        "url": "https://www.githubstatus.com/api/v2/summary.json",
        "status_url": "https://www.githubstatus.com/",
        "type": SERVICE_TYPE_GITHUB_JSON,
        "component_name": "Copilot"  # Name of the component on GitHub's status page
    },
    {
        "name": "Cursor",
        "url": "https://status.cursor.com/api/v2/status.json",
        "status_url": "https://status.cursor.com/",
        "type": SERVICE_TYPE_STATUSPAGE_JSON
    },
    {
        "name": "Claude Code",
        "url": "https://status.claude.com/api/v2/status.json",
        "status_url": "https://status.claude.com/",
        "type": SERVICE_TYPE_STATUSPAGE_JSON
    },
    {
        "name": "Gemini Code Assist (GCP)",
        "url": "https://status.cloud.google.com/",
        "status_url": "https://status.cloud.google.com/",
        "type": SERVICE_TYPE_GCP_HTML,
        "component_name": "Gemini Code Assist"  # Can also try "Vertex Gemini API" as fallback
    },
]

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Only log warnings and errors by default
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_service_config(service: dict) -> bool:
    """
    Validate a service configuration dictionary.
    
    Args:
        service: Service configuration dictionary
        
    Returns:
        True if valid, False otherwise
    """
    required_fields = ["name", "url", "type"]
    for field in required_fields:
        if field not in service:
            logger.error(f"Service configuration missing required field: {field}")
            return False
    
    service_type = service.get("type")
    valid_types = [SERVICE_TYPE_STATUSPAGE_JSON, SERVICE_TYPE_GITHUB_JSON, 
                   SERVICE_TYPE_GCP_HTML, SERVICE_TYPE_MANUAL_CHECK]
    if service_type not in valid_types:
        logger.error(f"Invalid service type '{service_type}' for service '{service.get('name')}'")
        return False
    
    # Validate component_name for services that require it
    if service_type in [SERVICE_TYPE_GITHUB_JSON, SERVICE_TYPE_GCP_HTML]:
        if not service.get("component_name"):
            logger.warning(f"Service '{service.get('name')}' of type '{service_type}' should have 'component_name'")
    
    return True


def validate_configuration() -> bool:
    """
    Validate the SERVICES_TO_MONITOR configuration.
    
    Returns:
        True if all services are valid, False otherwise
    """
    if not SERVICES_TO_MONITOR:
        logger.error("SERVICES_TO_MONITOR is empty")
        return False
    
    all_valid = True
    for service in SERVICES_TO_MONITOR:
        if not validate_service_config(service):
            all_valid = False
    
    return all_valid

# --- Status Parsing Logic ---

class StatusResult(NamedTuple):
    """Represents the status result for a service."""
    service_name: str
    display_status: str  # Emoji representation
    indicator: str  # Standardized status string
    status_url: str


def _is_operational_status(indicator: str) -> bool:
    """Check if indicator represents an operational status."""
    return indicator.lower() in ("operational", "none", "resolved", "up", "available")


def _is_degraded_status(indicator: str) -> bool:
    """Check if indicator represents a degraded status."""
    return indicator.lower() in ("degraded_performance", "partial_outage", "performance_issues", "warn", "degraded")


def _is_outage_status(indicator: str) -> bool:
    """Check if indicator represents an outage status."""
    return indicator.lower() in ("major_outage", "partial_outage", "down", "error", "disruption")


def get_status_emoji(indicator: str) -> str:
    """
    Returns an emoji based on the status indicator.
    
    Args:
        indicator: Status indicator string (case-insensitive)
        
    Returns:
        Emoji string representing the status
    """
    indicator_lower = indicator.lower()
    if _is_operational_status(indicator):
        return "✅"
    elif _is_degraded_status(indicator):
        return "⚠️"
    elif _is_outage_status(indicator):
        return "❌"
    elif indicator_lower == "maintenance":
        return "🔧"
    elif indicator_lower == "manual":
        return "🔍"
    else:
        return "❓"  # For 'unknown'

async def _parse_gcp_html(html_content: str, component_name: str, service_name: str, status_url: str) -> StatusResult:
    """
    Parse GCP status page HTML to find component status.
    
    Args:
        html_content: HTML content from GCP status page
        component_name: Name of the component to find
        service_name: Name of the service
        status_url: URL to the status page
        
    Returns:
        StatusResult with parsed status information
    """
    try:
        soup = BeautifulSoup(html_content, 'html5lib')
        
        if not component_name:
            logger.warning(f"{service_name}: component_name not provided for GCP HTML parsing")
            return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)
        
        # Find the product row in the table
        # GCP uses <th class="j2GwVIZkdLB__product">Product Name</th>
        product_rows = soup.find_all('th', class_='j2GwVIZkdLB__product')
        
        for row in product_rows:
            product_text = row.get_text(strip=True)
            # Check if component name matches (case-insensitive, partial match)
            if component_name.lower() in product_text.lower():
                # Find the parent row
                parent_row = row.find_parent('tr')
                if parent_row:
                    # Look for status icon in the row
                    # GCP uses SVG with classes like psd__available, psd__degraded, etc.
                    status_icons = parent_row.find_all('svg', class_=lambda x: x and 'psd__status-icon' in x)
                    
                    if status_icons:
                        # Get the aria-label or class to determine status
                        status_icon = status_icons[0]  # Get first status icon (usually global status)
                        aria_label = status_icon.get('aria-label', '')
                        icon_classes = ' '.join(status_icon.get('class', []))
                        icon_classes_lower = icon_classes.lower()
                        aria_label_lower = aria_label.lower()
                        
                        # Map GCP status to standardized format
                        if 'available' in icon_classes_lower or 'available' in aria_label_lower:
                            return StatusResult(service_name, get_status_emoji(STATUS_OPERATIONAL), STATUS_OPERATIONAL, status_url)
                        elif 'degraded' in icon_classes_lower or 'degraded' in aria_label_lower:
                            return StatusResult(service_name, get_status_emoji(STATUS_DEGRADED), STATUS_DEGRADED, status_url)
                        elif 'outage' in icon_classes_lower or 'outage' in aria_label_lower or 'disruption' in aria_label_lower:
                            return StatusResult(service_name, get_status_emoji(STATUS_OUTAGE), STATUS_OUTAGE, status_url)
                        elif 'maintenance' in icon_classes_lower or 'maintenance' in aria_label_lower:
                            return StatusResult(service_name, get_status_emoji(STATUS_MAINTENANCE), STATUS_MAINTENANCE, status_url)
                        else:
                            logger.warning(f"{service_name}: Unknown GCP status from classes '{icon_classes}' and aria-label '{aria_label}'")
                            return StatusResult(service_name, get_status_emoji(STATUS_UNKNOWN), STATUS_UNKNOWN, status_url)
                    
                    # If no status icon found, assume available (empty cell means available)
                    return StatusResult(service_name, get_status_emoji(STATUS_OPERATIONAL), STATUS_OPERATIONAL, status_url)
        
        # Component not found
        logger.warning(f"{service_name}: Component '{component_name}' not found on GCP status page")
        return StatusResult(service_name, get_status_emoji(STATUS_UNKNOWN), STATUS_UNKNOWN, status_url)
    except Exception as e:
        logger.error(f"{service_name}: Error parsing GCP HTML: {e}", exc_info=True)
        return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)


async def _parse_statuspage_json(data: dict, service_name: str, status_url: str) -> StatusResult:
    """
    Parse standard Atlassian Statuspage JSON format.
    
    Args:
        data: JSON data from status page API
        service_name: Name of the service
        status_url: URL to the status page
        
    Returns:
        StatusResult with parsed status information
    """
    indicator = data.get("status", {}).get("indicator", STATUS_UNKNOWN)
    return StatusResult(service_name, get_status_emoji(indicator), indicator, status_url)


async def _parse_github_json(data: dict, component_name: str, service_name: str, status_url: str) -> StatusResult:
    """
    Parse GitHub's specific status JSON format.
    
    Args:
        data: JSON data from GitHub status API
        component_name: Name of the component to find
        service_name: Name of the service
        status_url: URL to the status page
        
    Returns:
        StatusResult with parsed status information
    """
    if not component_name:
        logger.warning(f"{service_name}: component_name not provided for GitHub JSON parsing")
        return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)

    components = data.get("components", [])
    for component in components:
        if component_name.lower() in component.get("name", "").lower():
            status = component.get("status", STATUS_UNKNOWN)
            # GitHub uses 'operational', 'degraded_performance', etc.
            return StatusResult(service_name, get_status_emoji(status), status, status_url)
    
    logger.warning(f"{service_name}: Component '{component_name}' not found in GitHub status")
    return StatusResult(service_name, get_status_emoji(STATUS_UNKNOWN), STATUS_UNKNOWN, status_url)


async def fetch_status(session: aiohttp.ClientSession, service: dict) -> StatusResult:
    """
    Fetches the status for a single service.
    
    Args:
        session: aiohttp client session for making requests
        service: Service configuration dictionary
        
    Returns:
        StatusResult containing service name, display status, indicator, and status URL
    """
    service_name = service.get("name", "Unknown Service")
    url = service.get("url", "")
    status_url = service.get("status_url", url)  # Fallback to API URL if status_url not provided
    service_type = service.get("type", "")

    if not url:
        logger.error(f"{service_name}: No URL provided")
        return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)

    try:
        if service_type == SERVICE_TYPE_MANUAL_CHECK:
            return StatusResult(service_name, get_status_emoji(STATUS_MANUAL), STATUS_MANUAL, status_url)

        # Set a timeout for the request
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
            if response.status != 200:
                logger.warning(f"{service_name}: HTTP {response.status} response")
                return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)
            
            if service_type == SERVICE_TYPE_GCP_HTML:
                html_content = await response.text()
                return await _parse_gcp_html(html_content, service.get("component_name", ""), service_name, status_url)
            
            # For JSON-based services, parse JSON
            data = await response.json()

            if service_type == SERVICE_TYPE_STATUSPAGE_JSON:
                return await _parse_statuspage_json(data, service_name, status_url)
            elif service_type == SERVICE_TYPE_GITHUB_JSON:
                return await _parse_github_json(data, service.get("component_name", ""), service_name, status_url)
            else:
                logger.error(f"{service_name}: Unknown service type '{service_type}'")
                return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)

    except aiohttp.ClientConnectorError as e:
        logger.error(f"{service_name}: Connection error - {e}")
        return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)
    except asyncio.TimeoutError:
        logger.error(f"{service_name}: Request timeout after {REQUEST_TIMEOUT}s")
        return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)
    except Exception as e:
        logger.error(f"{service_name}: Unexpected error - {e}", exc_info=True)
        return StatusResult(service_name, get_status_emoji(STATUS_ERROR), STATUS_ERROR, status_url)

def get_status_style(indicator: str) -> str:
    """
    Returns a Rich style string based on the status indicator.
    
    Args:
        indicator: Status indicator string (case-insensitive)
        
    Returns:
        Rich style string for terminal formatting
    """
    indicator_lower = indicator.lower()
    if _is_operational_status(indicator):
        return "bold green"
    elif _is_degraded_status(indicator):
        return "bold yellow"
    elif _is_outage_status(indicator):
        return "bold red"
    elif indicator_lower == "maintenance":
        return "bold cyan"
    elif indicator_lower == "manual":
        return "bold blue"
    else:
        return "bold grey50"  # For 'unknown'

def generate_table(status_results: list[StatusResult], selected_index: int = -1) -> Table:
    """
    Creates a Rich Table from the list of status results.
    
    Args:
        status_results: List of StatusResult objects
        selected_index: Index of the currently selected row (-1 for none)
        
    Returns:
        Rich Table object ready for display
    """
    table = Table(
        Column("Service", style="cyan", no_wrap=True),
        Column("Status", style="white", no_wrap=True),
        title="Coding LLM Status Monitor",
        box=ROUNDED,
        expand=False,
        show_header=True,
        padding=(0, 1)
    )
    
    sorted_results = sorted(status_results, key=lambda x: x.service_name)
    for idx, result in enumerate(sorted_results):
        style = get_status_style(result.indicator)
        # Highlight selected row
        if idx == selected_index:
            name_style = "bold cyan"
            status_text = Text(f"{result.display_status} ←", style=style)
        else:
            name_style = "cyan"
            status_text = Text(result.display_status, style=style)
        
        name_text = Text(result.service_name, style=name_style)
        table.add_row(name_text, status_text)

    return table

async def main_loop():
    """Main application loop to fetch and display statuses."""
    console = Console()
    selected_index = 0
    last_refresh = time.time()
    keyboard_enabled = False
    old_settings = None
    
    # Setup keyboard input (Unix/macOS only)
    if sys.stdin.isatty():
        try:
            old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())
            keyboard_enabled = True
        except (termios.error, AttributeError, OSError):
            # Windows or other systems without termios
            keyboard_enabled = False
    
    try:
      async with aiohttp.ClientSession(headers={"User-Agent": "Coding-LLM-Monitor/1.0"}) as session:
        # Initial fetch
        tasks = [fetch_status(session, service) for service in SERVICES_TO_MONITOR]
        status_results = await asyncio.gather(*tasks)
        
        with Live(console=console, screen=False, auto_refresh=False) as live:
                while True:
                    # Check for keyboard input (non-blocking, Unix/macOS only)
                    if keyboard_enabled:
                        try:
                            if select.select([sys.stdin], [], [], KEYBOARD_POLL_INTERVAL)[0]:
                                key = sys.stdin.read(1)
                                
                                sorted_results = sorted(status_results, key=lambda x: x.service_name)
                                
                                if key == '\x1b':  # ESC sequence
                                    next_key = sys.stdin.read(1)
                                    if next_key == '[':
                                        arrow = sys.stdin.read(1)
                                        if arrow == 'A':  # Up arrow
                                            selected_index = (selected_index - 1) % len(sorted_results)
                                        elif arrow == 'B':  # Down arrow
                                            selected_index = (selected_index + 1) % len(sorted_results)
                                elif key == '\n' or key == '\r':  # Enter
                                    # Open selected service's status page
                                    if 0 <= selected_index < len(sorted_results):
                                        status_url = sorted_results[selected_index].status_url
                                        webbrowser.open(status_url)
                                        console.print(f"\n[yellow]Opening {status_url}...[/yellow]")
                                elif key == 'q' or key == 'Q':
                                    raise KeyboardInterrupt
                        except (OSError, ValueError) as e:
                            # Input error, continue without keyboard
                            logger.debug(f"Keyboard input error: {e}")
                            pass
                    
                    # Check if it's time to refresh
                    current_time = time.time()
                    if current_time - last_refresh >= REFRESH_INTERVAL:
                        # Create all fetch tasks
                        tasks = [fetch_status(session, service) for service in SERVICES_TO_MONITOR]
                        
                        # Run tasks concurrently
                        status_results = await asyncio.gather(*tasks)
                        last_refresh = current_time
                    
                    # Display current state
                    table = generate_table(status_results, selected_index)
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Calculate table width based on content
                    sorted_results = sorted(status_results, key=lambda x: x.service_name)
                    max_service_width = max(len(result.service_name) for result in sorted_results) if sorted_results else 20
                    # Estimate: service width + status column (~6) + borders/padding (~6)
                    table_width = max(max_service_width + 12, 50)
                    
                    # Create multi-line footer text
                    if keyboard_enabled:
                        footer_lines = [
                            f"Last updated: {timestamp}",
                            f"Controls: ↑/↓ select | Enter open | Q quit | Refresh: {REFRESH_INTERVAL}s"
                        ]
                    else:
                        footer_lines = [
                            f"Last updated: {timestamp}",
                            f"Refresh: {REFRESH_INTERVAL}s | Press Ctrl+C to exit"
                        ]
                    
                    # Create footer with multiple lines, each aligned to table width
                    footer_texts = [Align.left(Text(line, style="dim"), width=table_width) for line in footer_lines]
                    footer = Group(*footer_texts)
                    
                    # Combine table and footer into a single renderable
                    renderable = Group(table, footer)
                    live.update(renderable)
                    live.refresh()
                    
                    # Small sleep to prevent CPU spinning
                    await asyncio.sleep(UI_REFRESH_INTERVAL)

    except asyncio.CancelledError:
        console.print("Shutting down...", style="yellow")
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting dashboard...[/yellow]")
    finally:
        # Restore terminal settings
        if old_settings is not None:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except (termios.error, AttributeError, OSError):
                pass

if __name__ == "__main__":
    # Validate configuration before starting
    if not validate_configuration():
        logger.error("Configuration validation failed. Please check your service configurations.")
        sys.exit(1)
    
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass