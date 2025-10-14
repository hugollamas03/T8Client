import os

from dotenv import load_dotenv

from t8_client.api import T8ApiClient

load_dotenv()  # carga las variables de .env

client = T8ApiClient(
    host=os.getenv("T8_HOST"),
    user=os.getenv("T8_USER"),
    password=os.getenv("T8_PASSWORD")
)

machine = "LP_Turbine"
point = "MAD31CY005"
mode = "AM1"

timestamps, iso_timestamps = client.list_waves(machine, point, mode)

print(f"\nOndas disponibles para {machine}/{point}/{mode}:")
print(f"Total: {len(timestamps)}\n")

for epoch, iso in zip(timestamps, iso_timestamps, strict=True):
    print(f"{machine}/{point}/{mode}/{epoch}   |   {machine}/{point}/{mode}/{iso}")

