from __future__ import annotations # Esto tengo que mirar bien para que sirve, es una buena práctica se supone
import os
from typing import Optional, Tuple
import requests

class T8ApiClient:
    """
    Cliente mínimo para la API REST del T8.
    - Lee T8_HOST, T8_USER, T8_PASSWORD desde variables de entorno.
    - test_connection() devuelve (status_code, snippet_text).
    """

    def __init__( # Se le da versatilidad pudiendo poner distintas credenciales y no solo llamando al .env
        self,
        host: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 10, # Si falla, no se queda infinitamente bloqueado
        verify_ssl: bool = True,
    ) -> None:
        self.host = (host or os.getenv("T8_HOST") or "").rstrip("/") # Evitamos que añada una /
        self.user = user or os.getenv("T8_USER")
        self.password = password or os.getenv("T8_PASSWORD")
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        if not self.host or not self.user or not self.password:
            raise ValueError("Faltan variables: T8_HOST, T8_USER o T8_PASSWORD")

        self.auth = (self.user, self.password)
        self.headers = {"Accept": "application/json"}

    def test_connection(self) -> Tuple[int, str]:
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
