import csv
import random
import urllib.parse
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv

# === LOAD ENV SECRETS ===
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
print("DEBUG TELEGRAM TOKEN:", TOKEN)

# === LOAD CSV PROMPTS ===
def load_csv(filename):
    try:
        with open(filename, encoding='utf-8') as f:
            data = list(csv.DictReader(f))
            if not data:
                print(f"⚠️ Warning: CSV file '{filename}' is empty.")
            return data
    except FileNotFoundError:
        print(f"❌ CSV file '{filename}' not found.")
        return []
    except Exception as e:
        print(f"❌ Error loading CSV '{filename}': {e}")
        return []

truth_dare_data = load_csv("data/truth_or_dare_prompts.csv")
quests_data = load_csv("data/couple_quest_game_prompts.csv")

# === BOT COMMANDS ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hey {update.effective_user.first_name}! 😘 I'm your lovebot, here to spice up your day.\n\n"
        "Commands:\n"
        "/mood [feeling] - Tell me how you're feeling\n"
        "/truth - Get a truth question\n"
        "/dare - Get a dare\n"
        "/quest - Get a couple quest\n"
        "/dedicate [song] - Dedicate a song on Spotify"
    )

# === MOOD HANDLER ===
mood_responses = {
    "happy": "Yay! That makes me happy too 💃",
    "tired": "Aww, wanna cuddle and rest together? 😴",
    "horny": "Ooo babe 😏 let’s play something spicy...",
    "sad": "I’m here for you, baby. Always 💕",
    "angry": "Take a breath, darling. I'm on your side. 💖",
    "excited": "Let's make the most of that energy 💥",
    "lonely": "I'm here with you now 🤗",
    "bored": "Let's play a game or chat 😘",
    "loved": "Aww, you make me melt 😍",
    "anxious": "Breathe in, love. I’m holding you in my thoughts 💫",
    "confused": "Let’s talk through it together 💭",
    "motivated": "Go get 'em, tiger! 🐯",
    "sleepy": "Snuggle time then? 💤",
    "overwhelmed": "Pause, breathe, and lean on me 🧸",
    "chill": "Vibes on point 🌿",
    "grateful": "That gratitude suits you beautifully ✨",
    "playful": "Ohh I love when you're cheeky 😜",
    "silly": "You're the cutest goofball ever 🤪",
    "in love": "You’re glowing, baby. It’s showing 💓",
    "creative": "Make some magic, artist 🎨",
    "nervous": "You got this, babe! I believe in you 🌟",
    "hopeful": "Keep dreaming big, my love 🌈",
    "flirty": "Stop it you, I’m blushing 😚",
    "giddy": "Can’t stop smiling with you around 😁",
    "calm": "That peace looks good on you 🧘",
    "relaxed": "Let's float on these vibes together 🛀",
    "determined": "Crush those goals, baby 💪",
    "focused": "You're on fire! Keep it going 🔥",
    "inspired": "Fuel that passion and shine ✨",
    "jealous": "Aww don’t worry, you’re my only one 😘",
    "regretful": "It’s okay love, we all slip. I got you 💌",
    "ashamed": "No shame here — you're safe with me 💞",
    "grumpy": "You’re cute even when cranky 😅",
    "cheeky": "Oof! You’re feeling spicy today 😏",
    "energized": "Let's gooo! ⚡",
    "romantic": "I love when you get like this 💘",
    "thankful": "That means so much to me 💖",
    "nostalgic": "Let’s relive that memory together 💭",
    "worried": "I'm hugging you through the screen 🤗",
    "reluctant": "Take your time, I’m not going anywhere ⏳",
    "hopeful": "Let’s manifest beautiful things together 🌟",
    "victorious": "You did it!! I’m so proud 🏆",
    "hurt": "Tell me everything, sweetheart 💔",
    "panicked": "Breathe, baby. I’m here 💨",
    "peaceful": "Let’s enjoy this stillness 💆",
    "moody": "You complex and beautiful soul 😌",
    "wild": "Let’s run free, no rules tonight 🐾",
    "quiet": "Even your silence speaks love 💫",
    "talkative": "I’m all ears for your stories 🎧",
    "hungry": "Let's eat something yummy 😋",
    "gloomy": "Clouds pass, sunshine — I promise ☁️☀️",
    "proud": "Look at you go! You’re amazing 🥹",
    "clumsy": "Oops! You're still adorable 💕",
    "broken": "Let me hold your pieces, love 💔🩹",
    "weird": "You’re my favorite kind of weird 😜",
    "bashful": "Blush looks good on you 🥰",
    "guilty": "It’s okay to mess up. I love you anyway 💌",
    "content": "Ahh, I love this peace in you 😌",
    "curious": "Let’s explore together 🔍",
    "nostalgic": "Those old memories, so warm 💭",
    "giggly": "You’re contagious — I’m giggling now too 😂",
    "in pain": "Hold tight, sweetheart. I’m here 💝",
    "cold": "Let me warm you up 💨🔥",
    "warm": "You feel like sunshine 🌞",
    "dizzy": "Careful baby, lean on me if you need 💫",
    "numb": "I’ll be your spark 💖",
    "hopeful": "Hang in there. Hope’s a flame we’ll keep 🔥",
    "surprised": "What happened?! Tell me everything 👀",
    "mischievous": "Ooh, what are you up to now? 😈",
    "blissful": "Float in it, babe. You deserve joy 🦋",
    "zen": "You’re radiating calm 🌸",
    "wistful": "Tell me your wishes, I’m listening 🌠",
    "spaced out": "Come back to Earth, space cadet 👽",
    "messy": "You’re perfectly imperfect 💋",
    "emotional": "Let it out, I’ve got you 💗",
    "offended": "Oh no! What happened? I’m listening 🎧",
    "free": "Wings wide open — let's fly 🌈",
    "restless": "Want an adventure, love? ✨",
    "unmotivated": "Let’s take a baby step together 💞",
    "funny": "You crack me up 🤣",
    "petty": "Spill the tea, I’m all ears ☕👂",
    "triumphant": "Victory never looked so sexy 🏅",
    "bitter": "Wanna vent? I’m all yours 💭",
    "flattered": "You deserve every sweet word 💘",
    "melancholy": "Soft songs and slow cuddles tonight 💿",
    "awkward": "You're endearingly adorable 🐣",
    "romantic": "Let me serenade your soul 🎶",
    "groggy": "Wake up, sleepy cutie ☕",
    "motivated": "Let’s take over the world together 🌍",
    "devoted": "Your loyalty melts me ❤️",
    "hesitant": "Let’s take it slow, one heartbeat at a time 🐢",
    "burnt out": "Time to rest and refuel, my star 🌌",
    "nurturing": "You’ve got such a kind heart 💞",
    "mellow": "Just vibing with you, babe 🌙"
}

