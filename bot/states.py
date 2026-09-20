from aiogram.fsm.state import State, StatesGroup
class Checkout(StatesGroup):
    name=State(); phone=State(); address=State(); comment=State(); payment=State(); confirm=State()
