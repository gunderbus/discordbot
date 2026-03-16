import os
import dspy

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# configure your model
lm = dspy.OpenAI(model="gpt-4o-mini")
dspy.settings.configure(lm=lm)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class QA(dspy.Signature):
    # Placeholder for actual question-answering logic
    ques = dspy.InputField()
    code = dspy.InputField()
    answer = dspy.OutputField()


@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
    except Exception as exc:
        print(f"Command sync failed: {exc}")
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="ping", description="Check if the bot is alive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("I love parker so much!")

@bot.tree.command(name="echo", description="Echo back your message.")
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="Check Code", description="Checks code and gives feedback.")
async def check_code(interaction: discord.Interaction, code: str):
    # Placeholder for code checking logic
    feedback = QA(ques="Is this code correct?", code=code).answer
    isSussy = dspy.predict(dspy.Signature("comment -> notNice: bool ", instructions="Determine if the comment is not nice."))
    commend = code
    trueIsSussy = isSussy(commend=commend).notNice

    if(trueIsSussy):
        feedback = "AYO buddy that isnt nice buckaroo you should be nice to people 😭✌️"

    await interaction.response.send_message(feedback)

token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("Missing DISCORD_TOKEN env var.")

bot.run(token)
