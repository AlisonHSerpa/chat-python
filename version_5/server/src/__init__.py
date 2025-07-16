from .model.server_model import ServerModel
from .controller.server_controller import ServerController

def create_server():
    controller = ServerController()
    return controller