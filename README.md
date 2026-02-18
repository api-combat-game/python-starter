# ⚔️ API Combat — Python Starter Client

A minimal Python client that walks through the core API Combat game loop: register, login, browse units, build a team, queue a battle, and read the results.

## Requirements

- Python 3.8+
- `requests` library

## Setup

```bash
pip install requests
```

## Usage

```bash
# Register a new account and play through the full game loop
python client.py

# Or log in with an existing account
python client.py --email you@example.com --password YourPass1!
```

The script will:
1. Register a new account (or login if credentials provided)
2. Show your player profile
3. Browse available units in the shop
4. Show your starting roster
5. Create a battle team from your units
6. Queue for a battle
7. Poll for results and display the combat log

## Build Your Own

`client.py` is intentionally simple — one file, no classes, just functions and `requests`. Fork it and make it your own:

- Add strategy configuration to outsmart opponents
- Build a loop that grinds battles automatically
- Parse combat logs to optimize your team composition
- Add a CLI with `argparse` or `click`
- Wrap it in a Discord bot

## API Docs

- Full documentation: [apicombat.com/api-docs/v1](https://apicombat.com/api-docs/v1)
- OpenAPI spec: [apicombat.com/openapi/v1.json](https://apicombat.com/openapi/v1.json)

## Links

- 🌐 [apicombat.com](https://apicombat.com)
- 💬 [Discord](https://discord.gg/jfSCSfAN49)
- 📖 [API Docs](https://apicombat.com/api-docs/v1)

---

Part of the [API Combat](https://github.com/api-combat-game) project.
