import io
import discord
from discord import app_commands
from discord.ext import commands
import qrcode
from qrcode.image.styledpil import StyledPilImage # Potentiality to add styles
from qrcode.image.styles.moduledrawers.pil import SquareModuleDrawer

class QRView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

class QRCode(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="create-qr-code", description="Make a qr code for the given url")
    @app_commands.describe(url="qr-code url")
    async def make_qr_code(self, interaction: discord.Interaction, url: str):
        # Possible TODO: Add checking for https or http and add if not present already
        embed = embed = discord.Embed(title=f"QR-Code for {url}",
                            description="Here you go!", color=discord.Color.green())

        qr = qrcode.QRCode(error_correction=qrcode.ERROR_CORRECT_H)
        qr.add_data(url)

        # Possible TODO: Add qr-code style selection
        img = qr.make_image(image_factory=StyledPilImage, module_drawer=SquareModuleDrawer())
        buffer = io.BytesIO()
        img.save(buffer)
        buffer.seek(0)

        attachment = discord.File(fp=buffer, filename="qr.png")
        embed.set_image(url="attachment://qr.png")

        await interaction.response.send_message(embed=embed, view=QRView(), file=attachment, ephemeral=True)
        buffer.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(QRCode(bot))
