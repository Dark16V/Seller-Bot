from .order import OrderManager
from .proxy import ProxyManager
from .user import UserManager
from .category import CatManager

class DbManager(OrderManager, ProxyManager, UserManager, CatManager):
    def __init__(self, session_maker):
        super().__init__(session_maker)