# Petrol Price Add-on

Fetches fuel price board images from a configurable URL, runs OCR to extract fuel types and prices, and exposes them via an HTTP API for the **Petrol Price** Home Assistant integration.

## Configuration

- **Image URL**: URL to the fuel price board image (e.g. direct image link or a URL that returns an image). Required.
- **Scan interval (hours)**: How often to fetch and parse the image (default: 6).

## Requirements

- The image should show a board with:
  - Optional: address (top left), logo (top right).
  - A **Fuel** section with a list of fuel type names and prices (prices on the right).

## Integration

1. Install and start this add-on; configure **Image URL** and **Scan interval**.
2. In Home Assistant, go to **Settings → Devices & services → Add integration** and add **Petrol Price**.
3. When prompted, enter the add-on **Web UI URL** (ingress). You can open the add-on in the Supervisor panel and copy the URL from the browser, or use the link shown in the add-on card (e.g. `https://your-ha/api/hassio_ingress/...`).
4. Sensors for each fuel type will appear under one device.

No MQTT broker is required; the integration talks to this add-on over HTTP (ingress).
