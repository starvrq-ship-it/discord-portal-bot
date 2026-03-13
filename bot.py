import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# leaderboard storage
review_counts = {}

# put your log channel ID here
LOG_CHANNEL_ID = 1466266915671379988


class ReviewModal(discord.ui.Modal, title="Submit Mass Review"):

    invites = discord.ui.TextInput(
        label="Invites gained",
        placeholder="Numbers only",
        required=True
    )

    portals = discord.ui.TextInput(
        label="Portals posted",
        placeholder="Numbers only",
        required=True
    )

    sep = discord.ui.TextInput(
        label="Sep posted (hours)",
        placeholder="Numbers only",
        required=True
    )

    server_link = discord.ui.TextInput(
        label="Server link",
        placeholder="Paste the server invite link",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        # validate numbers
        if not self.invites.value.isdigit() or not self.portals.value.isdigit() or not self.sep.value.isdigit():
            await interaction.response.send_message(
                "Invites, portals, and sep must be numbers only.",
                ephemeral=True
            )
            return

        invites = self.invites.value
        portals = self.portals.value
        sep = self.sep.value
        server_link = self.server_link.value

        user = interaction.user.mention

        message = f"""
_ _
 　 　𝄞 　 `🎧`　　　{user} has [massed]({server_link})
-# _ _  　 　 {invites}i  +  {portals}p  for  {sep}h  sep

  　 　 　ㅤ ׅ  ▶• ılıılıılılılıılıılı. 0 𝅄ㅤ
"""

        await interaction.response.send_message(message)

        sent_message = await interaction.original_response()

        # create thread
        await sent_message.create_thread(
            name=f"{interaction.user.name}'s mass review"
        )

        # update leaderboard
        review_counts[interaction.user.id] = review_counts.get(interaction.user.id, 0) + 1

        # log to staff channel
        log_channel = bot.get_channel(LOG_CHANNEL_ID)

        if log_channel:
            await log_channel.send(
                f"{interaction.user} submitted a review\n"
                f"Invites: {invites}\n"
                f"Portals: {portals}\n"
                f"Sep: {sep}\n"
                f"Server: {server_link}"
            )


@bot.tree.command(name="review", description="Submit a mass review")
async def review(interaction: discord.Interaction):
    await interaction.response.send_modal(ReviewModal())


@bot.tree.command(name="leaderboard", description="Show top massers")
async def leaderboard(interaction: discord.Interaction):

    if not review_counts:
        await interaction.response.send_message("No reviews yet.", ephemeral=True)
        return

    sorted_users = sorted(review_counts.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 **Mass Leaderboard**\n\n"

    for i, (user_id, count) in enumerate(sorted_users[:10], start=1):
        user = await bot.fetch_user(user_id)
        text += f"{i}. {user.name} — {count} masses\n"

    await interaction.response.send_message(text)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


bot.run(os.getenv("TOKEN"))