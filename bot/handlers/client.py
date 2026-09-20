from aiogram import Router,F
from aiogram.filters import Command
from aiogram.types import Message,CallbackQuery
from aiogram.fsm.context import FSMContext
from ..ui import main,pizzas_menu,sizes,qty,cart,payment,confirm
from ..text import money,cart_text,order_text
from ..repo import pizzas,pizza,user,create_order,orders
from ..states import Checkout

router=Router()

@router.message(Command("start"))
async def start(m:Message): await m.answer("🍕 <b>Добро пожаловать!</b> Выберите действие:",reply_markup=main())

@router.message(F.text.in_({"🍕 Меню","/menu"}))
async def menu(m,session):
    ps=await pizzas(session)
    text="🍕 <b>Меню</b>\n\n"+"\n".join(f"<b>{p.name}</b> — от {money(p.price_25,'₽')}\n{p.description}" for p in ps)
    await m.answer(text,reply_markup=pizzas_menu(ps))

@router.callback_query(F.data=="menu")
async def menu_cb(c,session):
    ps=await pizzas(session)
    await c.message.edit_text("🍕 <b>Меню</b>",reply_markup=pizzas_menu(ps)); await c.answer()

@router.callback_query(F.data.startswith("pizza:"))
async def details(c,session):
    p=await pizza(session,int(c.data.split(":")[1]))
    await c.message.edit_text(f"🍕 <b>{p.name}</b>\n\n{p.description}\n\nВыберите размер:",reply_markup=sizes(p.id)); await c.answer()

@router.callback_query(F.data.startswith("size:"))
async def size_cb(c,session):
    _,pid,s=c.data.split(":"); p=await pizza(session,int(pid)); size=int(s)
    price={25:p.price_25,30:p.price_30,35:p.price_35}[size]
    await c.message.edit_text(f"{p.name}, {size} см — {money(price,'₽')}\n\nКоличество:",reply_markup=qty(p.id,size)); await c.answer()

@router.callback_query(F.data.startswith("qty:"))
async def qty_cb(c,session,cart_service):
    _,pid,s,q=c.data.split(":"); p=await pizza(session,int(pid)); size=int(s)
    price={25:p.price_25,30:p.price_30,35:p.price_35}[size]
    cart_service.add(c.from_user.id,p.id,p.name,size,price,int(q))
    await c.message.edit_text("✅ Добавлено в корзину. Нажмите «🛒 Корзина»."); await c.answer()

@router.message(F.text.in_({"🛒 Корзина","/cart"}))
async def cart_msg(m,cart_service,config):
    items=cart_service.items(m.from_user.id)
    await m.answer(cart_text(items,config.currency,config.delivery_price),reply_markup=cart(items))

@router.callback_query(F.data.startswith(("inc:","dec:")))
async def cart_change(c,cart_service,config):
    action,key=c.data.split(":",1)
    (cart_service.inc if action=="inc" else cart_service.dec)(c.from_user.id,key)
    items=cart_service.items(c.from_user.id)
    await c.message.edit_text(cart_text(items,config.currency,config.delivery_price),reply_markup=cart(items)); await c.answer()

@router.callback_query(F.data=="clear_cart")
async def clear(c,cart_service):
    cart_service.clear(c.from_user.id); await c.message.edit_text("🛒 Корзина очищена."); await c.answer()

@router.callback_query(F.data=="checkout")
async def checkout(c,state,cart_service):
    if not cart_service.items(c.from_user.id): await c.answer("Корзина пуста",show_alert=True); return
    await state.set_state(Checkout.name); await c.message.edit_text("Введите имя получателя:"); await c.answer()

@router.message(Checkout.name)
async def name(m,state): await state.update_data(name=m.text.strip()); await state.set_state(Checkout.phone); await m.answer("📞 Введите телефон:")

@router.message(Checkout.phone)
async def phone(m,state): await state.update_data(phone=m.text.strip()); await state.set_state(Checkout.address); await m.answer("📍 Введите адрес доставки:")

@router.message(Checkout.address)
async def address(m,state): await state.update_data(address=m.text.strip()); await state.set_state(Checkout.comment); await m.answer("💬 Комментарий или «нет»:")

@router.message(Checkout.comment)
async def comment(m,state):
    await state.update_data(comment=None if m.text.strip().lower()=="нет" else m.text.strip())
    await state.set_state(Checkout.payment); await m.answer("Выберите оплату:",reply_markup=payment())

@router.callback_query(Checkout.payment,F.data.startswith("pay:"))
async def pay(c,state,cart_service,config):
    p=c.data.split(":")[1]; await state.update_data(payment=p,payment_name="Наличными" if p=="cash" else "Картой курьеру")
    d=await state.get_data(); items=cart_service.items(c.from_user.id)
    s=cart_service.total(c.from_user.id)
    await state.set_state(Checkout.confirm)
    await c.message.edit_text(f"🔎 <b>Проверьте заказ</b>\n\n👤 {d['name']}\n📞 {d['phone']}\n📍 {d['address']}\n💳 {d['payment_name']}\n\n{cart_text(items,config.currency,config.delivery_price)}",reply_markup=confirm())
    await c.answer()

@router.callback_query(Checkout.confirm,F.data=="confirm")
async def confirm_order(c,state,session,cart_service,config,bot):
    items=cart_service.items(c.from_user.id); d=await state.get_data()
    u=await user(session,c.from_user.id,c.from_user.username,c.from_user.first_name); u.phone=d["phone"]
    o=await create_order(session,u,d,items,config.delivery_price); cart_service.clear(c.from_user.id); await state.clear()
    await c.message.edit_text(f"✅ <b>Заказ #{o.id} создан!</b>\nСумма: {money(o.total,config.currency)}")
    for aid in config.admin_ids:
        try: await bot.send_message(aid,f"🔔 <b>Новый заказ #{o.id}</b>\n\n{order_text(o,config.currency)}")
        except Exception: pass
    await c.answer("Заказ создан")

@router.callback_query(F.data=="cancel_checkout")
async def cancel(c,state): await state.clear(); await c.message.edit_text("Оформление отменено."); await c.answer()

@router.message(F.text.in_({"📦 Мои заказы","/orders"}))
async def my_orders(m,session,config):
    u=await user(session,m.from_user.id,m.from_user.username,m.from_user.first_name); os=await orders(session,u.id)
    if not os: await m.answer("📦 Заказов пока нет."); return
    for o in os[:10]: await m.answer(order_text(o,config.currency))
