# qr-mcp

Servidor MCP mínimo: genera un código QR con estilo a partir de un link y lo
muestra como imagen en el chat. Sin base de datos, sin secretos, sin
autenticación — pensado para que cualquiera lo use libremente en una demo.

## Herramienta

| Herramienta | Entrada | Salida |
|---|---|---|
| `generar_qr` | `link: str`, `color: str = "#0F172A"`, `fondo: str = "#FFFFFF"` | Imagen PNG del QR |

Si `link` no trae esquema (`http://`/`https://`), se le antepone `https://`
automáticamente. Los colores se validan como hexadecimal `#RRGGBB`.

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
