from .start import StartMenu
from .proxy import ProxyClient
from .instrucions import InstructionsClient
from .servers import ServerClient
from .vpn import VPNClient
from .orders import OrdersClient


user_modules = [StartMenu, ProxyClient, InstructionsClient, ServerClient, VPNClient, OrdersClient]


__all__ = ['user_modules']