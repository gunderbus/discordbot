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

def answer_question(question: str) -> str:
    # Placeholder for actual question-answering logic
    return 

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
    feedback = f"Received your code:\n```\n{code}\n```\nThis is just a placeholder response."
    await interaction.response.send_message(feedback)

token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("Missing DISCORD_TOKEN env var.")

bot.run(token)
