from aiogram.fsm.state import StatesGroup, State

class Register(StatesGroup):
    email = State()
    password = State()

class Login(StatesGroup):
    email = State()
    password = State()