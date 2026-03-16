import os
import dspy

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# configure your model (Ollama)
ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
ollama_api_base = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
lm = dspy.LM(
    f"ollama_chat/{ollama_model}",
    api_base=ollama_api_base,
    api_key="",
)
dspy.settings.configure(lm=lm)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class QA(dspy.Signature):
    # Placeholder for actual question-answering logic
    ques = dspy.InputField()
    code = dspy.InputField()
    answer = dspy.OutputField()

class NotNice(dspy.Signature):
    """Determine if the comment is not nice. Reply with true or false only."""
    comment = dspy.InputField()
    notNice = dspy.OutputField(desc="true if the comment is not nice, else false")

qa = dspy.Predict(QA)
is_sussy = dspy.Predict(NotNice)

guild_id = os.getenv("DISCORD_GUILD_ID")
guild = discord.Object(id=int(guild_id)) if guild_id else None

# Simple guard to prevent always-true model outputs.
BAD_WORDS = {
    "idiot",
    "stupid",
    "dumb",
    "hate",
    "kill",
    "shut up",
}


def safe_text(text: str) -> str:
    # Replace invalid UTF-8 surrogates that Discord rejects.
    return text.encode("utf-8", "replace").decode("utf-8")


def to_bool_strict(value) -> bool:
    return str(value).strip().lower() == "true"


@bot.event
async def on_ready():
    try:
        if guild:
            await bot.tree.sync(guild=guild)
            print(f"Synced commands to guild {guild.id}")
        else:
            await bot.tree.sync()
            print("Synced commands globally (may take up to 1 hour).")
    except Exception as exc:
        print(f"Command sync failed: {exc}")
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="ping", description="Check if the bot is alive.")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("I love parker so much!")

@bot.tree.command(name="echo", description="Echo back your message.")
async def echo(interaction: discord.Interaction, message: str):
    await interaction.response.send_message(message)

@bot.tree.command(name="check_code", description="Checks code and gives feedback.")
async def check_code(interaction: discord.Interaction, code: str):
    # Acknowledge quickly to avoid the 3-second interaction timeout.
    await interaction.response.defer(thinking=True)

    feedback = qa(ques="Please give me an explination of the code, three things i can do better in bullet points, and someplaces you might think that errors will occur.", code=code).answer

    code_lower = code.lower()
    contains_bad = any(bad in code_lower for bad in BAD_WORDS)
    true_is_sussy = False
    if contains_bad:
        sussy_raw = is_sussy(comment=code).notNice
        true_is_sussy = to_bool_strict(sussy_raw)

    if true_is_sussy:
        feedback = "AYO buddy that isnt nice buckaroo you should be nice to people \ud83d\ude2d\u270c\ufe0f"

    await interaction.followup.send(safe_text(feedback))

token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("Missing DISCORD_TOKEN env var.")

bot.run(token)
