"""
Telegram bot adapter for the NGI Sales Assistance KB.

Sends user messages to scripts/ask_kb.py via subprocess and returns
the stdout as a Telegram reply. Long-polling only, no webhook.

Usage:
    export TELEGRAM_BOT_TOKEN="your_token"
    python scripts/telegram_bot.py
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# Absolute path to the ask_kb.py script (sibling file)
ASK_KB_SCRIPT: Path = Path(__file__).resolve().parent / "ask_kb.py"

# Maximum seconds to wait for ask_kb.py to respond
SUBPROCESS_TIMEOUT: int = 30

# Telegram message length limit (UTF-8 text)
TELEGRAM_MAX_LENGTH: int = 4096

# Query log file for unanswered / fallback / failed queries
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
QUERY_LOG_PATH: Path = PROJECT_ROOT / "logs" / "unanswered_queries.jsonl"

# ---------------------------------------------------------------------------
# Logging – technical output goes to console only
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Query logging – lightweight local file for owner review
# ---------------------------------------------------------------------------

def _log_query(question: str, answer: str, category: str, user_name: str = "") -> None:
    """Append a failed/fallback query to the JSONL log file."""
    QUERY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user": user_name,
        "question": question,
        "answer_snippet": answer[:200],
        "category": category,
    }
    with open(QUERY_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify_answer(answer: str) -> str:
    """Classify the answer to determine logging category."""
    if not answer or answer == "No answer found.":
        return "no_answer"
    return "ok"


def _query_kb(question: str, user_name: str = "") -> str:
    """
    Call ask_kb.py as a subprocess and return its stdout.
    All errors are logged to the console; the caller receives a safe
    user-facing string on failure.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(ASK_KB_SCRIPT), question],
            capture_output=True,
            text=True,
            timeout=SUBPROCESS_TIMEOUT,
            cwd=str(ASK_KB_SCRIPT.parent.parent),  # project root
        )

        if result.returncode != 0:
            logger.error(
                "ask_kb.py exited %d\nstderr: %s", result.returncode, result.stderr
            )
            _log_query(question, "(subprocess error)", "error", user_name)
            return "Sorry, I couldn't process that question. Please try again."

        answer = result.stdout.strip()
        if not answer or answer == "No answer found.":
            _log_query(question, answer or "(empty)", "no_answer", user_name)
            return (
                "I don't have a confirmed answer for this question.\n\n"
                "This may be because:\n"
                "• The plan you asked about is not yet in scope\n"
                "• The question type isn't supported yet\n\n"
                "Currently supported: Remedy 02, 03, 04, 05, 06 and Classic plans.\n"
                "Type /scope for the full list, or /examples for sample questions."
            )

        category = _classify_answer(answer)
        if category != "ok":
            _log_query(question, answer, category, user_name)

        return answer

    except subprocess.TimeoutExpired:
        logger.error("ask_kb.py timed out after %ds", SUBPROCESS_TIMEOUT)
        _log_query(question, "(timeout)", "error", user_name)
        return "The query took too long. Please try a simpler question."
    except Exception:
        logger.exception("Unexpected error calling ask_kb.py")
        _log_query(question, "(exception)", "error", user_name)
        return "Something went wrong. Please try again later."


def _split_message(text: str, max_len: int = TELEGRAM_MAX_LENGTH) -> list[str]:
    """Split text into chunks that fit within the Telegram message limit."""
    if len(text) <= max_len:
        return [text]

    chunks: list[str] = []
    while text:
        if len(text) <= max_len:
            chunks.append(text)
            break

        # Try to split on the last newline within the limit
        split_pos = text.rfind("\n", 0, max_len)
        if split_pos == -1:
            # No newline found – split on last space
            split_pos = text.rfind(" ", 0, max_len)
        if split_pos == -1:
            # No space either – hard split
            split_pos = max_len

        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip("\n")

    return chunks


# ---------------------------------------------------------------------------
# Telegram handlers
# ---------------------------------------------------------------------------

START_TEXT = (
    "Hello! I'm the NGI Sales Assistance bot.\n"
    "Send me a question about insurance plans, benefits, or provider networks "
    "and I'll look it up for you.\n\n"
    "Type /help for examples.\n"
    "Type /scope to see supported plans.\n"
    "Type /examples for sample questions."
)

