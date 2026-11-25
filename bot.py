import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
    )


def send_photo(chat_id, photo, caption):
    requests.post(
        f"{TELEGRAM_API}/sendPhoto",
        json={
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "parse_mode": "HTML"
        }
    )


def search_movie(movie_name):
    url = "https://www.omdbapi.com/"
    params = {
        "apikey": OMDB_API_KEY,
        "s": movie_name,
        "type": "movie"
    }

    response = requests.get(url, params=params, timeout=15)
    return response.json()


@app.route("/")
def home():
    return "🎬 Movie Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if not data or "message" not in data:
        return "OK"

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if text == "/start":
        send_message(
            chat_id,
            "🎬 <b>Welcome to Movie Hub!</b>\n\n"
            "🔍 Movie name type panni search pannunga.\n\n"
            "🖼️ Posters\n"
            "⭐ Ratings\n"
            "🎭 Movie details\n"
            "🍿 Movie discovery"
        )
        return "OK"

    if text == "/help":
        send_message(
            chat_id,
            "🎬 Movie name type pannunga!\n"
            "Example: Avatar, Leo, Interstellar"
        )
        return "OK"

    if text:
        result = search_movie(text)

        if result.get("Response") == "True":
            movies = result.get("Search", [])

            for movie in movies[:5]:
                title = movie.get("Title", "Unknown")
                year = movie.get("Year", "Unknown")
                poster = movie.get("Poster", "")

                caption = (
                    f"🎬 <b>{title}</b>\n"
                    f"📅 Year: {year}\n\n"
                    f"🔎 Movie information:\n"
                    f"https://www.imdb.com/find/?q="
                    f"{requests.utils.quote(title)}\n\n"
                    f"🍿 Availability:\n"
                    f"https://www.justwatch.com/in/search?q="
                    f"{requests.utils.quote(title)}"
                )

                if poster and poster != "N/A":
                    send_photo(chat_id, poster, caption)
                else:
                    send_message(chat_id, caption)

        else:
            send_message(
                chat_id,
                "❌ Movie not found.\n"
                "Spelling check panni try pannunga!"
            )

    return "OK"


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
