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
    help="URL base del T8 (también desde T8_HOST).",
)
@click.option(
    "--user",
    envvar="T8_USER",
    help="Usuario T8 (también desde T8_USER).",
)
@click.option(
    "--password",
    envvar="T8_PASSWORD",
    help="Password T8 (también desde T8_PASSWORD).",
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
    t8-client: CLI para interactuar con el T8.
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
    default=True,
    help="Mostrar timestamps en ISO 8601 (por defecto) o epoch.",
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
    Imprime una lista de timestamps (ISO 8601 o epoch).
    """
    client: T8ApiClient = ctx.obj["client"]

    try:
        timestamps, iso_timestamps = client.list_waves(machine, point, mode)

        if not timestamps:
            click.echo("No se encontraron ondas.")
            return

        data_to_show = iso_timestamps if iso else timestamps
        for t in data_to_show:
            click.echo(t)

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
    default=True,
    help="Mostrar timestamps en ISO 8601 (por defecto) o epoch.",
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
    Imprime una lista de timestamps (ISO 8601 o epoch).
    """
    client: T8ApiClient = ctx.obj["client"]

    try:
        timestamps, iso_timestamps = client.list_spectra(machine, point, mode)

        if not timestamps:
            click.echo("No se encontraron espectros.")
            return

        data_to_show = iso_timestamps if iso else timestamps
        for t in data_to_show:
            click.echo(t)

    except Exception as exc:  
        click.echo(f"Error al listar espectros: {exc}", err=True)
        raise click.ClickException("Fallo en list-spectra (ver salida anterior)."
        ) from None


if __name__ == "__main__":
    cli()
