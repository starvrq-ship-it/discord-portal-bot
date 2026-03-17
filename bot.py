import discord
from discord.ext import commands
from discord import app_commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    try:
        with open("leaderboard.json", "r") as f:
            return json.load(f)
    except:
        return {}

review_counts = load_data()

def save_data():
    with open("leaderboard.json", "w") as f:
        json.dump(review_counts, f)

GUILD_ID = 1418404678777180303  # your server ID
REVIEW_CHANNEL_ID = 1430705928012824697  # review channel ID
TICKET_LOG_CHANNEL = 1480708106827726929

class CloseTicketView(discord.ui.View):
    @discord.ui.button(label="close Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔒 closing ticket in 5 seconds...")

        await interaction.channel.edit(
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
        )

        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        await interaction.channel.delete()

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
        text += f"{i}. <@{user_id}> — {count} masses\n"

    await interaction.response.send_message(text)

@bot.tree.command(name="sync", description="sync bot commands")
async def sync(interaction: discord.Interaction):

    guild = discord.Object(id=GUILD_ID)

    await bot.tree.sync(guild=guild)

    await interaction.response.send_message(
        "commands synced !",
        ephemeral=True

    )

@bot.command()
async def clearslash(ctx):
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    await ctx.send("cleared slash commands.")

@app_commands.checks.has_permissions(manage_guild=True)
@bot.tree.command(name="addpoints", description="add mass points to a user")
@app_commands.describe(user="user to give points to", points="number of masses to add")
async def addpoints(interaction: discord.Interaction, user: discord.Member, points: int):

    if points <= 0:
        await interaction.response.send_message("points must be a positive number.", ephemeral=True)
        return

    review_counts[str(user.id)] = review_counts.get(str(user.id), 0) + points
    save_data()

    message = f"""
_ _ 
_ _                               _ _     ᨻ  .     successful 
_ _                     added  **{points}**  masses   ~~      ~~   {user.mention}
_ _             ﹒    ׅthey now have **{review_counts[str(user.id)]}** masses.
"""

    await interaction.response.send_message(message)

STAFF_ROLE_ID = 1418404679364251687  # put your staff role id here


@bot.tree.command(name="music", description="open a mass ticket")
async def ticket(interaction: discord.Interaction):

    guild = interaction.guild
    user = interaction.user

    category = guild.get_channel(1427077235353063575)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }

    channel = await guild.create_text_channel(
        name=f"﹒w2p﹒{user.name}",
        category=category,
        overwrites=overwrites
    )

    await channel.send(user.mention, delete_after=5)

    await channel.send(
"""
_ _
_ _                               _ _        opened   __a__  ticket 
_ _                     run  ` .mass  `  to  start   ~~      ~~   massing
_ _                       ﹒    i hope you enjoy massing !*!*
_ _
""",)

class CloseTicketView(discord.ui.View):
    @discord.ui.button(label="close ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        user = interaction.user
        channel = interaction.channel
        guild = interaction.guild

        log_channel = guild.get_channel(TICKET_LOG_CHANNEL)

        if log_channel:
            await log_channel.send(
f"""
 　 　 　⇆ `　　　ticket closed

User: {user.mention}
Channel: {channel.name}
Closed By: {interaction.user.mention}
"""
            )

        await interaction.response.send_message("🔒 slosing ticket in 5 seconds...")

        await channel.edit(
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False)
            }
        )

        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        await channel.delete()

        await interaction.response.send_message(
        f"ticket created: {channel.mention}",
        ephemeral=True
    )

import os
bot.run(os.getenv("TOKEN"))