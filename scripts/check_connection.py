import sys

from dotenv import load_dotenv

from t8_client.api import T8ApiClient

load_dotenv()  # Carga .env 

def main() -> None:
    # Se intenta crear el cliente
    try:
        client = T8ApiClient()
    except Exception as e:
        print("ERROR: no se pudo crear T8ApiClient:", e)
        sys.exit(1)

    # Se intenta hacer una petición de prueba
    try:
        status, snippet = client.test_connection()
        print("HTTP status code:", status)
        if snippet:
            print("Snippet (primeros 1000 caracteres):")
            print(snippet)
    except Exception as e:
        print("ERROR durante la petición:", type(e).__name__, e)
        sys.exit(2)

# Para ejecutar
if __name__ == "__main__":
    main()
