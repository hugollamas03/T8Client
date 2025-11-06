from __future__ import annotations

import os
from typing import Any

import click
from dotenv import load_dotenv

from t8_client.api import T8ApiClient

load_dotenv()

CONTEXT_SETTINGS: dict[str, Any] = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--host",
    envvar="T8_HOST",
    help="URL base de la API del T8.",
)
@click.option(
    "--user",
    envvar="T8_USER",
    help="Usuario de la API del T8",
)
@click.option(
    "--password",
    envvar="T8_PASSWORD",
    help="Contraseña de la API del T8",
)
@click.option(
    "--timeout",
    default=10,
    show_default=True,
    help="Timeout en segundos para peticiones.",
)
@click.option(
    "--no-verify-ssl",
    is_flag=True,
    default=False,
    help="Desactivar verificación SSL.",
)
@click.pass_context
def cli(
    ctx: click.Context,
    host: str | None,
    user: str | None,
    password: str | None,
    timeout: int,
    no_verify_ssl: bool,
) -> None:
    """
    t8-client: CLI para interactuar con la API del T8.
    Las credenciales pueden provenir de variables de entorno o de .env.
    """
    host = host or os.getenv("T8_HOST")
    user = user or os.getenv("T8_USER")
    password = password or os.getenv("T8_PASSWORD")

    if not host or not user or not password:
        click.echo(
            "Aviso: falta T8_HOST, T8_USER o T8_PASSWORD. "
            "Puedes pasarlos con --host/--user/--password."
        )

    client: T8ApiClient = T8ApiClient(
        host=host,
        user=user,
        password=password,
        timeout=timeout,
        verify_ssl=not no_verify_ssl,
    )
    ctx.obj = {"client": client}


@cli.command("list-waves")
@click.option(
    "--machine",
    "-M",
    required=True,
    help="Nombre de la máquina (ej. LP_Turbine).",
)
@click.option(
    "--point",
    "-p",
    required=True,
    help="Punto de medida (ej. MAD31CY005).",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    help="Modo de procesamiento (ej. AM1).",
)
@click.option(
    "--iso/--epoch",
    default=None,
    help=(
        "Controla el formato de tiempo mostrado: "
        "--iso muestra solo timestamps ISO 8601, "
        "--epoch muestra solo timestamps epoch, "
        "y si no se indica, se muestran ambos."
    ),
)
@click.pass_context
def list_waves(
    ctx: click.Context,
    machine: str,
    point: str,
    mode: str,
    iso: bool,
) -> None:
    """
    Lista las ondas disponibles para (MACHINE, POINT, MODE).
    Imprime una lista de timestamps.
    """
    client: T8ApiClient = ctx.obj["client"]

    try:
        timestamps, iso_timestamps = client.list_waves(machine, point, mode)

        if not timestamps:
            click.echo("No se encontraron ondas.")
            return

        if iso is True:
            # Solo ISO
            click.echo("ISO 8601")
            click.echo("-" * 25)
            for iso_ts in iso_timestamps:
                click.echo(iso_ts)

        elif iso is False:
            # Solo epoch
            click.echo("EPOCH")
            click.echo("-" * 15)
            for ts in timestamps:
                click.echo(ts)
        else:
            # Ambos (por defecto)
            click.echo(f"{'EPOCH':<15} | ISO 8601")
            click.echo("-" * 40)
            for ts, iso_ts in zip(timestamps, iso_timestamps, strict=True):
                click.echo(f"{ts:<15} | {iso_ts}")

    except Exception as exc:  
        click.echo(f"Error al listar ondas: {exc}", err=True)
        raise click.ClickException("Fallo en list-waves (ver salida anterior)."
        ) from None
    
@cli.command("list-spectra")
@click.option(
    "--machine",
    "-M",
    required=True,
    help="Nombre de la máquina (ej. LP_Turbine).",
)
@click.option(
    "--point",
    "-p",
    required=True,
    help="Punto de medida (ej. MAD31CY005).",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    help="Modo de procesamiento (ej. AM1).",
)
@click.option(
    "--iso/--epoch",
    default=None,
       help=(
        "Controla el formato de tiempo mostrado: "
        "--iso muestra solo timestamps ISO 8601, "
        "--epoch muestra solo timestamps epoch, "
        "y si no se indica, se muestran ambos."
    ),
)
@click.pass_context
def list_spectra(
    ctx: click.Context,
    machine: str,
    point: str,
    mode: str,
    iso: bool,
) -> None:
    """
    Lista los espectros disponibles para (MACHINE, POINT, MODE).
    Imprime una lista de timestamps.
    """
    client: T8ApiClient = ctx.obj["client"]

    try:
        timestamps, iso_timestamps = client.list_spectra(machine, point, mode)

        if not timestamps:
            click.echo("No se encontraron espectros.")
            return

        if iso is True:
            # Solo ISO
            click.echo("ISO 8601")
            click.echo("-" * 25)
            for iso_ts in iso_timestamps:
                click.echo(iso_ts)

        elif iso is False:
            # Solo epoch
            click.echo("EPOCH")
            click.echo("-" * 15)
            for ts in timestamps:
                click.echo(ts)
        else:
            # Ambos (por defecto)
            click.echo(f"{'EPOCH':<15} | ISO 8601")
            click.echo("-" * 40)
            for ts, iso_ts in zip(timestamps, iso_timestamps, strict=True):
                click.echo(f"{ts:<15} | {iso_ts}")

    except Exception as exc:  
        click.echo(f"Error al listar espectros: {exc}", err=True)
        raise click.ClickException("Fallo en list-spectra (ver salida anterior)."
        ) from None

