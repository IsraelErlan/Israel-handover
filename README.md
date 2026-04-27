# GPS Track Viewer

A desktop and web application for visualising GPS flight tracks extracted from ArduPilot MAVLink `.bin` log files.

Built with **Python**, **Flet** (Flutter-based UI), and **pymavlink**.

---

## Features

- Parses MAVLink `.bin` log files and extracts GPS coordinates
- Displays the full flight track on an interactive map (CartoDB Voyager tiles)
- Marks takeoff and landing points with distinct icons
- Runs as a native desktop app locally, or as a web app inside Docker

---

## Project Structure

```
israel_handover/
├── data/
│   └── log_file_test_01.bin      # MAVLink log file (not committed)
├── src/
│   ├── business_logic/
│   │   ├── main.py               # Public entry point: get_clean_gps_data()
│   │   ├── mavlink_reader.py     # Reads and filters GPS messages from .bin
│   │   └── gps_processor.py     # Converts raw data to a clean DataFrame
│   └── gui/
│       └── map_component.py     # Flet UI — map, markers, toolbar
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Prerequisites

- Python 3.12+
- pip

---

## Running Locally

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Run the app**

```bash
python src/gui/map_component.py
```

A native desktop window opens with the map.
The data file path defaults to the hardcoded path in `map_component.py`.
To use a different file, set the `DATA_FILE` environment variable:

```bash
# Windows
set DATA_FILE=C:\path\to\your\log.bin
python src/gui/map_component.py

# macOS / Linux
DATA_FILE=/path/to/your/log.bin python src/gui/map_component.py
```

---

## Running with Docker

**1. Build and start**

```bash
docker compose up --build
```

**2. Open in browser**

```
http://localhost:8080
```

The `data/` directory is mounted read-only into the container.
To use a different log file, update the `DATA_FILE` value in `docker-compose.yml`:

```yaml
environment:
  DATA_FILE: /app/data/your_log.bin
```

---

## Architecture

### Data flow

```
.bin file
   └─► MavlinkGpsReader       filters GPS messages (Instance=1), downsamples 1-in-10
         └─► GpsDataProcessor  converts to DataFrame, renames columns
               └─► get_clean_gps_data()   public API returning DataFrame
                     └─► map_component.py  builds Flet markers & polyline
```

### Why background thread for data loading?

Flet renders the map (and starts fetching map tiles) only after `main()` returns.
Loading GPS data synchronously inside `main()` would block tile requests until the
file is fully parsed. The background thread lets both happen in parallel.

### Why `move_to` instead of `initial_center`?

`initial_center` is a one-time initialisation parameter — changing it after the map
has been rendered has no effect. `move_to` is an async method that sends a navigation
command to the live Flutter map control.

---

## Environment Variables

| Variable   | Default                                   | Description                        |
|------------|-------------------------------------------|------------------------------------|
| `DATA_FILE`| Windows path in `map_component.py`        | Path to the MAVLink `.bin` log     |
| `FLET_ENV` | _(unset)_                                 | Set to `docker` to enable web mode |

---

## Dependencies

| Package      | Purpose                              |
|--------------|--------------------------------------|
| `flet`       | UI framework (Flutter-based)         |
| `flet-map`   | Interactive map control for Flet     |
| `flet-web`   | Web server mode for Flet             |
| `pymavlink`  | Parses ArduPilot MAVLink `.bin` logs |
| `pandas`     | DataFrame manipulation               |
