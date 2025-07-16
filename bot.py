import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import requests

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Funkcja poprawiająca typowe literówki
def popraw_tekst(tekst):
    poprawki = {
        "prosim": "proszę",
        "muy": "wiele",
        "w muy sposobach": "na wiele sposobów",
        "was": "Cię",
        # możesz dopisać więcej poprawek
    }
    for blad, poprawka in poprawki.items():
        tekst = tekst.replace(blad, poprawka)
    return tekst

# Twój kanał, na którym działa !ai
ALLOWED_CHANNEL_ID = 1394226059003691079

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command(name="pomoc")
async def pomoc(ctx):
    await ctx.send(f"ℹ️ Komenda !ai działa tylko na kanale o ID: {ALLOWED_CHANNEL_ID}")

@bot.command()
async def ai(ctx, *, prompt):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        await ctx.send("❌ Ta komenda działa tylko na wyznaczonym kanale.")
        return

    await ctx.send("🤖 Przetwarzam zapytanie...")

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [
                {"role": "system", "content": "Jesteś pomocnym asystentem AI, który mówi tylko po polsku."},
                {"role": "user", "content": prompt}
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )

        result = response.json()

        if "choices" in result and result["choices"]:
            message = result["choices"][0]["message"]["content"]
            poprawiona_wiadomosc = popraw_tekst(message)
            await ctx.send(poprawiona_wiadomosc)
        else:
            await ctx.send(f"❌ Błąd: Brak odpowiedzi od modelu. Odpowiedź z API: {result}")

    except Exception as e:
        await ctx.send(f"❌ Wystąpił błąd: {e}")

bot.run(TOKEN)

