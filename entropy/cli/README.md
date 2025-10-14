# ENTROPY Terminal Chat Interface

Terminal chat interface using Rich for beautiful formatting.

## Usage

```bash
./scripts/chat.sh
# or
python -m entropy.cli.chat
```

## Features

- **Conversation history**: Up/down arrows, saved to `~/.entropy_history`
- **Cost tracking**: Shows cost per query and session total
- **Session management**: Multiple sessions with `/clear` command
- **Rich UI**: Syntax highlighting, panels, animated loader

## Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands and examples |
| `/quit`, `/exit` | Exit the chat |
| `/clear` | Start new session (clear history) |
| `/cost` | Show total cost for session |
| `/session` | Show session ID, cost, worker count |

## Architecture

- Uses `Orchestrator` directly (no HTTP API needed)
- Same multi-agent system as API server
- Cheaper than API (no HTTP overhead, direct Python calls)

## Example Session

```
You: What is AAPL's current price?
                                                  
╭────────────────────────────────── ENTROPY ──────────────────────────────────╮
│ I'll get Apple's current price for you.                                     │
│                                                                             │
│ Apple (AAPL) is currently trading at $243.18.                               │
│                                                                             │
│ Additional context:                                                         │
│                                                                             │
│  • Market cap: $3.69 trillion                                               │
│  • P/E ratio: 37.08                                                         │
│  • 52-week range: $164.08 - $250.80                                         │
│  • The stock is trading near the higher end of its 52-week range            │
╰─────────────────────────────────────────────────────────────────────────────╯
Agent:       generalist
Query cost:  $0.0060   
Total cost:  $0.0060   
```

## Implementation Details

- Located in: `entropy/cli/chat.py`
- Entry point: `EntropyChat.run()` async method
- Launcher script: `scripts/chat.sh`
- History file: `~/.entropy_history` (readline format)

## Requirements

- Rich (for terminal UI)
- readline (for command history, standard library)
- All ENTROPY dependencies (Orchestrator, agents, tools)
