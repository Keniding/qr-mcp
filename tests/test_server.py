from fastmcp import Client

from qrmcp.server import mcp


async def test_generar_qr_devuelve_imagen_png():
    async with Client(mcp) as client:
        result = await client.call_tool("generar_qr", {"link": "https://claude.com"})
    assert not result.is_error
    assert len(result.content) == 1
    bloque = result.content[0]
    assert bloque.type == "image"
    assert bloque.mime_type == "image/png"


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
