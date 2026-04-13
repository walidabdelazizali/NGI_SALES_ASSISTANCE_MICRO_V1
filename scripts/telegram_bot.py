"""
Telegram bot adapter for the NGI Sales Assistance KB.

Sends user messages to scripts/ask_kb.py via subprocess and returns
the stdout as a Telegram reply. Long-polling only, no webhook.

Usage:
    export TELEGRAM_BOT_TOKEN="your_token"
    python scripts/telegram_bot.py
"""

import logging
import os
import subprocess
import sys
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

# ---------------------------------------------------------------------------
# Logging – technical output goes to console only
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _query_kb(question: str) -> str:
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
            return "Sorry, I couldn't process that question. Please try again."

        answer = result.stdout.strip()
        if not answer:
            return "No answer found for your question. Try rephrasing or ask /help."

        return answer

    except subprocess.TimeoutExpired:
        logger.error("ask_kb.py timed out after %ds", SUBPROCESS_TIMEOUT)
        return "The query took too long. Please try a simpler question."
    except Exception:
        logger.exception("Unexpected error calling ask_kb.py")
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
    "Type /help for examples."
)

HELP_TEXT = (
    "Examples you can ask:\n"
    "• What is the annual limit for Remedy 02?\n"
    "• Is Aster Hospital Qusais in the network?\n"
    "• Does Remedy 02 include maternity?\n"
    "• What is the copay for Remedy 03?\n\n"
    "Just type your question as a normal message."
)


async def cmd_start(update: Update, context) -> None:
    """Handle /start command."""
    await update.message.reply_text(START_TEXT)


async def cmd_help(update: Update, context) -> None:
    """Handle /help command."""
    await update.message.reply_text(HELP_TEXT)


async def handle_message(update: Update, context) -> None:
    """Handle any plain-text message by querying the KB."""
    user_text: Optional[str] = update.message.text

    if not user_text or not user_text.strip():
        await update.message.reply_text("Please send a question about insurance plans or networks.")
        return

    question = user_text.strip()
    logger.info("Question from %s: %s", update.effective_user.first_name, question)

    answer = _query_kb(question)

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Long-polling – blocks until interrupted
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
