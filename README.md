# T8Client
Este repositorio contiene un cliente en Python para interactuar con la API del sistema T8. Permite obtener, procesar y visualizar formas de onda y espectros. Incluye una interfaz de línea de comandos (CLI) y varios scripts auxiliares que replican las funciones principales para facilitar el uso y la automatización.

---

## Descripción
T8Client está pensado para conectarse a la API del T8, descargar datos de espectros y formas de onda, procesarlos y generar gráficos o resultados numéricos.  
El objetivo es simplificar la interacción con el sistema desde Python, tanto de forma manual (CLI) como programática (scripts).

El proyecto está implementado en Python y usa **[uv](https://github.com/astral-sh/uv)** para la gestión de dependencias y entornos, sin necesidad de Poetry ni pip tradicional.

---

## Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/hugollamas03/T8Client.git
   cd T8Client

2. Instala las dependencias usando uv:
    ```bash
    uv sync
Esto creará el entorno virtual y descargará las dependencias definidas en el archivo pyproject.toml y bloqueadas en uv.lock.

3. Credenciales 

Antes de usar el cliente, define las credenciales y la dirección del host de la API mediante variables de entorno o un archivo .env en la raíz del proyecto.

Ejemplo de .env:

    
    USER=tu_usuario
    PASSW=tu_contraseña
    HOST=https://t8-api.ejemplo.com

Estas variables son utilizadas por la CLI y los scripts para autenticarse y conectarse a la API. También se da la flexibilidad de incluirlas en los comandos de la mayoría de funciones.

## Estructura del proyecto

    T8Client/
    ├── scripts/                 # Scripts auxiliares
    │   └── compare_spectra.py   # Script para comparar espectros
    ├── src/                     # Código fuente principal del cliente
    │   ├── api.py               # Módulo de conexión y autenticación con la API
    │   ├── cli.py               # Implementación de la interfaz de línea de comandos
    │   ├── spectrum.py          # Funciones para manejo de espectros
    │   └── __init__.py
    ├── pyproject.toml           # Configuración del proyecto y dependencias
    ├── uv.lock                  # Archivo de dependencias bloqueadas
    └── README.md

## Ejecucción del proyecto 

1. Ejecutar comandos desde la CLI

La interfaz de comandos cuenta con numerosos usos posibles, entre los que podemos listar, descargar y representa una onda u espectro, o acceder al script de comparar espectro que explicaré mas adelante en detalle.

Para ejecutar la CLI simplemente podemos poner en la terminal: 

    t8-client 

Con ello se nos dará acceso a toda la ayuda de los diferentes comandos y su modo de uso si seleccionamos uno de ellos así:

    t8-client comando --help

Los subcomandos disponibles y su modo de uso son, por tanto:

- Listar timestamps:
    ```bash
    t8-client list-waves -M <machine> -p <point> -m <pmode>
    t8-client list-spectra -M <machine> -p <point> -m <pmode>

- Descargar una onda/espectro con un timestamp concreto (todo el codigo funciona tanto en iso como en formato linux):
    ```bash
    t8-client get-wave -M <machine> -p <point> -m <pmode> -t <date>
    t8-client get-spectrum -M <machine> -p <point> -m <pmode> -t <date>

- Representar dichas descargas y guardarlas o no:
    ```bash
    t8-client plot-wave -M <machine> -p <point> -m <pmode> -t <date>
    t8-client plot-spectrum -M <machine> -p <point> -m <pmode> -t <date>

- Computar un espectro a partir de una onda descargada:
    ```bash
    t8-client compute-spectrum -w data/waves/LP_Turbine_MAD31CY005_AM1_1555119736.json ---fmin 0 --fmax 2000  

Se le pueden pasar como hemos visto diferentes credenciales al comando del t8-client.

2. Script de comparación de espectros

Este script compara y representa dos espectros, uno de ellos generado mediante un computo a partir de una descargada y el otro directamente descargado del T8. Para ejecutarlo debemos escribir:

    uv run python scripts/compare_spectra.py \
    --downloaded data/spectra/machine_point_mode_date.json \
    --computed data/spectra/machine_point_mode_date_computed.json

