import os

from dotenv import load_dotenv

from t8_client.api import T8ApiClient

load_dotenv()

client = T8ApiClient(
    host=os.getenv("T8_HOST"),
    user=os.getenv("T8_USER"),
    password=os.getenv("T8_PASSWORD")
)

timestamp = "0" 

wave_data = client.get_spectra("LP_Turbine", "MAD31CY005", "AM1", timestamp)