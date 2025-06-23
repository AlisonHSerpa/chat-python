from threading import Thread
from servidor import create_server

def main():
    # Cria e configura o servidor
    model, controller = create_server()
    model.initialize_server()
    
    # Inicia thread para mensagens do servidor
    Thread(target=controller.server_message_loop, daemon=True).start()
    Thread(target=model.check_connections, daemon=True).start()
    
    # Inicia loop principal de conexões
    controller.connection_request_loop()

if __name__ == "__main__":
    main()