@cli.command("get-wave")
@click.option(
    "--machine",
    "-M",
    required=True,
    help="Nombre de la máquina (ej. LP_Turbine).",
)
@click.option(
    "--point",
    "-p",
    required=True,
    help="Punto de medida (ej. MAD31CY005).",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    help="Modo de procesamiento (ej. AM1).",
)
@click.option(
    "--datetime",
    "-d",
    "dt_iso",
    required=False,
    help="Fecha/hora en ISO 8601 (ej. 2019-04-11T18:25:54).",
)
@click.option(
    "--timestamp",
    "-t",
    "ts_epoch",
    required=False,
    help="Timestamp en formato epoch (segundos desde 1970).",
)
@click.pass_context
def get_wave(
    ctx: click.Context,
    machine: str,
    point: str,
    mode: str,
    dt_iso: str | None,
    ts_epoch: str | None,
) -> None:
    """
    Descarga una onda del T8 y la guarda en data/waves/.
    - Usar -d DATETIME (ISO) o -t TIMESTAMP (epoch) para seleccionar una onda concreta.
    - Si no se especifica, se descargará la última disponible.
    """
    client: T8ApiClient = ctx.obj["client"]

    # ---- Validación de exclusividad: -d y -t no pueden usarse a la vez ----
    if dt_iso and ts_epoch:
        raise click.ClickException("Especifique sólo una de las opciones "
        "-d/--datetime o -t/--timestamp.")
    
    timestamp_to_use: str | None = dt_iso or ts_epoch or None

    try:
        wave_data = client.get_wave(machine=machine, point=point, mode=mode, 
                                    timestamp=timestamp_to_use)
        if wave_data is None:
            raise click.ClickException("No se pudo descargar la onda "
            "(ver salida previa).")
        
    except click.ClickException:
        raise

    except Exception as exc:
        click.echo(f"Error al ejecutar get-wave: {exc}", err=True)
        raise click.ClickException("Fallo en get-wave (ver salida anterior).") from None
    
@cli.command("get-spectrum")
@click.option(
    "--machine",
    "-M",
    required=True,
    help="Nombre de la máquina (ej. LP_Turbine).",
)
@click.option(
    "--point",
    "-p",
    required=True,
    help="Punto de medida (ej. MAD31CY005).",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    help="Modo de procesamiento (ej. AM1).",
)
@click.option(
    "--datetime",
    "-d",
    "dt_iso",
    required=False,
    help="Fecha/hora en ISO 8601 (ej. 2019-04-11T18:25:54).",
)
@click.option(
    "--timestamp",
    "-t",
    "ts_epoch",
    required=False,
    help="Timestamp en formato epoch (segundos desde 1970).",
)
@click.pass_context
def get_spectrum(
    ctx: click.Context,
    machine: str,
    point: str,
    mode: str,
    dt_iso: str | None,
    ts_epoch: str | None,
) -> None:
    """
    Descarga un espectro del T8 y la guarda en data/spectra/.
    - Usar -d DATETIME (ISO) o -t TIMESTAMP (epoch) para seleccionar
      un espectro concreto.
    - Si no se especifica, se descargará el último disponible.
    """
    client: T8ApiClient = ctx.obj["client"]

    # ---- Validación de exclusividad: -d y -t no pueden usarse a la vez ----
    if dt_iso and ts_epoch:
        raise click.ClickException("Especifique sólo una de las opciones "
        "-d/--datetime o -t/--timestamp.")
    
    timestamp_to_use: str | None = dt_iso or ts_epoch or None

    try:
        wave_data = client.get_spectrum(machine=machine, point=point, mode=mode, 
                                    timestamp=timestamp_to_use)
        if wave_data is None:
            raise click.ClickException("No se pudo descargar el espectro"
            "(ver salida previa).")
        
    except click.ClickException:
        raise

    except Exception as exc:
        click.echo(f"Error al ejecutar get-spectra: {exc}", err=True)
        raise click.ClickException("Fallo en get-spectra (ver salida anterior" \
        ").") from None
    
