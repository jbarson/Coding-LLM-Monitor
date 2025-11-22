import asyncio
import aiohttp
import time
import webbrowser
import sys
import select
import tty
import termios
from bs4 import BeautifulSoup
from rich.console import Console, Group
from rich.table import Table, Column
from rich.live import Live
from rich.text import Text
from rich.box import ROUNDED
from rich.align import Align

# --- Configuration ---
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
        "type": "github_json",
        "component_name": "Copilot"  # Name of the component on GitHub's status page
    },
    {
        "name": "Cursor",
        "url": "https://status.cursor.com/api/v2/status.json",
        "status_url": "https://status.cursor.com/",
        "type": "statuspage_json"
    },
    {
        "name": "Claude Code",
        "url": "https://status.claude.com/api/v2/status.json",
        "status_url": "https://status.claude.com/",
        "type": "statuspage_json"
    },
    {
        "name": "Gemini Code Assist (GCP)",
        "url": "https://status.cloud.google.com/",
        "status_url": "https://status.cloud.google.com/",
        "type": "gcp_html",
        "component_name": "Gemini Code Assist"  # Can also try "Vertex Gemini API" as fallback
    },
]

# How often to refresh the status, in seconds
REFRESH_INTERVAL = 600  # 10 minutes

# --- Status Parsing Logic ---

def get_status_emoji(indicator: str) -> str:
    """Returns an emoji based on the status indicator."""
    indicator = indicator.lower()
    if indicator in ("operational", "none", "resolved", "up", "available"):
        return "✅"
    elif indicator in ("degraded_performance", "partial_outage", "performance_issues", "warn", "degraded"):
        return "⚠️"
    elif indicator in ("major_outage", "partial_outage", "down", "error", "disruption"):
        return "❌"
    elif indicator == "maintenance":
        return "🔧"
    elif indicator == "manual":
        return "🔍"
    else:
        return "❓"  # For 'unknown'

async def fetch_status(session: aiohttp.ClientSession, service: dict) -> tuple[str, str, str, str]:
    """
    Fetches the status for a single service.
    Returns a tuple: (service_name, display_status, indicator, status_url)
    'indicator' is a standardized status string (e.g., 'operational', 'degraded_performance', 'error')
    'status_url' is the URL to the service's status page
    """
    service_name = service["name"]
    url = service["url"]
    status_url = service.get("status_url", url)  # Fallback to API URL if status_url not provided
    service_type = service["type"]

    try:
        if service_type == "manual_check":
            return (service_name, get_status_emoji("manual"), "manual", status_url)

        # Set a timeout for the request
        async with session.get(url, timeout=10) as response:
            if not response.status == 200:
                return (service_name, get_status_emoji("error"), "error", status_url)
            
            if service_type == "gcp_html":
                # GCP status page HTML parsing
                html_content = await response.text()
                soup = BeautifulSoup(html_content, 'html5lib')
                
                component_name = service.get("component_name", "")
                if not component_name:
                    return (service_name, get_status_emoji("error"), "error")
                
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
                                
                                # Map GCP status to standardized format
                                if 'available' in icon_classes.lower() or 'available' in aria_label.lower():
                                    return (service_name, get_status_emoji("operational"), "operational", status_url)
                                elif 'degraded' in icon_classes.lower() or 'degraded' in aria_label.lower():
                                    return (service_name, get_status_emoji("degraded_performance"), "degraded_performance", status_url)
                                elif 'outage' in icon_classes.lower() or 'outage' in aria_label.lower() or 'disruption' in aria_label.lower():
                                    return (service_name, get_status_emoji("major_outage"), "major_outage", status_url)
                                elif 'maintenance' in icon_classes.lower() or 'maintenance' in aria_label.lower():
                                    return (service_name, get_status_emoji("maintenance"), "maintenance", status_url)
                                else:
                                    # Try to extract from aria-label
                                    return (service_name, get_status_emoji("unknown"), "unknown", status_url)
                            
                            # If no status icon found, assume available (empty cell means available)
                            return (service_name, get_status_emoji("operational"), "operational", status_url)
                
                # Component not found
                return (service_name, get_status_emoji("unknown"), "unknown", status_url)
            
            # For JSON-based services, parse JSON
            data = await response.json()

            if service_type == "statuspage_json":
                # Standard Atlassian Statuspage format
                indicator = data.get("status", {}).get("indicator", "unknown")
                return (service_name, get_status_emoji(indicator), indicator, status_url)

            elif service_type == "github_json":
                # GitHub's specific status format
                component_name = service.get("component_name")
                if not component_name:
                    return (service_name, get_status_emoji("error"), "error", status_url)

                components = data.get("components", [])
                for component in components:
                    if component_name.lower() in component.get("name", "").lower():
                        status = component.get("status", "unknown")
                        # GitHub uses 'operational', 'degraded_performance', etc.
                        return (service_name, get_status_emoji(status), status, status_url)
                
                return (service_name, get_status_emoji("unknown"), "unknown", status_url)

            else:
                return (service_name, get_status_emoji("error"), "error", status_url)

    except aiohttp.ClientConnectorError:
        return (service_name, get_status_emoji("error"), "error", status_url)
    except asyncio.TimeoutError:
        return (service_name, get_status_emoji("error"), "error", status_url)
    except Exception as e:
        return (service_name, get_status_emoji("error"), "error", status_url)

def get_status_style(indicator: str) -> str:
    """Returns a Rich style string based on the status indicator."""
    indicator = indicator.lower()
    if indicator in ("operational", "none", "resolved", "up", "available"):
        return "bold green"
    elif indicator in ("degraded_performance", "partial_outage", "performance_issues", "warn", "degraded"):
        return "bold yellow"
    elif indicator in ("major_outage", "partial_outage", "down", "error", "disruption"):
        return "bold red"
    elif indicator == "maintenance":
        return "bold cyan"
    elif indicator == "manual":
        return "bold blue"
    else:
        return "bold grey50" # For 'unknown'

def generate_table(status_results: list[tuple[str, str, str, str]], selected_index: int = -1) -> Table:
    """Creates a Rich Table from the list of status results."""
    table = Table(
        Column("Service", style="cyan", no_wrap=True),
        Column("Status", style="white", no_wrap=True),
        title="Coding LLM Status Monitor",
        box=ROUNDED,
        expand=False,
        show_header=True,
        padding=(0, 1)
    )
    
    sorted_results = sorted(status_results)
    for idx, (name, description, indicator, status_url) in enumerate(sorted_results):
        style = get_status_style(indicator)
        # Highlight selected row
        if idx == selected_index:
            name_style = "bold cyan"
            status_text = Text(f"{description} ←", style=style)
        else:
            name_style = "cyan"
            status_text = Text(description, style=style)
        
        name_text = Text(name, style=name_style)
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
                            if select.select([sys.stdin], [], [], 0.1)[0]:
                                key = sys.stdin.read(1)
                                
                                sorted_results = sorted(status_results)
                                
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
                                        _, _, _, status_url = sorted_results[selected_index]
                                        webbrowser.open(status_url)
                                        console.print(f"\n[yellow]Opening {status_url}...[/yellow]")
                                elif key == 'q' or key == 'Q':
                                    raise KeyboardInterrupt
                        except (OSError, ValueError):
                            # Input error, continue without keyboard
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
                    sorted_results = sorted(status_results)
                    max_service_width = max(len(name) for name, _, _, _ in sorted_results) if sorted_results else 20
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
                    await asyncio.sleep(0.1)

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
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        pass