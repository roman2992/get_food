from sqlalchemy import select
from .models import Pizza

DATA=[
("Маргарита","Томатный соус, моцарелла, базилик",450,590,750),
("Пепперони","Томатный соус, моцарелла, пепперони",520,690,850),
("Четыре сыра","Моцарелла, дорблю, пармезан, чеддер",550,720,890),
("Гавайская","Моцарелла, ветчина, ананас",500,650,810),
("Мясочелло","Томатный соус, моцарелла, мясная начинка",500,650,810),
]

async def seed(session):
    r=await session.execute(select(Pizza).limit(1))
    if r.scalar_one_or_none(): return
    for n,d,p25,p30,p35 in DATA: session.add(Pizza(name=n,description=d,price_25=p25,price_30=p30,price_35=p35))
    await session.commit()
