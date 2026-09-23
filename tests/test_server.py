from fastmcp import Client
from fastmcp.apps.config import UI_EXTENSION_ID
from fastmcp.client.client import ClientExtension

from qrmcp.server import mcp


class _UIExtension(ClientExtension):
    """Declara soporte de la extensión MCP Apps, como haría un cliente capaz."""

    identifier = UI_EXTENSION_ID


async def test_generar_qr_sin_soporte_ui_devuelve_imagen_estandar():
    async with Client(mcp) as client:
        result = await client.call_tool("generar_qr", {"link": "https://claude.com"})
    assert not result.is_error
    assert len(result.content) == 1
    bloque = result.content[0]
    assert bloque.type == "image"
    assert bloque.mime_type == "image/png"
    assert result.structured_content is None


async def test_generar_qr_con_soporte_ui_devuelve_tarjeta():
    async with Client(mcp, extensions=[_UIExtension()]) as client:
        result = await client.call_tool("generar_qr", {"link": "https://claude.com"})
    assert not result.is_error
    vista = result.structured_content["view"]
    assert "data:image/png;base64," in str(vista)


async def test_generar_qr_agrega_https_si_falta_esquema():
    async with Client(mcp) as client:
        result = await client.call_tool("generar_qr", {"link": "claude.com"})
    assert not result.is_error


async def test_generar_qr_colores_personalizados():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generar_qr",
            {"link": "https://claude.com", "color": "#FF0000", "fondo": "#000000"},
        )
    assert not result.is_error


async def test_generar_qr_color_invalido_rechazado():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generar_qr",
            {"link": "https://claude.com", "color": "no-es-un-color"},
            raise_on_error=False,
        )
    assert result.is_error


async def test_generar_qr_link_vacio_rechazado():
    async with Client(mcp) as client:
        result = await client.call_tool(
            "generar_qr", {"link": "   "}, raise_on_error=False
        )
    assert result.is_error
