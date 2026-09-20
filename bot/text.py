STATUS={"new":"🆕 Новый","accepted":"✅ Принят","cooking":"👨‍🍳 Готовится","delivery":"🚚 У курьера","completed":"🏁 Доставлен","cancelled":"❌ Отменён"}
def money(v,c): return f"{v:,}".replace(","," ")+f" {c}"
def cart_text(items,currency,delivery):
    if not items:return "🛒 <b>Корзина пуста</b>"
    s=0; out=["🛒 <b>Корзина</b>",""]
    for x in items:
        t=x["unit_price"]*x["quantity"]; s+=t
        out.append(f"• {x['name']} {x['size']} см × {x['quantity']} — {money(t,currency)}")
    out += ["",f"Товары: {money(s,currency)}",f"Доставка: {money(delivery,currency)}",f"<b>Итого: {money(s+delivery,currency)}</b>"]
    return "\n".join(out)
def order_text(o,currency):
    out=[f"📦 <b>Заказ #{o.id}</b>",f"Статус: {STATUS.get(o.status,o.status)}",""]
    out += [f"• {x.pizza_name} {x.size} см × {x.quantity} — {money(x.unit_price*x.quantity,currency)}" for x in o.items]
    out += ["",f"<b>Итого: {money(o.total,currency)}</b>",f"📍 {o.address}",f"📞 {o.phone}"]
    return "\n".join(out)
