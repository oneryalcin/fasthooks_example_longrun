#!/bin/bash
# Start headless Chromium with remote debugging for chrome-devtools-mcp
chromium \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --disable-dev-shm-usage \
  --remote-debugging-port=9222 \
  --remote-debugging-address=0.0.0.0 \
  --user-data-dir=/tmp/chrome-profile \
  &

# Wait for Chrome to be ready
sleep 2

# Execute the main command
exec "$@"
