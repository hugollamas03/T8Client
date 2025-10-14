import os

from dotenv import load_dotenv

from t8_client.api import T8ApiClient

load_dotenv()  # carga las variables de .env

client = T8ApiClient(
    host=os.getenv("T8_HOST"),
    user=os.getenv("T8_USER"),
    password=os.getenv("T8_PASSWORD")
)

client = T8ApiClient()
client.plot_wave("data/waves/LP_Turbine_MAD31CY005_AM1_1554907724.json")

