import json
import discord
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

try:
    with open("reviews.json", "r") as f:
        review_counts = json.load(f)
except:
    review_counts = {}

GUILD_ID = 1418404678777180303  # your server ID
REVIEW_CHANNEL_ID = 1430705928012824697  # review channel ID


class ReviewModal(discord.ui.Modal, title="Mass Review"):

    server_link = discord.ui.TextInput(
        label="Server Invite Link",
        placeholder="https://discord.gg/...",
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
        server_link = self.server_link.value

        user_id = str(interaction.user.id)

        review_counts[user_id] = review_counts.get(user_id, 0) + 1

        with open("reviews.json", "w") as f:
            json.dump(review_counts, f)

        channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)

        message_text = f"""
_ _
 　 　𝄞 　 `🎧`　　　{interaction.user.mention} has [massed]({self.server_link.value})
-# _ _  　 　 {invites}i　 +  {portals}p  for  {sep}h  sep

  　 　 　ㅤ ׅ  ▶• ılıılıılılılıılıılı. 0 𝅄ㅤ
"""

        msg = await channel.send(message_text)

        await msg.create_thread(
            name=f"review - {interaction.user.name}"
        )

        await interaction.response.send_message(
            "review submitted !",
            ephemeral=True
        )


@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)

    bot.tree.clear_commands(guild=guild)  # removes old ones
    bot.tree.copy_global_to(guild=guild)

    await bot.tree.sync(guild=guild)

    print(f"Logged in as {bot.user}")


@bot.tree.command(name="review", description="submit a mass review")
async def review(interaction: discord.Interaction):
    await interaction.response.send_modal(ReviewModal())

@bot.tree.command(name="leaderboard", description="show top massers")
async def leaderboard(interaction: discord.Interaction):

    if not review_counts:
        await interaction.response.send_message("no reviews yet.")
        return

    sorted_users = sorted(review_counts.items(), key=lambda x: x[1], reverse=True)

    text = f"""_ _
 　 　 　⇆ 　 🏆 `　　　mass leaderboard
-# _ _  　 　 　run　 /review  after  massing  to  log

"""

    for i, (user_id, count) in enumerate(sorted_users[:10], start=1):
        user = await bot.fetch_user(int(user_id))
        text += f"{i}. <@{user_id}> — {count} masses\n"

    await interaction.response.send_message(text)

@bot.tree.command(name="sync", description="Sync bot commands")
async def sync(interaction: discord.Interaction):

    guild = discord.Object(id=GUILD_ID)

    await bot.tree.sync(guild=guild)

    await interaction.response.send_message(
        "Commands synced!",
        ephemeral=True

    )

@bot.command()
async def clearslash(ctx):
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    await ctx.send("Cleared slash commands.")

import os
bot.run(os.getenv("TOKEN"))