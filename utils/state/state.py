from aiogram.fsm.state import State, StatesGroup



class UploadFile(StatesGroup):
    waiting_for_file = State()
    price = State()

class NumProx(StatesGroup):
    type = State()
    country = State()
    await_accept = State()
    number = State()


class Mailing(StatesGroup):
    message = State()

class IncBalance(StatesGroup):
    price = State()
    method = State()


class PaymentState(StatesGroup):
    AMOUNT = State()    
    WALLET = State()   
    COIN = State()   
    PAY_WAIT = State()    

class DeleteProxy(StatesGroup):
    ip = State()

class UsersState(StatesGroup):
    id = State()


class Prolong(StatesGroup):
    proxy_id: int = State()
    period: int = State()
    