from .order import OrderManager
from .proxy import ProxyManager
from .user import UserManager
from .category import CatManager
from .promocode import PromoCodeManager

class DbManager(OrderManager, ProxyManager, UserManager, CatManager, PromoCodeManager):
    def __init__(self, session_maker):
        super().__init__(session_maker)