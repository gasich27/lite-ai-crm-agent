from dotenv import load_dotenv

from app.telegram_bot.bot import run_bot


load_dotenv()


if __name__ == "__main__":
    run_bot()

