import os

from dotenv import load_dotenv

from t8_client.api import T8ApiClient

load_dotenv()  # carga las variables de .env

client = T8ApiClient(
    host=os.getenv("T8_HOST"),
    user=os.getenv("T8_USER"),
    password=os.getenv("T8_PASSWORD")
)

timestamps, iso_timestamps = client.list_waves("LP_Turbine", "MAD31CY005", "AM1")

print("Número de ondas:", len(timestamps))
for e, i in zip(timestamps, iso_timestamps):
    print(f"{e} | {i}")


