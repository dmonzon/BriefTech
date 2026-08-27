#!/usr/bin/env python3
"""Construye el HTML y el texto plano de El Brief Diario.

Entrada:  un JSON con la forma
    {"fecha": "Miércoles, 26 de agosto de 2026",
     "categorias": [{"titulo": "...", "accent": "#0f766e",
                     "items": [{"titulo","resumen","fuente","url"}, ...]}, ...]}

Salida:   <out>.html  y  <out>.txt

El HTML se mantiene deliberadamente compacto (clases CSS compartidas, sin
tablas anidadas por noticia). Ver README.md: un HTML de ~93 KB hace fallar el
envío por el MCP de Resend; esta plantilla deja 70 noticias en ~48 KB.
"""

import argparse
import html
import json
import sys

CSS = (
    "body{margin:0;padding:0;background:#f2f1ed;font-family:Georgia,'Times New Roman',serif}"
    ".w{background:#f2f1ed;padding:28px 10px}"
    ".c{max-width:640px;width:100%;background:#fff;border-radius:10px;overflow:hidden}"
    ".h{background:#14213d;padding:34px 36px 26px}"
    ".he{font-family:Helvetica,Arial,sans-serif;color:#e8b923;font-size:12px;"
    "letter-spacing:3px;text-transform:uppercase;margin-bottom:6px}"
    ".ht{color:#fff;font-size:30px;font-weight:bold;line-height:1.2}"
    ".hd{font-family:Helvetica,Arial,sans-serif;color:#a9b4c9;font-size:13px;margin-top:8px}"
    ".in{padding:26px 36px 4px;font-family:Helvetica,Arial,sans-serif;color:#444;"
    "font-size:14px;line-height:1.6}"
    ".sh{padding:26px 36px 2px}"
    ".sb{padding-left:12px}"
    ".se{font-family:Helvetica,Arial,sans-serif;font-size:11px;letter-spacing:2px;"
    "text-transform:uppercase;font-weight:bold}"
    ".st{color:#14213d;font-size:22px;font-weight:bold;margin-top:2px}"
    ".i{padding:13px 36px;border-bottom:1px solid #eee}"
    ".l{padding:13px 36px 4px}"
    ".n{font-size:13px;font-weight:bold;font-family:Helvetica,Arial,sans-serif;letter-spacing:1px}"
    ".t{color:#1a1a1a;font-size:16px;font-weight:bold;line-height:1.35;margin-top:3px}"
    ".s{font-family:Helvetica,Arial,sans-serif;color:#555;font-size:13.5px;"
    "line-height:1.55;margin-top:6px}"
    ".m{font-family:Helvetica,Arial,sans-serif;font-size:12.5px;margin-top:7px}"
    ".g{color:#999}"
    ".a{text-decoration:none;font-weight:bold}"
    ".f{background:#f7f6f2;padding:24px 36px;font-family:Helvetica,Arial,sans-serif;"
    "color:#8a8a86;font-size:12px;line-height:1.6;border-top:1px solid #ececec}"
)

REMITENTE = "noreply@monzonlabs.com"


def e(s):
    return html.escape(s, quote=True)


def render_html(data):
    filas = []
    for cat in data["categorias"]:
        ac = cat["accent"]
        filas.append(
            f'<tr><td class="sh"><div class="sb" style="border-left:4px solid {ac}">'
            f'<div class="se" style="color:{ac}">Sección</div>'
            f'<div class="st">{e(cat["titulo"])}</div></div></td></tr>'
        )
        total = len(cat["items"])
        for idx, it in enumerate(cat["items"], 1):
            cls = "i" if idx < total else "l"
            filas.append(
                f'<tr><td class="{cls}">'
                f'<div class="n" style="color:{ac}">{idx:02d}</div>'
                f'<div class="t">{e(it["titulo"])}</div>'
                f'<div class="s">{e(it["resumen"])}</div>'
                f'<div class="m"><span class="g">{e(it["fuente"])}</span> &middot; '
                f'<a href="{e(it["url"])}" class="a" style="color:{ac}">'
                f'Leer noticia completa &rarr;</a></div>'
                f'</td></tr>'
            )

    nombres = [c["titulo"].lower() for c in data["categorias"]]
    temas = (
        ", ".join(nombres[:-1]) + " y " + nombres[-1] if len(nombres) > 1 else nombres[0]
    )
    return (
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>El Brief Diario</title><style>" + CSS + "</style></head><body>"
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" class="w">'
        '<tr><td align="center">'
        '<table role="presentation" width="640" cellpadding="0" cellspacing="0" class="c">'
        '<tr><td class="h" align="center"><div class="he">BriefTech Newsletter</div>'
        '<div class="ht">El Brief Diario</div>'
        f'<div class="hd">{e(data["fecha"])}</div></td></tr>'
        f'<tr><td class="in">Las 10 noticias más relevantes del día en '
        f'{len(data["categorias"])} categorías: {e(temas)}.</td></tr>'
        + "".join(filas)
        + '<tr><td class="f" align="center">Brief generado automáticamente a partir de '
        "fuentes públicas verificadas.<br>"
        f"Enviado por BriefTech &middot; {REMITENTE}</td></tr>"
        "</table></td></tr></table></body></html>"
    )


def render_text(data):
    lineas = [
        "EL BRIEF DIARIO - " + data["fecha"],
        f'Las 10 noticias mas relevantes del dia en {len(data["categorias"])} categorias.',
        "",
    ]
    for cat in data["categorias"]:
        lineas.append(cat["titulo"].upper())
        for idx, it in enumerate(cat["items"], 1):
            lineas.append(f'{idx}. {it["titulo"]} [{it["fuente"]}] {it["url"]}')
        lineas.append("")
    lineas.append(f"Enviado por BriefTech - {REMITENTE}")
    return "\n".join(lineas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json_in", help="JSON con fecha y categorias")
    ap.add_argument("-o", "--out", default="brief", help="prefijo de salida")
    args = ap.parse_args()

    with open(args.json_in, encoding="utf-8") as fh:
        data = json.load(fh)

    doc = render_html(data)
    txt = render_text(data)

    with open(args.out + ".html", "w", encoding="utf-8") as fh:
        fh.write(doc)
    with open(args.out + ".txt", "w", encoding="utf-8") as fh:
        fh.write(txt)

    n = sum(len(c["items"]) for c in data["categorias"])
    kb = len(doc.encode("utf-8")) / 1024
    print(f"{args.out}.html  {kb:.1f} KB  |  {n} noticias  |  {doc.count('<a href=')} enlaces")
    print(f"{args.out}.txt   {len(txt.encode('utf-8')) / 1024:.1f} KB")

    if kb > 60:
        print("AVISO: >60 KB. El envio por el MCP de Resend puede fallar.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
