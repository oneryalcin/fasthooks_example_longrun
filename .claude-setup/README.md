# Claude Code Setup for LongRunningStrategy

This folder contains the configuration files used to run Claude Code with the `LongRunningStrategy` from [fasthooks](https://github.com/oneryalcin/fasthooks).

## Files

| File | Description |
|------|-------------|
| `settings.json` | Claude Code settings with hooks configuration |
| `hooks.py` | The fasthooks handler using LongRunningStrategy |
| `Dockerfile.claude` | Docker image with Claude Code + headless Chromium |
| `docker-compose.claude.yml` | Docker Compose for running Claude Code |
| `entrypoint.sh` | Starts headless Chrome for browser testing |

## How It Works

The LongRunningStrategy implements Anthropic's [two-agent pattern](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):

1. **SessionStart Hook**: Injects context based on session type
   - First session → Initializer Agent (creates feature_list.json)
   - Subsequent sessions → Coding Agent (implements features)

2. **Stop Hook**: Blocks stopping until:
   - All changes are committed
   - Progress file is updated

3. **PostToolUse Hook**: Tracks file writes and git commits

## Quick Setup

```bash
# Install fasthooks
pip install fasthooks

# Or use Docker (recommended)
docker compose -f docker-compose.claude.yml up -d
docker compose -f docker-compose.claude.yml exec claude claude
```

## Configuration

### settings.json

```json
{
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "python hooks.py"}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "python hooks.py"}]}],
    "PostToolUse": [{"matcher": "Write|Edit|Bash", "hooks": [{"type": "command", "command": "python hooks.py"}]}]
  }
}
```

### hooks.py

```python
from fasthooks import HookApp
from fasthooks.strategies import LongRunningStrategy

app = HookApp()
strategy = LongRunningStrategy(min_features=24)
app.include(strategy.get_blueprint())

if __name__ == "__main__":
    app.run()
```

## Learn More

- [fasthooks documentation](https://github.com/oneryalcin/fasthooks)
- [LongRunningStrategy docs](https://github.com/oneryalcin/fasthooks/blob/main/docs/strategies/long-running.md)
- [Anthropic's article on long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
