from __future__ import annotations

import base64
import json
import os
import zlib
from datetime import UTC, datetime

import matplotlib.pyplot as plt
import numpy as np
import requests


class T8ApiClient:
    """
    Cliente mínimo para la API REST del T8.
    - Lee T8_HOST, T8_USER, T8_PASSWORD desde variables de entorno.
    - test_connection() devuelve (status_code, snippet_text).
    """

    def __init__( # Se le da versatilidad pudiendo poner distintas credenciales 
        self,
        host: str | None = None,
        user: str | None = None,
        password: str | None = None,
        timeout: int = 10, # Si falla, no se queda infinitamente bloqueado
        verify_ssl: bool = True,
    ) -> None:
        # Evitamos que añada una /
        self.host = (host or os.getenv("T8_HOST") or "").rstrip("/") 
        self.user = user or os.getenv("T8_USER")
        self.password = password or os.getenv("T8_PASSWORD")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        if not self.host or not self.user or not self.password:
            raise ValueError("Faltan variables: T8_HOST, T8_USER o T8_PASSWORD")

        self.auth = (self.user, self.password)
        self.headers = {"Accept": "application/json"}

    def test_connection(self) -> tuple[int, str]:
        """
        Hace GET al endpoint base (/rest) y devuelve (status_code, snippet_text).
        No lanza excepción por status != 200; devuelve el código para que el
        llamador lo compruebe.
        """
        url = self.host 
        resp = requests.get(url, auth=self.auth, headers=self.headers,
                            timeout=self.timeout, verify=self.verify_ssl)
        
        # Inspección de la conexión
        snippet = resp.text[:1000] if resp.text else ""
        return resp.status_code, snippet
    
    def list_waves(self, machine: str, point: str, mode: str
                   ) -> tuple[list[str], list[str]]:
        """
        Devuelve la lista de URLs completas de las ondas disponibles para
        una combinación específica de máquina, punto y modo de procesamiento.

        Parámetros:
            machine (str): Nombre de la máquina.
            point (str): Punto de medición.
            mode (str): Modo de procesamiento (por ejemplo, 'AM1').

        Devuelve:
            list[str]: Lista de URLs completas de cada onda disponible.
                    Cada URL puede usarse para descargar la onda correspondiente.
        """

        # Construimos la URL del endpoint de la API para esta máquina/punto/modo
        url = f"{self.host}/waves/{machine}/{point}/{mode}"

        resp = requests.get(  # Hacemos la petición
            url,
            auth=self.auth,
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify_ssl
        )

        if resp.status_code != 200: # Evitamos errores
            print(f"Error {resp.status_code}: {resp.text[:200]}")
            return [], []

        body = resp.json()
        
        urls = []
        timestamps = []
        iso_timestamps = []
        # Recorremos cada elemento de '_items', que representa una onda individual
        for item in body.get("_items", []): # Si no existe se devuelve lista vacía
            # Entramos en links y self
            url_self = item.get("_links", {}).get("self") 

            if url_self: # Si la URL tiene algún valor se añade a la lista
                urls.append(url_self)

                timestamp = url_self.rstrip("/").split("/")[-1]

                timestamps.append(timestamp)

                iso_val = self.epoch_to_iso(timestamp)
                iso_timestamps.append(iso_val)

        return timestamps, iso_timestamps
    
    def epoch_to_iso(self, epoch_str: str) -> str:
        """
        Convierte un timestamp en formato epoch (segundos desde 01-01-1970 UTC)
        a formato ISO 8601 (ejemplo: '2019-04-10T12:08:44 UTC').

        Parámetros:
            epoch_str (str): Timestamp en formato epoch (por ejemplo '1554907724').

        Devuelve:
            str: Fecha y hora en formato ISO 8601 (UTC).
        """
        try:
            epoch_int = int(epoch_str)
            dt = datetime.fromtimestamp(epoch_int, tz=UTC)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            return ""
        
    def iso_to_epoch(self, iso_str: str) -> str:
        """
        Convierte una fecha ISO 8601 (ej. '2019-04-10T12:08:44')
        a un timestamp epoch (segundos desde 01-01-1970 UTC).

        Parámetros:
            iso_str (str): Fecha en formato ISO 8601.

        Devuelve:
            str: Timestamp en formato epoch (UTC).
        """
        try:
            dt = datetime.fromisoformat(iso_str)
            return str(int(dt.replace(tzinfo=UTC).timestamp()))
        except (ValueError, TypeError):
            return ""

    
    def get_wave(
        self,
        machine: str,
        point: str,
        mode: str,
        timestamp: str | None = None,
    ) -> dict | None:
        """
        Descarga una onda específica desde la API y la guarda en 'data/waves/'.

        Args:
            machine (str): Nombre de la máquina.
            point (str): Punto de medición.
            mode (str): Modo de procesamiento (por ejemplo 'AM1').
            timestamp (str): Marca de tiempo de la onda (en formato epoch).

        Returns:
            dict | None: Contenido de la onda si se descargó correctamente,
            o None si hubo un error.
        """
        # Si no se especifica timestamp → última onda
        if not timestamp:
            timestamp = "0"
        
        # Se puede pasar también ISO 8601 en el timestamp
        if "T" in timestamp or "-" in timestamp:
            timestamp = self.iso_to_epoch(timestamp)

        url = f"{self.host}/waves/{machine}/{point}/{mode}/{timestamp}"

        # Petición
        resp = requests.get(
            url,
            auth=self.auth,
            headers=self.headers,
            timeout=self.timeout,
            verify=self.verify_ssl,
        )

        if resp.status_code != 200:
            print(f"Error {resp.status_code}: {resp.text[:200]}")
            return None
        
        wave_data = resp.json()

        # Si se pidió la última onda (timestamp=0), extraer el timestamp real
        if timestamp == "0":
            urls, _ = self.list_waves(machine, point, mode)
            last_real_url = urls[-2]
            timestamp = last_real_url.rstrip("/").split("/")[-1]

        # Ruta de guardado
        save_path = f"data/waves/{machine}_{point}_{mode}_{timestamp}.json"

        # Guardar el JSON en archivo
        with open(save_path, "w", encoding="utf-8") as file:
            json.dump(wave_data, file, ensure_ascii=False, indent=2)

        print(f"Onda guardada en: {save_path}")
        return wave_data
    
    def plot_wave(self, file_path: str) -> None:
        """
        Genera un gráfico de la onda almacenada en un archivo JSON.

        Parámetros:
            file_path (str): Ruta del archivo JSON que contiene la onda.
        """
        with open(file_path, encoding="utf-8") as f:
            wave = json.load(f)

        # Decodificar base64
        compressed = base64.b64decode(wave["data"])

        # Descomprimir con zlib
        raw_bytes = zlib.decompress(compressed)

        # Convertir a int16
        signal = np.frombuffer(raw_bytes, dtype=np.int16)

        # Aplicar factor de escala
        signal = signal * wave.get("factor", 1.0)

        # Crear eje temporal
        fs = wave.get("sample_rate", 1)
        duration = len(signal) / fs
        time = np.linspace(0, duration, len(signal))

        plt.figure(figsize=(10, 4))
        plt.plot(time, signal)
        plt.xlabel("Tiempo (s)")
        plt.ylabel("Amplitud")
        plt.title(wave.get("path", "Onda desconocida"))
        plt.grid(True)
        plt.tight_layout()
        plt.show()