# How This App Was Built

This expense tracker was built autonomously by Claude Code using the [fasthooks LongRunningStrategy](https://github.com/oneryalcin/fasthooks).

## The Initial Prompt

The entire application was built from this single prompt:

```
Build a full-stack expense tracker with:
- Backend: FastAPI with SQLite, user auth (JWT), CRUD for expenses with categories
- Frontend: React with charts showing spending by category/month
- Features: CSV export, budget alerts, recurring expenses, receipt image upload
- Tests: pytest for backend, proper error handling, input validation
- Docker compose for deployment
```

That's it. No additional instructions, no manual coding. The LongRunningStrategy handled:
- Breaking down the work into 24 testable features
- Working on one feature at a time across multiple sessions
- Committing progress before context filled up
- Resuming work in fresh sessions with no memory loss

## Session Timeline

### Session 1: Initializer Agent
The first session detected no `feature_list.json` and became the **Initializer Agent**:

```
[18:18:10] SessionStart → custom: type=initializer
[18:18:10] → Injected INITIALIZER context
```

Claude created:
- `feature_list.json` with 24 features
- `init.sh` setup script
- Basic project structure
- Initial git commit

### Stop Blocked Until Progress Updated
When Claude tried to stop without updating progress:

```
[18:22:23] Stop → decision=block
  "Cannot stop - please address: Please update claude-progress.txt"
[18:22:37] Stop → decision=approve (after progress file updated)
```

### Context Compaction
When context filled up, PreCompact injected a checkpoint reminder:

```
[18:36:43] PreCompact → custom: checkpoint_needed
  "COMPACTION CHECKPOINT - commit work before context is compacted"
```

### Session 2+: Coding Agent
After compaction, new SessionStart detected `feature_list.json` and became **Coding Agent**:

```
[18:37:11] SessionStart → custom: type=coding
  "Features: 0/24 passing, Session #2"
```

Claude then:
1. Read progress file to understand what was done
2. Picked highest priority incomplete feature
3. Implemented and tested it
4. Marked `passes: true` in feature_list.json
5. Committed and updated progress

### Stop Blocked Again
Same pattern - blocked until progress updated:

```
[18:41:22] Stop → decision=block
[18:42:11] Stop → decision=approve
```

## Key Strategy Events

From `logs/strategy.log`:

| Time | Event | Result |
|------|-------|--------|
| 18:18:10 | SessionStart | `type=initializer` (first session) |
| 18:22:23 | Stop | `block` (progress not updated) |
| 18:22:37 | Stop | `approve` (after update) |
| 18:36:43 | PreCompact | checkpoint reminder injected |
| 18:37:11 | SessionStart | `type=coding` (after compact) |
| 18:41:22 | Stop | `block` (progress not updated) |
| 18:42:11 | Stop | `approve` (after update) |

## What the Hooks Enforced

1. **Initializer Context** (Session 1)
   - Create 24+ features in `feature_list.json`
   - Set up project structure
   - Initialize git repository

2. **Coding Context** (Sessions 2+)
   - Read progress file first
   - Work on ONE feature at a time
   - Test thoroughly before marking complete
   - Commit before stopping

3. **Stop Enforcement**
   - Must commit all changes
   - Must update progress file
   - Blocked until conditions met

4. **PreCompact Checkpoint**
   - Reminder to save work before compaction
   - Preserves state across context windows

## Final Result

After ~5 sessions:
- 24/24 features implemented and tested
- 84 backend tests passing
- Full React frontend with charts
- Docker Compose deployment ready

See `claude-progress.txt` for the full session-by-session development log.

## Reproduce This

1. Set up hooks per `.claude-setup/`
2. Give Claude the initial prompt
3. Let it run autonomously
4. Watch the `logs/strategy.log` for events

The strategy prevents:
- **One-shotting**: Can't try to do everything at once
- **Premature victory**: Can't declare done early
- **Memory loss**: Progress file preserves context across sessions
