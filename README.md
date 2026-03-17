# Petrol Price – Home Assistant Add-on + Integration

Fetches fuel price board images from a URL, parses them with OCR, and exposes fuel types as **native Home Assistant sensor entities** (one sensor per fuel type, price as state).

## Components

1. **Add-on** (`petrolprice/`): Docker add-on that fetches the image from a configurable URL, runs Tesseract OCR, parses the "Fuel" section, and serves `GET /api/prices` via HTTP (ingress).
2. **Custom integration** (`custom_components/petrolprice/`): Polls the add-on API and creates sensor entities directly in Home Assistant (no MQTT).

## Installation

### 1. Add-on

- Copy the `petrolprice/` folder into your Home Assistant add-ons directory (or add this repo as a custom add-on repository).
- Install the **Petrol Price** add-on.
- Configure **Image URL** (required) and **Scan interval (hours)** (default 6).
- Start the add-on.

### 2. Integration

- Copy `custom_components/petrolprice/` into your Home Assistant `config/custom_components/` directory (or install via HACS if you add this repo).
- Restart Home Assistant.
- Go to **Settings → Devices & services → Add integration** and add **Petrol Price**.
- Enter the add-on **Web UI URL** (ingress URL). You can get it from the add-on card in the Supervisor panel (e.g. open the add-on and copy the URL from the browser).
- Optionally set the **Scan interval** for how often the integration polls the add-on.

Sensors will appear under one device (**Petrol Price**) with one entity per fuel type; state is the price (e.g. €/L).

## Image format

The add-on expects an image of a fuel price board that includes:

- Optional: address (top left), logo (top right).
- A section titled **Fuel**.
- Below that, lines with fuel type names (left) and prices on the right (e.g. `1.45` or `1,45`).

Use the sample images in `Resources/` to tune the parser if needed.

## Development

- **Add-on**: Python 3, Tesseract OCR, aiohttp. Options are read from `/data/options.json`.
- **Integration**: Uses a `DataUpdateCoordinator` to poll the add-on and creates `SensorEntity` instances per fuel type.
