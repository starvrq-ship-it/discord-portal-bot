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


    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.listening,
            name="⚞     celeste's   portɑl     𓈃"
        )
    )

    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
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
    
    await interaction.followup.send("🎟️ Ticket created!", ephemeral=True)

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

variable : ticket
value : 0

class MassSelect(discord.ui.View):
    def __init__(self):
        super().__init__()

        select = discord.ui.Select(
            placeholder="tag ur skips here",
            options=[
                discord.SelectOption(label="tag as skip!", value="skip"),
                discord.SelectOption(label="tag as invalid!", value="invalid"),
                discord.SelectOption(label="reset!", value="reset"),
            ]
        )

        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        value = interaction.data["values"][0]

        if value == "skip":
            await interaction.response.send_message("tagged successfully", ephemeral=True)
            await interaction.channel.send(f"{interaction.channel.mention} was tagged as skip")

        elif value == "invalid":
            await interaction.response.send_message("tagged successfully", ephemeral=True)
            await interaction.channel.send(f"{interaction.channel.mention} was tagged as invalid")

        elif value == "reset":
            await interaction.response.send_message("resetted!", ephemeral=True)

        await interaction.message.edit(view=None)
@bot.command()
async def selectmenu(ctx):
    await ctx.send("Select an option:", view=MassSelect())

import os
bot.run(os.getenv("TOKEN"))