from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from ..ui import main, pizzas_menu, qty, cart, payment, confirm
from ..text import money, cart_text, order_text
from ..repo import pizzas, pizza, user, create_order, orders
from ..states import Checkout
router = Router()
@router.message(Command("start"))
async def start(m: Message):
    await m.answer("🍕 <b>Добро пожаловать!</b>\n\nВыберите действие:", reply_markup=main())
@router.message(F.text.in_({"🍕 Меню", "/menu"}))
async def menu(m: Message, session):
    ps = await pizzas(session)
    text = "🍕 <b>Меню</b>\n\n" + "\n".join(f"<b>{p.name}</b> — {money(p.price_30, '₽')}\n{p.description}" for p in ps)
    await m.answer(text, reply_markup=pizzas_menu(ps))
@router.callback_query(F.data == "menu")
async def menu_cb(c, session):
    ps = await pizzas(session)

    text = (
        "🍕 <b>Меню</b>\n\n"
        + "\n".join(
            f"<b>{p.name}</b> — {money(p.price_30, '₽')}\n"
            f"{p.description}"
            for p in ps
        )
    )

    if c.message.photo:
        await c.message.delete()
        await c.message.answer(
            text,
            reply_markup=pizzas_menu(ps)
        )
    else:
        await c.message.edit_text(
            text,
            reply_markup=pizzas_menu(ps)
        )

    await c.answer()
@router.callback_query(F.data.startswith("pizza:"))
async def details(c, session, bot):
    p = await pizza(session, int(c.data.split(":")[1]))
    text = f"🍕 <b>{p.name}</b>\n\n{p.description}\n\nЦена: <b>{money(p.price_30, '₽')}</b>\n\nВыберите количество:"
    if p.image_file_id:
        await c.message.delete(); await bot.send_photo(chat_id=c.from_user.id, photo=p.image_file_id, caption=text, reply_markup=qty(p.id))
    else:
        await c.message.edit_text(text, reply_markup=qty(p.id))
    await c.answer()
@router.callback_query(F.data.startswith("qty:"))
async def qty_cb(c, session, cart_service):
    _, pid, q = c.data.split(":")
    p = await pizza(session, int(pid)); quantity = int(q); price = p.price_30
    cart_service.add(c.from_user.id, p.id, p.name, 30, price, quantity)
    text = f"✅ <b>{p.name}</b>\n\nДобавлено в корзину: {quantity} шт.\nЦена за штуку: {money(price, '₽')}\nСумма: {money(price * quantity, '₽')}"
    if c.message.photo:
        await c.message.edit_caption(caption=text, reply_markup=None)
    else:
        await c.message.edit_text(text, reply_markup=None)
    await c.answer("Добавлено в корзину")
@router.message(F.text.in_({"🛒 Корзина", "/cart"}))
async def cart_msg(m: Message, cart_service, config):
    items = cart_service.items(m.from_user.id)
    await m.answer(cart_text(items, config.currency, config.delivery_price), reply_markup=cart(items))
@router.callback_query(F.data.startswith(("inc:", "dec:")))
async def cart_change(c, cart_service, config):
    action, key = c.data.split(":", 1)
    (cart_service.inc if action == "inc" else cart_service.dec)(c.from_user.id, key)
    items = cart_service.items(c.from_user.id)
    await c.message.edit_text(cart_text(items, config.currency, config.delivery_price), reply_markup=cart(items)); await c.answer()
@router.callback_query(F.data == "clear_cart")
async def clear(c, cart_service):
    cart_service.clear(c.from_user.id); await c.message.edit_text("🛒 Корзина очищена."); await c.answer()
@router.callback_query(F.data == "checkout")
async def checkout(c, state, cart_service):
    if not cart_service.items(c.from_user.id): await c.answer("Корзина пуста", show_alert=True); return
    await state.set_state(Checkout.name); await c.message.edit_text("Введите имя получателя:"); await c.answer()
@router.message(Checkout.name)
async def name(m: Message, state):
    await state.update_data(name=m.text.strip()); await state.set_state(Checkout.phone); await m.answer("📞 Введите телефон:")
@router.message(Checkout.phone)
async def phone(m: Message, state):
    await state.update_data(phone=m.text.strip()); await state.set_state(Checkout.address); await m.answer("📍 Введите адрес доставки:")
@router.message(Checkout.address)
async def address(m: Message, state):
    await state.update_data(address=m.text.strip()); await state.set_state(Checkout.comment); await m.answer("💬 Комментарий или «нет»:")
@router.message(Checkout.comment)
async def comment(m: Message, state):
    await state.update_data(comment=None if m.text.strip().lower() == "нет" else m.text.strip()); await state.set_state(Checkout.payment); await m.answer("Выберите оплату:", reply_markup=payment())
@router.callback_query(Checkout.payment, F.data.startswith("pay:"))
async def pay(c, state, cart_service, config):
    payment_method = c.data.split(":")[1]
    await state.update_data(payment=payment_method, payment_name="Наличными" if payment_method == "cash" else "Картой курьеру")
    d = await state.get_data(); items = cart_service.items(c.from_user.id); await state.set_state(Checkout.confirm)
    await c.message.edit_text(f"🔎 <b>Проверьте заказ</b>\n\n👤 {d['name']}\n📞 {d['phone']}\n📍 {d['address']}\n💳 {d['payment_name']}\n\n{cart_text(items, config.currency, config.delivery_price)}", reply_markup=confirm()); await c.answer()
@router.callback_query(Checkout.confirm, F.data == "confirm")
async def confirm_order(c, state, session, cart_service, config, bot):
    items = cart_service.items(c.from_user.id); d = await state.get_data()
    u = await user(session, c.from_user.id, c.from_user.username, c.from_user.first_name); u.phone = d["phone"]
    o = await create_order(session, u, d, items, config.delivery_price); cart_service.clear(c.from_user.id); await state.clear()
    await c.message.edit_text(f"✅ <b>Заказ #{o.id} создан!</b>\nСумма: {money(o.total, config.currency)}")
    for aid in config.admin_ids:
        try: await bot.send_message(aid, f"🔔 <b>Новый заказ #{o.id}</b>\n\n{order_text(o, config.currency)}")
        except Exception: pass
    await c.answer("Заказ создан")
@router.callback_query(F.data == "cancel_checkout")
async def cancel(c, state):
    await state.clear(); await c.message.edit_text("Оформление отменено."); await c.answer()
@router.message(F.text.in_({"📦 Мои заказы", "/orders"}))
async def my_orders(m: Message, session, config):
    u = await user(session, m.from_user.id, m.from_user.username, m.from_user.first_name); os = await orders(session, u.id)
    if not os: await m.answer("📦 Заказов пока нет."); return
    for o in os[:10]: await m.answer(order_text(o, config.currency))


@router.message(F.photo)
async def get_photo_id(message: Message):
    photo = message.photo[-1]
    await message.answer(f"file_id:\n{photo.file_id}")