from fastmcp import Client

from qrmcp.server import mcp


async def test_generar_qr_devuelve_tarjeta_con_imagen():
    async with Client(mcp) as client:
        result = await client.call_tool("generar_qr", {"link": "https://claude.com"})
    assert not result.is_error
    vista = result.structured_content["view"]
    assert vista["type"] == "Div"
    # La imagen debe ir embebida como data URI PNG, visible sin expandir nada.
    contenido = str(vista)
    assert "data:image/png;base64," in contenido


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
