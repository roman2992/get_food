from aiogram.types import ReplyKeyboardMarkup,KeyboardButton,InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🍕 Меню"),KeyboardButton(text="🛒 Корзина")],
                                          [KeyboardButton(text="📦 Мои заказы")]],resize_keyboard=True)

def pizzas_menu(items):
    b=InlineKeyboardBuilder()
    for p in items: b.button(text=p.name,callback_data=f"pizza:{p.id}")
    b.adjust(1); return b.as_markup()

def sizes(pid):
    b=InlineKeyboardBuilder()
    for s in (25,30,35): b.button(text=f"{s} см",callback_data=f"size:{pid}:{s}")
    b.button(text="⬅️ Меню",callback_data="menu"); b.adjust(3,1); return b.as_markup()

def qty(pid,size):
    b=InlineKeyboardBuilder()
    for q in (1,2,3,4,5): b.button(text=str(q),callback_data=f"qty:{pid}:{size}:{q}")
    b.adjust(5); return b.as_markup()

def cart(items):
    b=InlineKeyboardBuilder()
    for x in items:
        b.button(text=f"➖ {x['name']} {x['size']}см",callback_data=f"dec:{x['key']}")
        b.button(text=f"➕ {x['name']} {x['size']}см",callback_data=f"inc:{x['key']}")
    if items: b.button(text="🗑 Очистить",callback_data="clear_cart"); b.button(text="✅ Оформить",callback_data="checkout")
    b.adjust(2); return b.as_markup() if items else None

def payment():
    b=InlineKeyboardBuilder(); b.button(text="💵 Наличными",callback_data="pay:cash"); b.button(text="💳 Картой курьеру",callback_data="pay:card"); b.adjust(1); return b.as_markup()

def confirm():
    b=InlineKeyboardBuilder(); b.button(text="✅ Подтвердить",callback_data="confirm"); b.button(text="❌ Отмена",callback_data="cancel_checkout"); b.adjust(1); return b.as_markup()

def admin(order_id,status):
    b=InlineKeyboardBuilder()
    nexts={"new":("✅ Принять","accepted"),"accepted":("👨‍🍳 Готовить","cooking"),"cooking":("🚚 Курьеру","delivery"),"delivery":("🏁 Доставлен","completed")}
    if status in nexts: b.button(text=nexts[status][0],callback_data=f"status:{order_id}:{nexts[status][1]}")
    if status not in ("completed","cancelled"): b.button(text="❌ Отменить",callback_data=f"status:{order_id}:cancelled")
    b.adjust(1); return b.as_markup()
