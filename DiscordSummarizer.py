# DiscordSummarizer.py

import os, json, discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timezone
from openai import OpenAI

# ─── Load configuration ────────────────────────────────────────────────────────
load_dotenv()

BOT_TOKEN      = os.getenv("DISCORD_BOT_TOKEN")
SRC_CHANNELS   = [int(x) for x in os.getenv("DISCORD_SOURCE_CHANNEL_IDS","").split(",") if x]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LAST_READ_FILE = os.getenv("LAST_READ_FILE", "last_read.json")
MODEL_NAME     = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")  # Change your ChatGPT version here

if not BOT_TOKEN or not SRC_CHANNELS or not OPENAI_API_KEY:
    raise RuntimeError("Missing DISCORD_BOT_TOKEN, DISCORD_SOURCE_CHANNEL_IDS, or OPENAI_API_KEY")

# ─── Persistence ────────────────────────────────────────────────────────────────
def load_last_read():
    if os.path.exists(LAST_READ_FILE):
        return json.load(open(LAST_READ_FILE, "r", encoding="utf-8"))
    cutoff = int((datetime.now(timezone.utc).timestamp() - 86400) * 1000)
    return { str(cid): cutoff for cid in SRC_CHANNELS }

def save_last_read(data):
    json.dump(data, open(LAST_READ_FILE, "w", encoding="utf-8"), indent=2)

# ─── OpenAI client ─────────────────────────────────────────────────────────────
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_messages(channel_id, messages):
    prompt = (
        f"Messages in `{channel_id}`:\n\n" + "\n".join(messages) +
        "\n\nSummarize everything missed, more detail for longer chats."
    )
    try:
        resp = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content":prompt}],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠ OpenAI error: {e}")
        return "⚠ Unable to generate summary."

# ─── Discord Bot ───────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

@bot.command(name="summarize", help="Summarize unread messages; DM you the digest.")
async def summarize(ctx):
    async with ctx.typing():
        last = load_last_read()
        new_last = {}
        all_summaries = []

        for cid in SRC_CHANNELS:
            try:
                ch = await bot.fetch_channel(cid)
            except Exception as e:
                print(f"⚠ Cannot fetch channel {cid}: {e}")
                continue

            after_ts = last.get(str(cid), 0)
            after_dt = datetime.fromtimestamp(after_ts/1000, tz=timezone.utc)

            msgs = []
            async for m in ch.history(limit=None, after=after_dt, oldest_first=True):
                t = m.created_at.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M")
                msgs.append(f"[{t}] {m.author.name}: {m.content.replace(chr(10),' ')}")

            if msgs:
                summary = summarize_messages(cid, msgs)
                header = f"**{ch.guild.name}#{ch.name}**\n"
                all_summaries.append(header + summary)

            new_last[str(cid)] = int(datetime.now(timezone.utc).timestamp()*1000)

        digest = "\n\n".join(all_summaries) if all_summaries else "🟢 No new messages."

    # DM the user
    embed = discord.Embed(
        title=f"Discord Digest @ {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC}",
        description=digest,
        color=discord.Color.blue()
    )
    try:
        await ctx.author.send(embed=embed)
    except Exception as e:
        await ctx.reply(f"❌ Could not DM you: {e}", mention_author=False)
        return

    save_last_read(new_last)
    await ctx.reply("✅ Digest sent to your DMs!", mention_author=False)

@bot.command(name="markread", help="Mark all as read without summary.")
async def markread(ctx):
    now_ms = int(datetime.now(timezone.utc).timestamp()*1000)
    save_last_read({ str(cid): now_ms for cid in SRC_CHANNELS })
    await ctx.reply("✅ All channels marked as read.", mention_author=False)

# ─── Kick off the bot ──────────────────────────────────────────────────────────
bot.run(BOT_TOKEN)
