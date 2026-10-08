# Arquitectura técnica de la PoC

## Flujo completo

1. **Usuario descarga `TraductorPro.exe`** de una fuente no oficial (GitHub, pendrive, etc.).
2. **Lo ejecuta** y ve una GUI de traductor funcional.
3. **En segundo plano**, el agente:
   - Recolecta info del sistema.
   - Consulta geolocalización por IP.
   - Lista archivos de interés.
   - Lee `Login Data` de Chrome y Edge.
4. **Empaqueta todo en JSON** y lo envía por HTTPS POST a un webhook.
5. **El atacante recibe los datos** en su receptor (Kali, detrás de un túnel ngrok).

## Por qué pasa desapercibido

### No hay comportamiento "clásicamente malicioso"

| Técnica clásica | ¿La usa la PoC? |
|---|---|
| Crear procesos hijos (`cmd.exe`, `powershell.exe`) | ❌ No |
| Inyectar código en otros procesos | ❌ No |
| Persistencia (registro, tareas programadas) | ❌ No |
| Exfiltración masiva (>MB) | ❌ No |
| Uso de exploits | ❌ No |
| Firmas de malware conocido | ❌ No |

### Lo que sí hace

- **Lectura de archivos del usuario** (algo que hacen backups, sync clients, antivirus legítimos).
- **Conexiones HTTPS salientes** (indistinguibles de cualquier app que use internet).
- **Ejecución en el mismo proceso** (sin hijos, sin inyección).

## Diagrama de componentes

```
traductor_pro.py
    │
    ├── GUI (tkinter) ──── Señuelo visible al usuario
    │
    └── acciones_al_iniciar() ──── Hilo en segundo plano
            │
            └── agente_v3.iniciar_en_hilo()
                    │
                    └── loop_agente()
                            │
                            ├── info_sistema()
                            ├── geo_ip()
                            ├── listar_archivos_interesantes()
                            └── leer_navegadores()
                                    │
                                    └── exfiltrar() ──── HTTPS POST
```

## Tecnologías usadas

- **Python 3.8+**: lenguaje base.
- **tkinter**: GUI del señuelo.
- **sqlite3**: lectura de `Login Data` de Chrome/Edge.
- **urllib.request**: exfiltración HTTPS.
- **PyInstaller**: empaquetado a `.exe`.
- **ngrok**: túnel para exponer el receptor.
