from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from .models import User, Pizza, Order, OrderItem

async def user(session,tid,username,first_name):
    r=await session.execute(select(User).where(User.telegram_id==tid)); u=r.scalar_one_or_none()
    if not u:
        u=User(telegram_id=tid,username=username,first_name=first_name); session.add(u)
    else:
        u.username=username; u.first_name=first_name
    await session.commit(); return u

async def pizzas(session):
    r=await session.execute(select(Pizza).where(Pizza.active.is_(True)).order_by(Pizza.id)); return list(r.scalars())

async def pizza(session,pid):
    r=await session.execute(select(Pizza).where(Pizza.id==pid,Pizza.active.is_(True))); return r.scalar_one_or_none()

async def create_order(session,u,data,items,delivery):
    subtotal=sum(x["unit_price"]*x["quantity"] for x in items)
    o=Order(user_id=u.id,customer_name=data["name"],phone=data["phone"],address=data["address"],
            comment=data.get("comment"),payment_method=data["payment"],subtotal=subtotal,
            delivery_price=delivery,total=subtotal+delivery)
    session.add(o); await session.flush()
    for x in items:
        session.add(OrderItem(order_id=o.id,pizza_id=x["pizza_id"],pizza_name=x["name"],size=x["size"],
                              quantity=x["quantity"],unit_price=x["unit_price"]))
    await session.commit(); await session.refresh(o); return o

async def orders(session,uid):
    r=await session.execute(select(Order).where(Order.user_id==uid).options(selectinload(Order.items)).order_by(Order.created_at.desc()))
    return list(r.scalars())