@cli.command("plot-wave")
@click.option(
    "--machine",
    "-M",
    required=True,
    help="Nombre de la máquina (ej. LP_Turbine).",
)
@click.option(
    "--point",
    "-p",
    required=True,
    help="Punto de medida (ej. MAD31CY005).",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    help="Modo de procesamiento (ej. AM1).",
)
@click.option(
    "--datetime",
    "-d",
    "dt_iso",
    required=False,
    help="Fecha/hora en ISO 8601 (ej. 2019-04-11T18:25:54).",
)
@click.option(
    "--timestamp",
    "-t",
    "ts_epoch",
    required=False,
    help="Timestamp en formato epoch (segundos desde 1970).",
)
@click.pass_context
def plot_wave(
    ctx: click.Context,
    machine: str,
    point: str,
    mode: str,
    dt_iso: str | None,
    ts_epoch: str | None,
) -> None:
    """
    Representa y/o guarda una onda previamente descargada.

    - Usar -d DATETIME (ISO) o -t TIMESTAMP (epoch) para seleccionar una onda.
    - Si no se especifica, se usará la última disponible.
    """
    client: T8ApiClient = ctx.obj["client"]

    if dt_iso and ts_epoch:
        raise click.ClickException(
            "Especifique solo una de las opciones -d/--datetime o -t/--timestamp."
        )

    if dt_iso:
        ts_epoch = str(client.iso_to_epoch(dt_iso))

    if not (dt_iso or ts_epoch):
        urls, _ = client.list_waves(machine, point, mode)
        if not urls:
            raise click.ClickException("No hay ondas disponibles.")
        last_ts = urls[-1].rstrip("/").split("/")[-1]
        ts_epoch = last_ts

    timestamp_to_use = ts_epoch or "0"
    file_path = f"data/waves/{machine}_{point}_{mode}_{timestamp_to_use}.json"

    if not os.path.exists(file_path):
        raise click.ClickException(f"No se encontró el archivo: {file_path}")

    try:
        click.echo(f"Graficando onda desde {file_path}...")
        client.plot_wave(file_path)

    except Exception as exc:
        click.echo(f"Error al ejecutar plot-wave: {exc}", err=True)
        raise click.ClickException(
            "Fallo en plot-wave (ver salida anterior)."
        ) from None
    
@cli.command("plot-spectrum")
@click.option(
    "--machine",
    "-M",
    required=True,
    help="Nombre de la máquina (ej. LP_Turbine).",
)
@click.option(
    "--point",
    "-p",
    required=True,
    help="Punto de medida (ej. MAD31CY005).",
)
@click.option(
    "--mode",
    "-m",
    required=True,
    help="Modo de procesamiento (ej. AM1).",
)
@click.option(
    "--datetime",
    "-d",
    "dt_iso",
    required=False,
    help="Fecha/hora en ISO 8601 (ej. 2019-04-11T18:25:54).",
)
@click.option(
    "--timestamp",
    "-t",
    "ts_epoch",
    required=False,
    help="Timestamp en formato epoch (segundos desde 1970).",
)
@click.pass_context
def plot_spectrum(
    ctx: click.Context,
    machine: str,
    point: str,
    mode: str,
    dt_iso: str | None,
    ts_epoch: str | None,
) -> None:
    """
    Representa y/o guarda un espectro previamente descargado.

    - Usar -d DATETIME (ISO) o -t TIMESTAMP (epoch) para seleccionar una onda.
    - Si no se especifica, se usará la última disponible.
    """
    client: T8ApiClient = ctx.obj["client"]

    if dt_iso and ts_epoch:
        raise click.ClickException(
            "Especifique solo una de las opciones -d/--datetime o -t/--timestamp."
        )

    if dt_iso:
        ts_epoch = str(client.iso_to_epoch(dt_iso))

    if not (dt_iso or ts_epoch):
        urls, _ = client.list_spectra(machine, point, mode)
        if not urls:
            raise click.ClickException("No hay espectros disponibles.")
        last_ts = urls[-1].rstrip("/").split("/")[-1]
        ts_epoch = last_ts

    timestamp_to_use = ts_epoch or "0"
    file_path = f"data/spectra/{machine}_{point}_{mode}_{timestamp_to_use}.json"

    if not os.path.exists(file_path):
        raise click.ClickException(f"No se encontró el archivo: {file_path}")

    try:
        click.echo(f"Graficando espectro desde {file_path}...")
        client.plot_spectrum(file_path)

    except Exception as exc:
        click.echo(f"Error al ejecutar plot-spectrum: {exc}", err=True)
        raise click.ClickException(
            "Fallo en plot-spectrum (ver salida anterior)."
        ) from None

@cli.command("compute-spectrum")
@click.option("-w", "--wave-file", required=True, type=click.Path(exists=True), help="Archivo de onda descargado (.json)")
@click.option("--fmin", required=True, type=float, help="Frecuencia mínima de interés (Hz)")
@click.option("--fmax", required=True, type=float, help="Frecuencia máxima de interés (Hz)")
def compute_spectrum_cmd(wave_file, fmin, fmax):
    """Calcula el espectro de una onda dada."""
    client = T8ApiClient()
    client.compute_spectrum(wave_file, fmin, fmax)


if __name__ == "__main__":
    cli()
