from .model.server_model import ServerModel
from .controller.server_controller import ServerController

def create_server():
    model = ServerModel()
    controller = ServerController(model)
    return model, controller