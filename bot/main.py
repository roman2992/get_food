import asyncio,logging
from aiogram import Bot,Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from .config import load_config
from .db import Base,create_session_factory
from .cart import Cart
from .seed import seed
from .handlers import client,admin

async def main():
    logging.basicConfig(level=logging.INFO)
    config=load_config(); engine,factory=create_session_factory(config)
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    async with factory() as s: await seed(s)
    bot=Bot(config.bot_token,default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp=Dispatcher(storage=MemoryStorage()); cart=Cart()
    async def middleware(handler,event,data):
        async with factory() as session:
            data.update(session=session,config=config,cart_service=cart,bot=bot)
            return await handler(event,data)
    dp.message.middleware(middleware); dp.callback_query.middleware(middleware)
    dp.include_router(client.router); dp.include_router(admin.router)
    try: await dp.start_polling(bot)
    finally: await bot.session.close(); await engine.dispose()

if __name__=="__main__": asyncio.run(main())
