# Recomendaciones defensivas

## Endpoint

- **Verificar el modo de Defender**: si FortiEDR está como AV principal, confirmar que Defender no esté en modo pasivo sin necesidad.
  ```powershell
  Get-MpComputerStatus | Select-Object AMRunningMode
  ```
- **Auditar políticas de ambos EDRs** para asegurar cobertura completa.
- **AppLocker o WDAC** para restringir la ejecución de binarios no firmados.
- **Bloquear la lectura de `Login Data`** por procesos no-navegador mediante reglas de aplicación.

## Red

- **Inspección TLS saliente** para detectar exfiltración cifrada.
- **Bloquear dominios de túnel** (ngrok, Cloudflare Tunnel, etc.) en entornos corporativos.
- **Monitorear conexiones a dominios no corporativos** desde procesos no habituales.
- **DNS filtering** para bloquear dominios maliciosos conocidos.

## Identidad

- **MFA en todas las cuentas críticas** (Gmail, bancos, etc.).
- **Password managers** en lugar de guardar credenciales en el navegador.
- **Monitoreo de credenciales filtradas** (Have I Been Pwned, etc.).

## Usuario

- **Educación sobre SmartScreen**: no ignorar las advertencias.
- **No descargar binarios** de fuentes no oficiales.
- **Formación sobre phishing**: verificar remitentes, no hacer clic en links sospechosos.
- **Simulacros de phishing** periódicos (GoPhish, KnowBe4).

## Datos

- **Cifrado de discos** (BitLocker).
- **Protección de `Login Data`** con políticas de aplicación.
- **Backups regulares** y planes de recuperación.

## Detección proactiva

- **Hunting de procesos que acceden a `Login Data`** de navegadores.
- **Monitoreo de conexiones HTTPS** a dominios de túnel.
- **Análisis de binarios PyInstaller** en endpoints.
- **Correlación de eventos** entre EDR, NDR y SIEM.

## Tabla resumen

| Capa | Recomendación |
|---|---|
| Endpoint | Verificar modo Defender, AppLocker/WDAC |
| Red | Inspección TLS, bloqueo de túneles |
| Identidad | MFA, password managers |
| Usuario | Educación, simulacros de phishing |
| Datos | Cifrado, backups |
| Detección | Hunting proactivo, correlación SIEM |
