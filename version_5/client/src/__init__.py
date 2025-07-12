from .controller.client_controller import ClientController

def create_client():
    """Factory function para criar o cliente MVC"""
    return ClientController()