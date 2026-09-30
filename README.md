# QR WiFi

Genera un código QR minimalista para conectarse a tu red WiFi automáticamente
(Android y iPhone lo reconocen de forma nativa, sin apps ni permisos), con un
ícono de WiFi al centro. Pensado para imprimir en un cuadro (10×10 cm @ 300 DPI).

## Instalación

1. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Configuración

1. Copia `.env.example` a `.env`:

   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y coloca tu SSID y contraseña reales:

   ```
   WIFI_SSID=NombreDeTuRed
   WIFI_PASSWORD=TuContraseña
   ```

   El archivo `.env` está en `.gitignore`, así que tus credenciales nunca se suben a git.

## Uso

```bash
python wifi_qr.py
```

Esto genera `wifi_qr.png` en la misma carpeta, listo para imprimir. El script:

- Codifica tu red en el formato estándar `WIFI:T:WPA;S:<ssid>;P:<password>;;`
- Coloca un badge circular con ícono de WiFi al centro
- Verifica automáticamente que el QR generado se pueda leer correctamente
  (si falla, reduce el tamaño del recuadro central y reintenta)
- Exporta en alta resolución (10×10 cm a 300 DPI)

## Ejemplo

Así se ve el resultado final (generado con datos inventados solo para
ilustrar el diseño — no es una red real, no conecta a nada):

![Ejemplo de QR WiFi generado](assets/example_qr.png)

## Notas

- Solo soporta redes WPA/WPA2. Si tu red es WPA3-only, edita `T:WPA` en
  `wifi_qr.py` (función `build_wifi_payload`) según corresponda.
- El tamaño del badge central es configurable con `INITIAL_LOGO_RATIO`
  y `MIN_LOGO_RATIO` en `wifi_qr.py`.
- El ícono central (`assets/wifi_badge.png`) es una imagen fija con fondo
  transparente que se pega y escala sobre el QR. Si quieres cambiar el diseño,
  reemplaza ese archivo por otra imagen circular con fondo transparente.
- Puedes reactivar el texto "WiFi" debajo del QR poniendo `SHOW_LABEL = True`.