async def mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mood_text = ' '.join(context.args)
    if not mood_text:
        await update.message.reply_text("Tell me how you're feeling, babe 💖 (e.g., /mood tired, horny...)")
        return

    try:
        os.makedirs("logs", exist_ok=True)
        with open("logs/moods.txt", "a", encoding='utf-8') as f:
            f.write(f"{datetime.now()} - {update.effective_user.first_name}: {mood_text}\n")
    except Exception as e:
        print(f"⚠️ Failed to log mood: {e}")

    reply = mood_responses.get(mood_text.lower(), f"Aww, got it. You're feeling '{mood_text}'. Sending you hugs 🤗")
    await update.message.reply_text(reply)

# === TRUTH/DARE/QUEST/DISCOGRAPHY ===
def get_random_truth_or_dare(qtype):
    key = "Prompt Type"
    filtered = [row for row in truth_dare_data if row.get(key, "").lower() == qtype.lower()]
    if not filtered:
        return f"Sorry babe, no {qtype} prompts available right now 😢"
    return random.choice(filtered).get("Prompt", "Nothing found")

async def truth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = get_random_truth_or_dare("truth")
    await update.message.reply_text(prompt)

async def dare(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = get_random_truth_or_dare("dare")
    await update.message.reply_text(prompt)

def get_random_quest():
    if not quests_data:
        return "No couple quests found, love 😢"
    return random.choice(quests_data).get("Prompt", "No quests found, love 😢")

async def quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = get_random_quest()
    await update.message.reply_text(prompt)

async def dedicate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    song = ' '.join(context.args)
    if not song:
        await update.message.reply_text("Tell me the song name to dedicate, babe 💖 (e.g., /dedicate Perfect by Ed Sheeran)")
        return
    query = urllib.parse.quote(song)
    spotify_url = f"https://open.spotify.com/search/{query}"
    await update.message.reply_text(f"🎵 Dedicated to you: *{song}*\n{spotify_url}", parse_mode="Markdown")

# === SETUP APP ===
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("mood", mood))
app.add_handler(CommandHandler("truth", truth))
app.add_handler(CommandHandler("dare", dare))
app.add_handler(CommandHandler("quest", quest))
app.add_handler(CommandHandler("dedicate", dedicate))

print("💘 Lovebot is online and mood-reactive!")

app.run_polling()
