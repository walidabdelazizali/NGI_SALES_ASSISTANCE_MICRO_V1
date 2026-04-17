# NGI Sales Assistance Telegram Bot — Operating SOP

## Quick Reference

| Action | Command |
|--------|---------|
| Start bot | `start_telegram_bot.bat` (double-click) |
| Stop bot | Close the terminal window, or `Ctrl+C` |
| Run validation | `python scripts/validation_pack_telegram.py` |
| Review failed queries | Open `logs/unanswered_queries.jsonl` |

---

## 1. Starting the Bot

```
cd C:\micro-insurance-kb-v1\NGI_SALES_ASSISTANCE_MICRO_V1
start_telegram_bot.bat
```

Or manually:
```
call NGI-ROBOT\.venv\Scripts\activate.bat
set TELEGRAM_BOT_TOKEN=<your-token>
python scripts/telegram_bot.py
```

The console should show:
```
Starting Telegram bot (long-polling)…
```

## 2. Stopping the Bot

- Press `Ctrl+C` in the terminal window, or
- Close the terminal window.

The bot will stop receiving messages immediately. No data is lost.

## 3. Verifying the Bot is Healthy

1. Open Telegram and message the bot.
2. Send `/start` — you should get the welcome message.
3. Send `/scope` — you should see the supported plan list.
4. Send a known question: `What is the annual limit for Remedy 02?`
5. You should get a `[PLAN]` prefixed answer with a real AED amount.

If any of these fail, check:
- The terminal window for error messages.
- That `TELEGRAM_BOT_TOKEN` is set correctly.
- That the virtual environment is activated.

## 4. Supported Plan Scope

### Approved for answer delivery:
- **Remedy 02**, **Remedy 03**, **Remedy 04**
- **HN Classic 1R**, **HN Classic 2**, **HN Classic 2R**, **HN Classic 3**, **HN Classic 4**

### NOT approved (bot will return safe fallback):
- Remedy 05, Remedy 06 — data loaded but blocked by deployment gate
- HN Classic 1 — no source workbook
- HN Prime 1, HN Prime 2 — no source data

### Bot commands:
| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Quick examples |
| `/scope` | Full list of supported and unsupported plans |
| `/examples` | 12 practical example questions (EN, AR, mixed) |

## 5. When Answers Look Wrong

1. **Note the exact question** the user asked.
2. **Test it manually**: `python scripts/ask_kb.py "the exact question"`
3. Check if the answer has the `[PLAN]`, `[NETWORK]`, `[RULE]`, or `[FAQ]` prefix — this tells you which data source responded.
4. If the answer is wrong:
   - Check the source data in `data/plans/`, `data/benefits/`, `data/networks/`, `data/rules/`, or `data/faq/`.
   - The issue is usually a missing or incorrect row in the CSV/JSON source files.
5. **Do NOT edit `ask_kb.py` routing logic** without testing via the validation pack.

## 6. Reviewing Failed Queries

Unanswered and error queries are logged to:
```
logs/unanswered_queries.jsonl
```

Each line is a JSON object:
```json
{"ts": "2026-04-16T10:30:00+00:00", "user": "Hassan", "question": "Does Remedy 07 cover dental?", "answer_snippet": "(empty)", "category": "no_answer"}
```

Categories:
- `no_answer` — bot returned "no answer found"
- `error` — subprocess error or timeout

To review top repeated failures:
```bash
python -c "
import json, collections
lines = open('logs/unanswered_queries.jsonl').readlines()
qs = [json.loads(l)['question'] for l in lines]
for q, c in collections.Counter(qs).most_common(10):
    print(f'{c:3d}x  {q}')
"
```

## 7. What is Intentionally NOT Supported Yet

- **Remedy 05 / 06 answers** — data exists but deployment gate blocks them.
- **Prime plan answers** — no source data ingested.
- **Classic 1 answers** — no TOB workbook available.
- **Multi-plan comparison** (e.g., "Compare Remedy 02 and 03").
- **Policy document lookup** (e.g., "Show me the TOB PDF").
- **Claims or member-specific queries** (e.g., "What's my claim status?").
- **Webhook / production hosting** — bot runs local long-polling only.

## 8. Running the Validation Pack

```bash
python scripts/validation_pack_telegram.py
```

This runs 30 real-world questions covering all supported topics and checks that:
- Supported plans return real answers.
- Unsupported plans return safe fallbacks.
- Arabic and mixed-language queries route correctly.

Review any `FAIL` lines and investigate before daily use.
