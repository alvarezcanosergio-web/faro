#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FARO v0.1 - Vigilante de tarifas del oceano LLM
Strange Loop Factory

Que hace:
  1. Descarga el catalogo completo de modelos y precios (OpenRouter /api/v1/models,
     publico y gratuito: 400+ modelos, todos los proveedores relevantes).
  2. Normaliza precios a USD por millon de tokens (entrada / salida) + contexto.
  3. Guarda un snapshot fechado (git = base de datos historica, coste cero).
  4. Compara contra el snapshot anterior y detecta eventos:
       NEW_MODEL, REMOVED, PRICE_UP, PRICE_DOWN, CONTEXT_CHANGE
  5. Si existe perfil.json, traduce cada evento a impacto personal (EUR/mes).
  6. Genera ALERTAS.md (humano) + data/events/*.json (maquina).
  7. Opcional: notifica por Telegram si hay eventos relevantes.

Uso:
  python faro_watch.py                 # ejecucion real (necesita red)
  python faro_watch.py --mock          # test sin red con fixtures deterministas
  python faro_watch.py --perfil perfil.json
  python faro_watch.py --data-dir data

Cero dependencias externas (solo stdlib). Python >= 3.9.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

API_URL = "https://openrouter.ai/api/v1/models"
UMBRAL_PCT = 0.5          # ignorar variaciones < 0.5% (ruido de float)
TOP_N_MD = 15             # maximo de filas por seccion en ALERTAS.md
USER_AGENT = "FARO/0.1 (+https://strangeloopfactory.com)"


# ----------------------------------------------------------------------------
# Descarga y normalizacion
# ----------------------------------------------------------------------------

def fetch_models() -> list:
    req = urllib.request.Request(API_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.loads(r.read().decode("utf-8"))
    return payload.get("data", [])


def _to_per_million(v) -> float | None:
    """OpenRouter da USD por token como string. Convertimos a USD por 1M tokens."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if f < 0:  # precios dinamicos/sentinela
        return None
    return round(f * 1_000_000, 6)


def normalize(models: list) -> dict:
    """Devuelve {model_id: {name, in, out, ctx, created}} con precios USD/M tokens."""
    out = {}
    for m in models:
        mid = m.get("id")
        if not mid:
            continue
        pricing = m.get("pricing") or {}
        out[mid] = {
            "name": m.get("name") or mid,
            "in": _to_per_million(pricing.get("prompt")),
            "out": _to_per_million(pricing.get("completion")),
            "ctx": m.get("context_length"),
            "created": m.get("created"),
        }
    return out


# ----------------------------------------------------------------------------
# Snapshots (git-friendly)
# ----------------------------------------------------------------------------

def snapshot_dir(data_dir: Path) -> Path:
    d = data_dir / "snapshots"
    d.mkdir(parents=True, exist_ok=True)
    return d


def latest_snapshot(data_dir: Path) -> tuple[dict, str] | tuple[None, None]:
    files = sorted(snapshot_dir(data_dir).glob("*.json"))
    if not files:
        return None, None
    f = files[-1]
    with open(f, "r", encoding="utf-8") as fh:
        return json.load(fh), f.stem


def save_snapshot(data_dir: Path, catalog: dict, ts: str) -> Path:
    p = snapshot_dir(data_dir) / f"{ts}.json"
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return p


# ----------------------------------------------------------------------------
# Diff -> eventos
# ----------------------------------------------------------------------------

def _pct(old: float, new: float) -> float:
    return round((new - old) / old * 100, 2) if old else 0.0


def diff(prev: dict, curr: dict) -> list:
    events = []
    prev_ids, curr_ids = set(prev), set(curr)

    for mid in sorted(curr_ids - prev_ids):
        c = curr[mid]
        events.append({"type": "NEW_MODEL", "model": mid, "name": c["name"],
                       "in": c["in"], "out": c["out"], "ctx": c["ctx"]})

    for mid in sorted(prev_ids - curr_ids):
        p = prev[mid]
        events.append({"type": "REMOVED", "model": mid, "name": p["name"],
                       "in": p["in"], "out": p["out"]})

    for mid in sorted(prev_ids & curr_ids):
        p, c = prev[mid], curr[mid]
        for side in ("in", "out"):
            po, co = p.get(side), c.get(side)
            if po is None or co is None or po == co:
                continue
            pct = _pct(po, co)
            if abs(pct) < UMBRAL_PCT:
                continue
            events.append({
                "type": "PRICE_UP" if pct > 0 else "PRICE_DOWN",
                "model": mid, "name": c["name"], "side": side,
                "old": po, "new": co, "pct": pct,
            })
        if p.get("ctx") and c.get("ctx") and p["ctx"] != c["ctx"]:
            events.append({"type": "CONTEXT_CHANGE", "model": mid, "name": c["name"],
                           "old": p["ctx"], "new": c["ctx"]})
    return events


# ----------------------------------------------------------------------------
# Impacto personal (perfil.json)
# ----------------------------------------------------------------------------

def load_perfil(path: Path | None) -> dict | None:
    if not path:
        return None
    if not path.exists():
        print(f"[FARO] Aviso: no existe {path}, se omite impacto personal.")
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def coste_mensual(perfil: dict, catalog: dict) -> tuple[float, list]:
    """Coste USD/mes del perfil con el catalogo dado + detalle por modelo."""
    total, detalle = 0.0, []
    for uso in perfil.get("uso_mensual", []):
        mid = uso.get("model")
        m = catalog.get(mid)
        if not m or m.get("in") is None or m.get("out") is None:
            detalle.append({"model": mid, "coste": None, "nota": "sin precio en catalogo"})
            continue
        c = uso.get("mtok_in", 0) * m["in"] + uso.get("mtok_out", 0) * m["out"]
        total += c
        detalle.append({"model": mid, "coste": round(c, 4)})
    return round(total, 4), detalle


def impacto_personal(perfil: dict, prev: dict, curr: dict, events: list) -> dict:
    fx = float(perfil.get("usd_eur", 1.0))
    divisa = perfil.get("divisa", "USD")
    total_prev, _ = coste_mensual(perfil, prev)
    total_curr, detalle = coste_mensual(perfil, curr)
    delta = round(total_curr - total_prev, 4)

    mis_modelos = {u.get("model") for u in perfil.get("uso_mensual", [])}
    afectan = [e for e in events if e.get("model") in mis_modelos]

    return {
        "divisa": divisa,
        "coste_mes_actual": round(total_curr * fx, 2),
        "coste_mes_anterior": round(total_prev * fx, 2),
        "delta_mes": round(delta * fx, 2),
        "eventos_que_te_afectan": afectan,
        "detalle": detalle,
    }


# ----------------------------------------------------------------------------
# Salidas: ALERTAS.md + events json + Telegram
# ----------------------------------------------------------------------------

def _fmt_price(v) -> str:
    return f"${v:,.2f}/M" if isinstance(v, (int, float)) else "n/d"


def render_md(ts: str, events: list, curr: dict, impacto: dict | None,
              primera_ejecucion: bool) -> str:
    L = [f"# FARO - Alertas de tarifas LLM", "",
         f"Ultima vigilancia: **{ts} UTC** | Modelos vigilados: **{len(curr)}**", ""]

    if primera_ejecucion:
        L += ["Primera ejecucion: snapshot base creado. A partir de la proxima "
              "ejecucion se detectaran cambios de tarifas, lanzamientos y retiradas.", ""]
        caros = sorted([(m["in"] or 0, mid, m) for mid, m in curr.items()],
                       reverse=True)[:5]
        L += ["## Foto inicial del mercado (top precios de entrada)", ""]
        for p, mid, m in caros:
            L.append(f"- `{mid}` entrada {_fmt_price(m['in'])} / salida {_fmt_price(m['out'])}")
        L.append("")
        return "\n".join(L)

    up = [e for e in events if e["type"] == "PRICE_UP"]
    down = [e for e in events if e["type"] == "PRICE_DOWN"]
    new = [e for e in events if e["type"] == "NEW_MODEL"]
    gone = [e for e in events if e["type"] == "REMOVED"]
    ctx = [e for e in events if e["type"] == "CONTEXT_CHANGE"]

    L += [f"**Resumen:** {len(up)} subidas | {len(down)} bajadas | "
          f"{len(new)} lanzamientos | {len(gone)} retiradas | {len(ctx)} cambios de contexto", ""]

    if impacto:
        d = impacto["delta_mes"]
        signo = "+" if d > 0 else ""
        L += ["## Impacto en tu perfil", "",
              f"- Coste estimado este mes: **{impacto['coste_mes_actual']} {impacto['divisa']}**",
              f"- Variacion por cambios de tarifa: **{signo}{d} {impacto['divisa']}/mes**"]
        for e in impacto["eventos_que_te_afectan"]:
            if e["type"] in ("PRICE_UP", "PRICE_DOWN"):
                L.append(f"- Te afecta: `{e['model']}` ({e['side']}) "
                         f"{_fmt_price(e['old'])} -> {_fmt_price(e['new'])} ({e['pct']:+.1f}%)")
            elif e["type"] == "REMOVED":
                L.append(f"- ATENCION: `{e['model']}` ha sido retirado. Busca alternativa.")
        L.append("")

    def seccion(titulo, items, fmt):
        if not items:
            return
        L.append(f"## {titulo}")
        L.append("")
        for e in items[:TOP_N_MD]:
            L.append(fmt(e))
        if len(items) > TOP_N_MD:
            L.append(f"- ... y {len(items) - TOP_N_MD} mas (ver events/*.json)")
        L.append("")

    seccion("Subidas de precio", sorted(up, key=lambda e: -e["pct"]),
            lambda e: f"- **`{e['model']}`** ({e['side']}): {_fmt_price(e['old'])} -> "
                      f"{_fmt_price(e['new'])} (**{e['pct']:+.1f}%**)")
    seccion("Bajadas de precio (oportunidades)", sorted(down, key=lambda e: e["pct"]),
            lambda e: f"- `{e['model']}` ({e['side']}): {_fmt_price(e['old'])} -> "
                      f"{_fmt_price(e['new'])} ({e['pct']:+.1f}%)")
    seccion("Nuevos modelos", new,
            lambda e: f"- `{e['model']}` entrada {_fmt_price(e['in'])} / "
                      f"salida {_fmt_price(e['out'])} / ctx {e.get('ctx') or 'n/d'}")
    seccion("Modelos retirados", gone, lambda e: f"- `{e['model']}`")
    seccion("Cambios de contexto", ctx,
            lambda e: f"- `{e['model']}`: {e['old']:,} -> {e['new']:,} tokens")

    if not events:
        L += ["Sin cambios desde la ultima vigilancia. El oceano esta en calma.", ""]

    return "\n".join(L)


def save_events(data_dir: Path, ts: str, events: list, impacto: dict | None) -> Path:
    d = data_dir / "events"
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{ts}.json"
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"ts": ts, "events": events, "impacto": impacto},
                  fh, ensure_ascii=False, indent=1)
    return p


def notify_telegram(texto: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat:
        return
    data = urllib.parse.urlencode({"chat_id": chat, "text": texto[:4000]}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    try:
        urllib.request.urlopen(req, timeout=30)
        print("[FARO] Notificacion Telegram enviada.")
    except Exception as e:  # noqa: BLE001
        print(f"[FARO] Telegram fallo (no critico): {e}")


# ----------------------------------------------------------------------------
# Fixtures deterministas para --mock (test sin red)
# ----------------------------------------------------------------------------

def _mk(mid, name, p_in, p_out, ctx):
    return {"id": mid, "name": name, "context_length": ctx, "created": 1700000000,
            "pricing": {"prompt": str(p_in / 1_000_000), "completion": str(p_out / 1_000_000)}}


MOCK_A = [
    _mk("acme/estable-1", "Estable 1", 3.00, 15.00, 200_000),
    _mk("acme/sube-pro", "Sube Pro", 5.00, 25.00, 200_000),
    _mk("beta/baja-flash", "Baja Flash", 0.50, 1.50, 1_000_000),
    _mk("beta/retirado-old", "Retirado Old", 2.00, 6.00, 32_000),
    _mk("gamma/ctx-crece", "Ctx Crece", 1.00, 3.00, 128_000),
]

MOCK_B = [
    _mk("acme/estable-1", "Estable 1", 3.00, 15.00, 200_000),        # sin cambios
    _mk("acme/sube-pro", "Sube Pro", 6.00, 30.00, 200_000),          # +20% in/out
    _mk("beta/baja-flash", "Baja Flash", 0.35, 1.50, 1_000_000),     # -30% in
    _mk("gamma/ctx-crece", "Ctx Crece", 1.00, 3.00, 256_000),        # ctx x2
    _mk("delta/nuevo-omni", "Nuevo Omni", 2.50, 10.00, 500_000),     # lanzamiento
]                                                                     # retirado-old desaparece


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="FARO - vigilante de tarifas LLM")
    ap.add_argument("--mock", action="store_true", help="usar fixtures sin red")
    ap.add_argument("--data-dir", default="data", help="directorio de datos")
    ap.add_argument("--perfil", default="perfil.json", help="perfil de consumo (opcional)")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%S")

    prev, prev_ts = latest_snapshot(data_dir)

    if args.mock:
        raw = MOCK_A if prev is None else MOCK_B
        print(f"[FARO] MOCK ({'A: dia base' if prev is None else 'B: dia con cambios'})")
    else:
        print(f"[FARO] Descargando catalogo de {API_URL} ...")
        raw = fetch_models()

    curr = normalize(raw)
    print(f"[FARO] Catalogo actual: {len(curr)} modelos.")

    primera = prev is None
    events = [] if primera else diff(prev, curr)

    perfil = load_perfil(Path(args.perfil) if args.perfil else None)
    impacto = None
    if perfil and not primera:
        impacto = impacto_personal(perfil, prev, curr, events)

    save_snapshot(data_dir, curr, ts)
    save_events(data_dir, ts, events, impacto)
    md = render_md(ts, events, curr, impacto, primera)
    with open("ALERTAS.md", "w", encoding="utf-8") as fh:
        fh.write(md)

    print(f"[FARO] Snapshot: data/snapshots/{ts}.json"
          + (f" (diff contra {prev_ts})" if prev_ts else " (primera ejecucion)"))
    print(f"[FARO] Eventos: {len(events)} -> ALERTAS.md + data/events/{ts}.json")

    relevantes = [e for e in events if e["type"] in ("PRICE_UP", "PRICE_DOWN", "NEW_MODEL")]
    if relevantes:
        resumen = f"FARO {ts}: " + " | ".join(
            f"{e['model']} {e['type']}"
            + (f" {e['pct']:+.1f}%" if "pct" in e else "")
            for e in relevantes[:10])
        notify_telegram(resumen)

    return 0


if __name__ == "__main__":
    sys.exit(main())
