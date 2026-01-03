#!/usr/bin/env python3
"""
Test hooks using fasthooks LongRunningStrategy.

This tests the two-agent pattern:
- First session: Initializer creates feature_list.json, init.sh, git repo
- Subsequent sessions: Coding agent works on ONE feature at a time
"""
import os

from fasthooks import HookApp
from fasthooks.strategies import LongRunningStrategy

# Initialize app with logging to /opt/hooks/logs (outside workspace)
app = HookApp(
    log_dir="/opt/hooks/logs",
    state_dir="/opt/hooks/logs",
)

# Create LongRunningStrategy with test-friendly settings
strategy = LongRunningStrategy(
    feature_list="feature_list.json",
    progress_file="claude-progress.txt",
    init_script="init.sh",
    min_features=5,  # Low for testing
    enforce_commits=True,
    require_progress_update=True,
)


# Enable observability - log to file
STRATEGY_LOG = "/opt/hooks/logs/strategy.log"


@strategy.on_observe
def log_strategy_events(event):
    """Log all strategy events to file for visibility."""
    with open(STRATEGY_LOG, "a") as f:
        f.write(f"[{event.timestamp}] {event.event_type}: {event.hook_name}\n")
        if hasattr(event, "decision"):
            f.write(f"  decision={event.decision}\n")
        if hasattr(event, "message") and event.message:
            msg = event.message[:200] + "..." if len(event.message) > 200 else event.message
            f.write(f"  message={msg}\n")
        if hasattr(event, "payload") and event.payload:
            f.write(f"  payload={event.payload}\n")


# Include strategy's hooks
app.include(strategy.get_blueprint())

if __name__ == "__main__":
    app.run()
