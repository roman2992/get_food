# Pizza Bot MVP

Telegram-бот для заказа пиццы: каталог, размеры, корзина, оформление заказа, история, админ-уведомления и статусы.

## Запуск
1. Создайте бота через @BotFather.
2. Скопируйте `.env.example` в `.env`.
3. Укажите `BOT_TOKEN` и Telegram ID администраторов в `ADMIN_IDS`.
4. Запустите `docker compose up --build`.

Локально: Python 3.12+, PostgreSQL и `pip install -r requirements.txt`, затем `python -m bot.main`.

Команды: `/start`, `/menu`, `/cart`, `/orders`, `/admin`, `/orders_admin`.
