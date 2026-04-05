import discord
from discord.ext import commands
from discord import app_commands
import json
import os

ticket_channels = {}

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

from discord import app_commands
import discord

class ReviewModal(discord.ui.Modal, title="Test Modal"):
    test_input = discord.ui.TextInput(label="Test", placeholder="type here")
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"You typed: {self.test_input.value}", ephemeral=True)

@bot.tree.command(name="review", description="submit a test review")
async def review(interaction: discord.Interaction):
    await interaction.response.send_modal(ReviewModal())

class MassInfoModal(discord.ui.Modal, title="mass info"):

    server_ad = discord.ui.TextInput(
        label="Server Ad",
        style=discord.TextStyle.paragraph,
        required=True
    )

    server_link = discord.ui.TextInput(
        label="Server Link",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        channel = interaction.channel

        ad_msg = await channel.send(f"\n{self.server_ad.value}")
        link_msg = await channel.send(f"*\n{self.server_link.value}")

        await ad_msg.pin()
        await link_msg.pin()

        await channel.send(
            "run `.access` to continue",
            view=EditView(self.server_ad.value, self.server_link.value)
        )

        await interaction.response.send_message("submitted !", ephemeral=True)

class EditView(discord.ui.View):
    def __init__(self, ad, link):
        super().__init__()
        self.ad = ad
        self.link = link

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.blurple)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MassInfoModal())

class StartMassView(discord.ui.View):
    @discord.ui.button(label="🌀", style=discord.ButtonStyle.blurple)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(MassInfoModal())

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

class ReviewModal(discord.ui.Modal, title="mass review"):

    server_link = discord.ui.TextInput(
        label="server invite link",
        placeholder="https://discord.gg/...",
        required=True
    )
    

    invites = discord.ui.TextInput(
        label="invites gained",
        placeholder="numbers only",
        required=True
    )

    portals = discord.ui.TextInput(
        label="portals posted",
        placeholder="numbers only",
        required=True
    )

    sep = discord.ui.TextInput(
        label="sep posted (hours)",
        placeholder="numbers only",
        required=True
    )

    server_toxicity = discord.ui.TextInput(
        label="server toxicity",
        placeholder="stox, ntox...",
        required=True
    )

    server_type = discord.ui.TextInput(
        label="server type",
        placeholder="type of server",
        required=True
    )

async def on_submit(self, interaction: discord.Interaction):

    # ✅ THIS FIXES THE ERROR
    await interaction.response.defer(ephemeral=True)

    # Validate numbers
    if not self.invites.value.isdigit() or not self.portals.value.isdigit() or not self.sep.value.isdigit():
        await interaction.followup.send(
            "invites, portals, and sep must be numbers only."
        )
        return

    invites = int(self.invites.value)
    portals = int(self.portals.value)
    sep = int(self.sep.value)

    server_link = self.server_link.value
    toxicity = self.server_toxicity.value
    server_type = self.server_type.value

    user_id = str(interaction.user.id)

    review_counts[user_id] = review_counts.get(user_id, 0) + 1

    with open("reviews.json", "w") as f:
        json.dump(review_counts, f)

    channel = interaction.guild.get_channel(REVIEW_CHANNEL_ID)

    message_text = f"""
_ _
_ _ 　 ⚞𓈒゜{invites}　 invites　  ᣟ◌　 +{portals}p
-# _ _ 　 <:0_:1488029407192023141>     {sep}h ⎯ {toxicity} ({server_type}) ৲੭
_ _ [⠀]({server_link})
"""

    msg = await channel.send(message_text)

    # ✅ Create thread + ping user
    thread = await msg.create_thread(
        name=f"review - {interaction.user.name}"
    )

    await thread.send(f"{interaction.user.mention}")

    # ✅ Final response (NO MORE ERROR)
    await interaction.followup.send("review submitted!")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    guild = discord.Object(id=GUILD_ID)
    bot.tree.clear_commands(guild=guild)
    bot.tree.copy_global_to(guild=guild)
    synced = await bot.tree.sync(guild=guild)
    print(f"Synced {len(synced)} commands")
    print("Commands registered:")
    for cmd in bot.tree.get_commands():
        print(cmd.name)


@bot.tree.command(name="review", description="submit a review")
async def review(interaction: discord.Interaction):
    try:
        await interaction.response.send_modal(ReviewModal())
    except Exception as e:
        print("ERROR:", e)

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

    await interaction.response.defer(ephemeral=True)

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

    ticket_channels[interaction.user.id] = channel.id

    await channel.send(user.mention, delete_after=5)

    await channel.send(
"""
_ _
_ _　　　　　　　　𓈒　 ꜜ ㅤ𓂃ㅤ ❤︎    welcome 
_ _　　　　　　　　⠾    ** click below**      ⠀ 𝄞 ⋆ˎˊ- ⠀
_ _
""",
view=StartMassView()
)
    
    await interaction.followup.send(
    f"your ticket has been created {channel.mention}",
    ephemeral=True
)

@bot.command()
async def close(ctx):

    log_channel = bot.get_channel(TICKET_LOG_CHANNEL)

    messages = []
    async for msg in ctx.channel.history(limit=None, oldest_first=True):
        messages.append(f"{msg.author}: {msg.content}")

    transcript = "\n".join(messages)

    if log_channel:
        if len(transcript) > 1900:
            with open("transcript.txt", "w", encoding="utf-8") as f:
                f.write(transcript)

            await log_channel.send(
                f"📁 Transcript from {ctx.channel.name}",
                file=discord.File("transcript.txt")
            )
        else:
            await log_channel.send(
                f"📁 Transcript from {ctx.channel.name}\n```{transcript}```"
            )

    await ctx.send("Closing ticket...")
    await ctx.channel.delete()

class MassingSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="skip", value="skip", description="Tag as skip"),
            discord.SelectOption(label="invalid", value="invalid", description="Tag as invalid"),
            discord.SelectOption(label="reset", value="reset", description="Reset")
        ]

        super().__init__(
            placeholder="tag your skips here",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        choice = self.values[0]
        user_id = interaction.user.id

        if user_id not in ticket_channels:
            await interaction.response.send_message("No ticket found.", ephemeral=True)
            return

        ticket_channel = interaction.guild.get_channel(ticket_channels[user_id])

        if choice == "skip":
            await interaction.response.send_message("tagged successfully", ephemeral=True)
            await ticket_channel.send(f"<#{interaction.channel.id}> was tagged as skip")

        elif choice == "invalid":
            await interaction.response.send_message("tagged successfully", ephemeral=True)
            await ticket_channel.send(f"<#{interaction.channel.id}> was tagged as invalid")

        elif choice == "reset":
            await interaction.response.send_message("reset!", ephemeral=True)

        self.view.stop()

class MassingView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(MassingSelect())

@bot.command()
async def selectmenu(ctx):

    await ctx.send(
        "tag your skips here",
        view=MassingView()
    )


import os
bot.run(os.getenv("TOKEN"))