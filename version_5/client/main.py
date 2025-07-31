from src import create_client

if __name__ == "__main__":
    try:
        client = create_client()
        client.run()
    except ConnectionError as e:
        print(f"Encerrando aplicação: {e}")