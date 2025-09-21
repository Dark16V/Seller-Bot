from .admin_client import AdminyIBK
from .user_client import UserIBK
from .pay_client import PayIBK


class IBK(AdminyIBK, UserIBK, PayIBK):
    pass