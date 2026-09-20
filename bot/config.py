import os
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()

@dataclass(frozen=True)
class Config:
    bot_token: str
    database_url: str
    admin_ids: set[int]
    currency: str
    delivery_price: int

def load_config():
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN is not configured")
    admins = {int(x.strip()) for x in os.getenv("ADMIN_IDS","").split(",") if x.strip()}
    return Config(token, os.getenv("DATABASE_URL","postgresql+asyncpg://pizza:pizza@localhost:5432/pizza"),
                  admins, os.getenv("CURRENCY","₽"), int(os.getenv("DELIVERY_PRICE","150")))
