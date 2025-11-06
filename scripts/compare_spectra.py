import argparse
import base64
import json
import zlib
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt


def decode_array(raw_bytes):
    """Intenta decodificar un array binario probando varios tipos de datos."""
    for dtype in [np.float32, np.float64, np.int16]:
        if len(raw_bytes) % np.dtype(dtype).itemsize == 0:
            try:
                arr = np.frombuffer(raw_bytes, dtype=dtype)
                if arr.size > 0 and not np.all(arr == 0):
                    return arr.astype(float)
            except Exception:
                continue
    raise ValueError("No se pudo decodificar el array: formato desconocido")


def load_spectrum(path):
    """Carga un espectro (descargado o calculado) desde un JSON."""
    with open(path, "r") as f:
        data = json.load(f)

    # --- Caso 1: espectro descargado del T8 ---
    if "data" in data and "min_freq" in data and "max_freq" in data:
        raw = zlib.decompress(base64.b64decode(data["data"]))
        spectrum = decode_array(raw)

        # 🔧 Aplicar factor de escala (igual que en plot_spectrum)
        factor = data.get("factor", 1.0)
        spectrum = spectrum * factor

        fmin = data["min_freq"]
        fmax = data["max_freq"]
        n = len(spectrum)
        freqs = np.linspace(fmin, fmax, n)
        return freqs, spectrum

    # --- Caso 2: espectro calculado localmente ---
    elif "freqs" in data and "spectrum" in data:
        return np.array(data["freqs"]), np.array(data["spectrum"])

    else:
        raise KeyError(f"No se reconocen claves válidas de espectro en {path}")


def main():
    parser = argparse.ArgumentParser(description="Comparar espectros descargado y calculado")
    parser.add_argument("--downloaded", required=True, help="Ruta al espectro descargado (.json)")
    parser.add_argument("--computed", required=True, help="Ruta al espectro calculado (.json)")
    parser.add_argument("--save", help="Guardar figura en vez de mostrarla")
    args = parser.parse_args()

    freqs_d, spec_d = load_spectrum(args.downloaded)
    freqs_c, spec_c = load_spectrum(args.computed)

    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(freqs_d, spec_d)
    plt.title("Espectro descargado del T8")
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Magnitud")

    plt.subplot(2, 1, 2)
    plt.plot(freqs_c, spec_c, color="orange")
    plt.title("Espectro calculado localmente")
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Magnitud")

    plt.tight_layout()

    if args.save:
        Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(args.save, dpi=150)
        print(f"✅ Figura guardada en {args.save}")
    else:
        plt.show()


if __name__ == "__main__":
    main()

    
""" Uso: uv run python scripts/compare_spectra.py \
--downloaded data/spectra/LP_Turbine_MAD31CY005_AM1_1555119736.json \
  --computed data/spectra/LP_Turbine_MAD31CY005_AM1_1555119736_computed.json"""
