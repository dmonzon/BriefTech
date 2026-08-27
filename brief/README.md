# El Brief Diario — envío

Resumen diario de noticias enviado por correo. Este documento fija la
configuración de envío y los dos fallos que ya ocurrieron en producción, para
no repetirlos.

## Destinatarios y remitente

| Campo | Valor |
|---|---|
| From | `BriefTech <noreply@monzonlabs.com>` |
| To | `danny.monzon@outlook.com` |
| Cc | `bnymed@proton.me`, `docbenefactor@gmail.com` |
| Bcc | `monzon8@hotmail.com` |

El dominio `monzonlabs.com` está verificado en Resend (región `us-east-1`,
envío habilitado), así que `noreply@monzonlabs.com` es un remitente válido.

## Orden de proveedores

1. **Resend** — siempre el primer intento.
2. **Gmail** — solo si Resend falla, para no dejar de enviar el resumen.

Si el envío termina cayendo en Gmail, decirlo explícitamente en el reporte:
el remitente entonces **no** es `noreply@monzonlabs.com`.

## Generar el contenido

```sh
python3 brief/build_brief.py noticias.json -o brief
# brief.html  47.7 KB  |  70 noticias  |  70 enlaces
# brief.txt   14.3 KB
```

Formato de `noticias.json`:

```json
{
  "fecha": "Miércoles, 26 de agosto de 2026",
  "categorias": [
    {
      "titulo": "Avances Tecnológicos",
      "accent": "#0f766e",
      "items": [
        {"titulo": "...", "resumen": "...", "fuente": "CNN", "url": "https://..."}
      ]
    }
  ]
}
```

Colores por sección: tecnología `#0f766e`, salud `#be123c`, programación
`#4338ca`, finanzas `#a16207`, educación `#0369a1`, IA `#7e22ce`, negocios
`#1e3a8a`.

## Errores conocidos

### 1. Mandar la ruta del archivo en lugar del contenido

Pasar `"/tmp/.../brief.html"` como argumento `html` de `send-email` **no
falla**: Resend acepta esa cadena como cuerpo y entrega un correo cuyo único
contenido es la ruta. Ya se envió así una vez.

Hay que leer el archivo y pasar el HTML literal. Verificación rápida tras
enviar, con `get-email`:

- el HTML debe empezar por `<!DOCTYPE`
- no debe aparecer ninguna ruta local
- el número de enlaces debe coincidir con el de noticias

### 2. Payload demasiado grande

Un HTML de ~93 KB hizo fallar la llamada al MCP de Resend con
`Anthropic Proxy: Invalid content from server` — un error de transporte, no de
Resend. La plantilla de `build_brief.py` usa clases CSS compartidas y evita
tablas anidadas por noticia, con lo que 70 noticias caben en ~48 KB. El script
avisa por `stderr` si se pasa de 60 KB.

Como `RESEND_API_KEY` no está en el entorno, no se puede evitar el MCP usando
la API REST directamente; mantener el HTML pequeño es la única defensa.

## Contenido

Solo información obtenida de búsquedas reales. No inventar noticias, cifras ni
URLs; cada noticia lleva enlace a su fuente original.
