import os
import dspy

import discord

try:
    from litellm.exceptions import APIConnectionError
except Exception:  # litellm may not expose this in older versions
    APIConnectionError = Exception

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

guild_id = os.getenv("1483181346816917640")
guild = discord.Object(id=int(guild_id)) if guild_id else None
tree_command = (lambda **kwargs: bot.tree.command(guild=guild, **kwargs)) if guild else bot.tree.command

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

def model_call_or_error(prompt: str, code: str):
    try:
        return qa(ques=prompt, code=code).answer, None
    except APIConnectionError as exc:
        return None, exc
    except Exception as exc:
        msg = str(exc)
        if "Connection refused" in msg or "APIConnectionError" in msg or "Ollama" in msg:
            return None, exc
        raise

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

@tree_command(name="talk_to_cole", description="Talk to cole and ask him questions about his code.")
async def talk_to_cole(interaction: discord.Interaction, question: str):
    print("Talking to cole in server: ", interaction.guild_id)
    await interaction.response.defer(thinking=True)
    feedback, model_err = model_call_or_error(question, "please talk as cole and answer the question based on what you know about him and his code. be as detailed as possible in your answer. Also, please talk like him, like using his common phrases and slang. If you dont know the answer, say you dont know but try to give your best guess. Here is some information about cole: cole is a software engineer who has been coding for 10 years. he has worked at google and facebook. he is currently working on a project called dspy which is a library for building AI agents. he is very smart and funny. he loves to make jokes and use memes in his code comments.")
    if model_err:
        await interaction.followup.send("Model backend is unavailable. Make sure Ollama is running and OLLAMA_API_BASE is reachable.")
        return
    await interaction.followup.send(safe_text(feedback))


@tree_command(name="give_suggestions", description="Gives suggestions to add to code.")
async def give_suggestions(interaction: discord.Interaction, code: str):
    await interaction.response.defer(thinking=True)
    print("Giving suggestions for code in server: ", interaction.guild_id)
    feedback, model_err = model_call_or_error("What are some things i can do better with this code?", code)
    if model_err:
        await interaction.followup.send("Model backend is unavailable. Make sure Ollama is running and OLLAMA_API_BASE is reachable.")
        return

    code_lower = code.lower()
    contains_bad = any(bad in code_lower for bad in BAD_WORDS)
    true_is_sussy = False
    if contains_bad:
        sussy_raw = is_sussy(comment=code).notNice
        true_is_sussy = to_bool_strict(sussy_raw)

    if true_is_sussy:
        feedback = "AYO buddy that isnt nice buckaroo you should be nice to people \ud83d\ude2d\u270c\ufe0f"

    await interaction.followup.send(safe_text(feedback))
    
@tree_command(name="ping", description="Check if the bot is alive.")
async def ping(interaction: discord.Interaction):
    print("Pinged in server: ", interaction.guild_id)
    await interaction.response.send_message("We're online!")

@tree_command(name="echo", description="Echo back your message.")
async def echo(interaction: discord.Interaction, message: str):
    print("Echoing message " + message + " in server: ", interaction.guild_id)
    await interaction.response.send_message(message)

@tree_command(name="explain_code", description="Explains the code in full detail.")
async def explain_code(interaction: discord.Interaction, code: str):
    # Acknowledge quickly to avoid the 3-second interaction timeout.
    await interaction.response.defer(thinking=True)
    print("Explaining code in server: ", interaction.guild_id)
    feedback, model_err = model_call_or_error("What is this code doing and what are some key points in the code?", code)
    if model_err:
        await interaction.followup.send("Model backend is unavailable. Make sure Ollama is running and OLLAMA_API_BASE is reachable.")
        return

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
