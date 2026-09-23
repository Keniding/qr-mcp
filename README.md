# qr-mcp

Servidor MCP mínimo: genera un código QR con estilo a partir de un link y lo
muestra como imagen en el chat. Sin base de datos, sin secretos, sin
autenticación — pensado para que cualquiera lo use libremente en una demo.

## Herramienta

| Herramienta | Entrada | Salida |
|---|---|---|
| `generar_qr` | `link: str`, `color: str = "#0F172A"`, `fondo: str = "#FFFFFF"` | Tarjeta con el QR, o imagen PNG (según el cliente) |

Si `link` no trae esquema (`http://`/`https://`), se le antepone `https://`
automáticamente. Los colores se validan como hexadecimal `#RRGGBB`.

### Cómo se muestra el QR en el chat

`generar_qr` detecta en tiempo real si el cliente MCP conectado soporta la
extensión **MCP Apps** (`io.modelcontextprotocol/ui`, SEP-2133) vía
`ctx.client_supports_extension(...)`:

- **Con soporte**: devuelve una tarjeta Prefab UI (imagen embebida como data
  URI + link) que se renderiza directamente en el chat, sin que el usuario
  tenga que expandir nada.
- **Sin soporte** (caso por defecto hoy con conectores remotos genéricos):
  devuelve un `ImageContent` estándar de MCP — el tipo de contenido que
  cualquier cliente sabe mostrar como imagen.

Esto se descubrió probando el despliegue real: un `@app.ui()` fijo mostraba
el placeholder literal `[Rendered Prefab UI]` en clientes sin soporte de la
extensión (ese texto es el *fallback* que FastMCP genera automáticamente en
el canal de contenido plano cuando la herramienta devuelve un componente
Prefab UI). Con la detección dinámica, cada cliente recibe la mejor
representación que sabe renderizar.

## Requisitos

- Python ≥ 3.10, [`uv`](https://docs.astral.sh/uv/).

## Correr localmente

```bash
uv sync
uv run pytest
uv run fastmcp list src/qrmcp/server.py
uv run fastmcp dev inspector src/qrmcp/server.py:mcp
```

## Instalar en Claude Desktop

```bash
uv run fastmcp install claude-desktop src/qrmcp/server.py:mcp --name "QR" --project .
```

No lleva `--env-file`: no hay variables de entorno que configurar.

## Desplegar en Prefect Horizon

Igual que `cobrador-mcp`, `fastmcp==4.0.5` no tiene comando de `deploy` por
CLI — se conecta el repositorio desde el sitio web:

1. Sube este repo a GitHub (puede ser público: no contiene secretos).
2. Entra a https://horizon.prefect.io, inicia sesión y conecta el repo.
3. Punto de entrada: `src/qrmcp/server.py:mcp`, transporte HTTP.
4. No hace falta configurar ninguna variable de entorno ni secreto.
5. La URL pública resultante puede compartirse directamente — no requiere
   `Authorization` ni ningún header especial.
