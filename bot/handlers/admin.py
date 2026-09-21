from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from ..models import Order,OrderStatus
from ..text import order_text
from ..ui import admin as admin_kb

router=Router()

def ok(uid,config): return uid in config.admin_ids

@router.message(Command("admin"))
async def admin(m,config):
    if ok(m.from_user.id,config): await m.answer("🛠 Админка\n/orders_admin — активные заказы")

@router.message(Command("orders_admin"))
async def orders_admin(m,session,config):
    if not ok(m.from_user.id,config): return
    r=await session.execute(select(Order).where(Order.status.not_in(["completed","cancelled"])).options(selectinload(Order.items),selectinload(Order.user)).order_by(Order.created_at.desc()))
    os=list(r.scalars())
    if not os: await m.answer("Активных заказов нет."); return
    for o in os: await m.answer(order_text(o,config.currency),reply_markup=admin_kb(o.id,o.status))

@router.callback_query(F.data.startswith("status:"))
async def status(c,session,config,bot):
    if not ok(c.from_user.id,config): await c.answer("Нет доступа",show_alert=True); return
    _,oid,status=c.data.split(":"); o=await session.get(Order,int(oid),options=[selectinload(Order.items),selectinload(Order.user)])
    if not o: await c.answer("Не найден",show_alert=True); return
    o.status=status; await session.commit()
    await c.message.edit_text(order_text(o,config.currency),reply_markup=admin_kb(o.id,o.status))
    labels={"accepted":"✅ Заказ принят","cooking":"👨‍🍳 Заказ готовится","delivery":"🚚 Заказ у курьера","completed":"🏁 Заказ доставлен","cancelled":"❌ Заказ отменён"}
    try: await bot.send_message(o.user.telegram_id,f"📦 Заказ #{o.id}\n\n{labels.get(status,status)}")
    except Exception: pass
    try:
        await c.answer("Статус изменён")
    except Exception:
        pass