HELP_TEXT = (
    "Examples you can ask:\n"
    "• What is the annual limit for Remedy 02?\n"
    "• Is Aster Hospital Qusais in the network?\n"
    "• Does Remedy 02 include maternity?\n"
    "• What is the copay for Remedy 03?\n\n"
    "Just type your question as a normal message.\n"
    "Type /scope to see which plans are currently supported."
)

SCOPE_TEXT = (
    "📋 Currently supported plans:\n\n"
    "Remedy plans:\n"
    "  • Remedy 02\n"
    "  • Remedy 03\n"
    "  • Remedy 04\n"
    "  • Remedy 05\n"
    "  • Remedy 06\n\n"
    "Classic plans:\n"
    "  • HN Classic 1R\n"
    "  • HN Classic 2\n"
    "  • HN Classic 2R\n"
    "  • HN Classic 3\n"
    "  • HN Classic 4\n\n"
    "Plans NOT yet supported:\n"
    "  • HN Classic 1 — no source workbook\n"
    "  • HN Prime 1, HN Prime 2 — no source data\n\n"
    "If you ask about an unsupported plan, the bot will tell you clearly."
)

EXAMPLES_TEXT = (
    "💡 Try these real questions:\n\n"
    "English:\n"
    "1. What is the annual limit for Remedy 02?\n"
    "2. Does Remedy 03 include maternity?\n"
    "3. Is telemedicine covered under Remedy 04?\n"
    "4. Does Remedy 02 cover dental?\n"
    "5. Is Aster Hospital Qusais in the Remedy 02 network?\n"
    "6. Does Remedy 02 offer direct billing?\n"
    "7. What is the copay for Remedy 05?\n"
    "8. Does Remedy 05 include maternity?\n"
    "9. What pharmacy coverage does Remedy 06 have?\n"
    "10. What is the annual limit for Remedy 06?\n\n"
    "Arabic:\n"
    "11. شو الحد السنوي لريمدي 02؟\n"
    "12. هل ريمدي 03 فيها تغطية حمل؟\n"
    "13. هل أستر القصيص ضمن شبكة ريمدي 02؟\n"
    "14. كم الكوباي لريمدي 06؟\n\n"
    "Mixed:\n"
    "15. هل dental مغطى في Remedy 02?\n"
    "16. Does Classic 2 cover maternity?\n"
    "17. What is the area of coverage for Classic 3?"
)


async def cmd_start(update: Update, context) -> None:
    """Handle /start command."""
    await update.message.reply_text(START_TEXT)


async def cmd_help(update: Update, context) -> None:
    """Handle /help command."""
    await update.message.reply_text(HELP_TEXT)


async def cmd_scope(update: Update, context) -> None:
    """Handle /scope command — show supported plans."""
    await update.message.reply_text(SCOPE_TEXT)


async def cmd_examples(update: Update, context) -> None:
    """Handle /examples command — show sample questions."""
    await update.message.reply_text(EXAMPLES_TEXT)


async def handle_message(update: Update, context) -> None:
    """Handle any plain-text message by querying the KB."""
    user_text: Optional[str] = update.message.text

    if not user_text or not user_text.strip():
        await update.message.reply_text("Please send a question about insurance plans or networks.")
        return

    question = user_text.strip()
    user_name = update.effective_user.first_name or ""
    logger.info("Question from %s: %s", user_name, question)

    answer = _query_kb(question, user_name)

    for chunk in _split_message(answer):
        await update.message.reply_text(chunk)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error(
            "TELEGRAM_BOT_TOKEN is not set. "
            "Export it as an environment variable before running."
        )
        sys.exit(1)

    logger.info("Starting Telegram bot (long-polling)…")
    logger.info("ask_kb.py path: %s", ASK_KB_SCRIPT)

    app = Application.builder().token(token).build()

    # Register handlers (order matters – commands first)
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("scope", cmd_scope))
    app.add_handler(CommandHandler("examples", cmd_examples))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Long-polling – blocks until interrupted
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
