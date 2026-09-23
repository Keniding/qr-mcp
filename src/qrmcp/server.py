import io
import re
from typing import Annotated

import qrcode
from fastmcp import Context, FastMCP
from fastmcp.apps.config import UI_EXTENSION_ID
from fastmcp.exceptions import ToolError
from fastmcp.utilities.types import Image
from mcp.types import ToolAnnotations
from prefab_ui.components import Column, Heading, Image as PrefabImage, Link, Text
from pydantic import Field
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import RoundedModuleDrawer

mcp = FastMCP(
    "qr",
    instructions=(
        "Genera códigos QR con estilo a partir de un link. No requiere base "
        "de datos ni credenciales; cualquiera puede usarlo."
    ),
    mask_error_details=True,
)

HEX_COLOR = re.compile(r"^#?[0-9a-fA-F]{6}$")


def _hex_a_rgb(valor: str, nombre_campo: str) -> tuple[int, int, int]:
    if not HEX_COLOR.match(valor):
        raise ToolError(
            f"'{valor}' no es un color hexadecimal válido para {nombre_campo}. "
            "Usa el formato #RRGGBB, por ejemplo #0F172A."
        )
    hexadecimal = valor.lstrip("#")
    return tuple(int(hexadecimal[i : i + 2], 16) for i in (0, 2, 4))


def _normalizar_url(url: str) -> str:
    url = url.strip()
    if not url:
        raise ToolError("El link no puede estar vacío.")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = f"https://{url}"
    return url


def _generar_png(url: str, color_rgb: tuple[int, int, int], fondo_rgb: tuple[int, int, int]) -> bytes:
    qr = qrcode.QRCode(error_correction=ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)

    imagen = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(back_color=fondo_rgb, front_color=color_rgb),
    )

    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()


def construir_resultado(png_bytes: bytes, url: str, *, ui_soportada: bool):
    """Elige la representación del resultado según si el cliente conectado
    soporta la extensión MCP Apps (io.modelcontextprotocol/ui). Con soporte,
    se devuelve una tarjeta visible directamente en el chat; sin soporte, un
    ImageContent estándar, que todo cliente MCP sabe renderizar."""
    if ui_soportada:
        data_uri = Image(data=png_bytes, format="png").to_data_uri()
        return Column(
            gap=12,
            children=[
                Heading("Código QR", level=3),
                PrefabImage(src=data_uri, alt=f"Código QR para {url}", width="280px"),
                Text(Link(url, href=url)),
            ],
        )
    return Image(data=png_bytes, format="png")


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
def generar_qr(
    ctx: Context,
    link: Annotated[str, Field(description="El link o texto a codificar en el QR.")],
    color: Annotated[
        str, Field(description="Color de los módulos del QR, en hexadecimal (#RRGGBB).")
    ] = "#0F172A",
    fondo: Annotated[
        str, Field(description="Color de fondo del QR, en hexadecimal (#RRGGBB).")
    ] = "#FFFFFF",
):
    """Genera un código QR con estilo (módulos redondeados) a partir de un
    link y lo muestra directamente en el chat. Úsala cuando te pidan un QR
    para una URL, un enlace de pago, una tarjeta de contacto, etc."""
    url = _normalizar_url(link)
    color_rgb = _hex_a_rgb(color, "color")
    fondo_rgb = _hex_a_rgb(fondo, "fondo")
    png_bytes = _generar_png(url, color_rgb, fondo_rgb)
    ui_soportada = ctx.client_supports_extension(UI_EXTENSION_ID)
    return construir_resultado(png_bytes, url, ui_soportada=ui_soportada)
