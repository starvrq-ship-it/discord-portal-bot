import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1418404678777180303  # your server ID
REVIEW_CHANNEL_ID = 1430705928012824697  # review channel ID


class ReviewModal(discord.ui.Modal, title="Mass Review"):

    server_link = discord.ui.TextInput(
        label="Server Link",
        placeholder="Paste the server invite link",
        required=True
    )

    invites = discord.ui.TextInput(
        label="Invites Gained",
        placeholder="Numbers only",
        required=True
    )

    portals = discord.ui.TextInput(
        label="Portals Posted",
        placeholder="Numbers only",
        required=True
    )

    sep = discord.ui.TextInput(
        label="Sep Posted (hours)",
        placeholder="Numbers only",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        if not self.invites.value.isdigit() or not self.portals.value.isdigit() or not self.sep.value.isdigit():
            await interaction.response.send_message(
                "Invites, portals, and sep must be numbers only.",
                ephemeral=True
            )
            return

        invites = int(self.invites.value)
        portals = int(self.portals.value)
        sep = int(self.sep.value)

        channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)

        message_text = f"""
_ _
 　 　𝄞 　 `🎧`　　　{interaction.user.mention} has [massed]({self.server_link.value})
-# _ _  　 　 {invites}i　 +  {portals}p  for  {sep}h  sep

  　 　 　ㅤ ׅ  ▶• ılıılıılılılıılıılı. 0 𝅄ㅤ
"""

        msg = await channel.send(message_text)

        await msg.create_thread(
            name=f"Review - {interaction.user.name}"
        )

        await interaction.response.send_message(
            "Review submitted!",
            ephemeral=True
        )


@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    bot.tree.clear_commands(guild=guild)  # removes old ones
    bot.tree.copy_global_to(guild=guild)

    await bot.tree.sync(guild=guild)

    print(f"Logged in as {bot.user}")


@bot.tree.command(name="review", description="Submit a mass review")
async def review(interaction: discord.Interaction):
    await interaction.response.send_modal(ReviewModal())

@bot.tree.command(name="sync", description="Sync bot commands")
async def sync(interaction: discord.Interaction):

    guild = discord.Object(id=GUILD_ID)

    await bot.tree.sync(guild=guild)

    await interaction.response.send_message(
        "Commands synced!",
        ephemeral=True
    )


bot.run(os.getenv("TOKEN"))