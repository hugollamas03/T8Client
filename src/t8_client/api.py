from __future__ import annotations

import os

import requests

from datetime import datetime, timezone


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
    
    def list_waves(self, machine: str, point: str, mode: str) -> tuple[list[str], list[str]]:
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

                if timestamp == "0": # Quitamos la última
                    continue

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
            dt = datetime.fromtimestamp(epoch_int, tz=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%S")
        except (ValueError, TypeError):
            return ""
    
