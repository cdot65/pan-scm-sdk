"""Test module for monitoring OAuth token refresh and API call behaviors.

This module contains tests and utilities for validating token refresh logic and tracking API call status in the SDK.
"""
from datetime import datetime
import sys
import time
from typing import Optional


class TokenMonitor:
    """Monitor class to track API calls and token status."""

    def __init__(self, address_client):
        self.address_client = address_client
        self.start_time = time.time()
        self.iteration = 0

    def _get_elapsed_time(self) -> float:
        """Get elapsed time in seconds since monitor started."""
        return time.time() - self.start_time

    def _format_time(self, seconds: float) -> str:
        """Format elapsed time as MM:SS."""
        return f"{int(seconds // 60):02d}:{int(seconds % 60):02d}"

    def _make_api_call(self) -> Optional[list]:
        """Make API call and return results."""
        try:
            return self.address_client.list(folder="Texas")
        except Exception as e:
            print(f"\nError making API call: {str(e)}")
            return None

    def _print_status(
        self,
        elapsed: float,
        result_count: Optional[int],
        is_expired: bool,
        clear_screen: bool = True,
    ):
        """Print formatted status update."""
        if clear_screen:
            print("\033[2J\033[H", end="")  # Clear screen and move cursor to top

        print(f"Token Monitor Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
        print(f"Elapsed Time: {self._format_time(elapsed)}")
        print(f"Iteration: {self.iteration}")
        print("-" * 50)
        print(f"API Call Result Count: {result_count if result_count is not None else 'ERROR'}")
        print(f"Token Status: {'EXPIRED' if is_expired else 'VALID'}")
        print("=" * 50)
        sys.stdout.flush()

    def run(self, interval: int = 10, duration: Optional[int] = None):
        """Run the monitor.

        Args:
            interval: Time between checks in seconds
            duration: Optional total runtime in seconds

        """
        try:
            while True:
                self.iteration += 1
                elapsed = self._get_elapsed_time()

                # Check if we've exceeded the duration
                if duration and elapsed >= duration:
                    break

                # Make API call
                results = self._make_api_call()
                result_count = len(results) if results is not None else None

                # Check token status
                is_expired = self.address_client.api_client.oauth_client.is_expired

                # Print status
                self._print_status(elapsed, result_count, is_expired)

                # Wait for next interval
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            print("\nMonitoring complete")


if __name__ == "__main__":
    # Example usage (commented out as it needs the actual client)
    """
    from your_module import create_address_client

    # Create the address client
    address_client = create_address_client()

    # Create and run the monitor
    monitor = TokenMonitor(address_client)

    # Run for 1 hour (3600 seconds)
    monitor.run(interval=10, duration=3600)
    """
