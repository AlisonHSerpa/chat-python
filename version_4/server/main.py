from threading import Thread
from src import create_server

def main():
    # Cria e configura o servidor
    model, controller = create_server()
    model.initialize_server()
    
    # Inicia thread para checar as conexoes ativas e enviar lista de usuarios
    Thread(target=controller.list_online_users, daemon=True).start()
    
    # Inicia loop principal de conexoes
    controller.connection_request_loop()

if __name__ == "__main__":
    main()