# Main entrypoint

import logging
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXTENSIONS = [
    "cogs.general",
    "cogs.qr_code",
              ]


class MagPy(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="!",
                         intents=discord.Intents.default())
        self.startup_errors: list[str] = []
        self.startup_errors_reported = False

    async def setup_hook(self) -> None:
        for extension in EXTENSIONS:
            try:
                await self.load_extension(extension)
            except Exception as error:
                self.startup_errors.append(
                    f"{extension}: {type(error).__name__}: {error}"
                )
                logger.exception("Failed to load extension %s", extension)

        if self.startup_errors:
            logger.error("Skipping command sync because an extension failed to load")
            return

        try:
            await self.tree.sync()
        except Exception as error:
            self.startup_errors.append(
                f"Application command sync: {type(error).__name__}: {error}"
            )
            logger.exception("Failed to sync application commands")

bot = MagPy()

@bot.event
async def on_ready() -> None:
    print(f"""
    Bot is online as {bot.user} ID: {bot.user.id}
    Currently registered in {len(bot.guilds)} guilds.
""")

    if not bot.startup_errors or bot.startup_errors_reported:
        return

    bot.startup_errors_reported = True
    channel_id = os.getenv("BOT_ERROR_CHANNEL_ID")
    try:
        parsed_channel_id = int(channel_id) if channel_id else None
    except ValueError:
        logger.error("BOT_ERROR_CHANNEL_ID must be a Discord channel ID")
        return

    if parsed_channel_id is None:
        logger.error(
            "Startup errors could not be reported: BOT_ERROR_CHANNEL_ID is unset"
        )
        return

    channel = bot.get_channel(parsed_channel_id)
    if channel is None:
        try:
            channel = await bot.fetch_channel(parsed_channel_id)
        except discord.HTTPException:
            logger.exception("Could not fetch startup error channel")
            return

    if not isinstance(channel, discord.abc.Messageable):
        logger.error("BOT_ERROR_CHANNEL_ID does not identify a messageable channel")
        return

    errors = "\n".join(
        f"- {discord.utils.escape_mentions(error)}" for error in bot.startup_errors
    )
    message = f"Bot startup encountered errors:\n{errors}"
    if len(message) > 1900:
        message = f"{message[:1897]}..."

    try:
        await channel.send(message)
    except discord.HTTPException:
        logger.exception("Could not send startup errors to the configured channel")


def main():
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")

    if not token:
        raise RuntimeError("DISCORD_TOKEN is not configured")

    bot.run(token)


if __name__ == "__main__":
    main()
