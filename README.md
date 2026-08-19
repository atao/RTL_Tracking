# rtl_tracking

🔌 A high-performance Python utility designed to capture live JSON data streams from `rtl_433`, store them into an optimized SQLite database, and generate real-time tracking metrics.

## Purpose

The primary objective of this project is to create a persistent storage layer for RF data packets intercepted via Software Defined Radio (SDR) using `rtl_433`. 

This tool serves as an excellent practical framework for learning how to intercept standard output (`stdout`) data streams from compiled binaries and pipe them directly into automated Python processing loops.

### Practical Use Case: TPMS & Sensor Tracking
By capturing data on the 433.92 MHz ISM band, you can permanently log and track:
- **TPMS (Tire Pressure Monitoring Systems):** Monitor and identify unique sensor IDs, tire pressures, and temperatures from vehicles driving around your receiver.
- **Weather Stations & Smart Meters:** Aggregate historical temperature, humidity, and power data from residential remote sensors.

## Key Features

- **Stream-Optimized Ingestion:** Uses a single, persistent SQLite connection channel instead of spawning an I/O request per line. This completely eliminates data loss and packet drops during intense RF bursts.
- **Embedded Storage Optimization:** Automatically applies SQLite Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) and relaxed synchronous boundaries. This drastically improves write speeds and extends the physical lifespan of flash storage (MicroSD cards on a **Raspberry Pi Zero 2**).
- **Automated Analytics View:** Deploys a relational database view called `tracking` that automatically groups, counts, and sorts unique device identifiers over time.

## Requirements

You must have an SDR device (such as an RTL-SDR Blog V4) and the `rtl_433` binary installed on your system.

## Usage and Routing Options

### Live SDR Interception
Pipe the live JSON outputs from `rtl_433` directly into the tracking pipeline:

```bash
rtl_433 -F json | python3 rtl_tracking.py
```

### Logging Outputs with Background Persistence
Store the tracking terminal feedback into a local log file:

```bash
rtl_433 -F json | python3 rtl_tracking.py >> output.log
```

### Batch Processing Historical Captures
You can back-populate your database by passing any pre-recorded newline-delimited JSON log file:

```bash
cat my_json_capture.json | python3 rtl_tracking.py
```

### Filtering Specific Devices
To optimize CPU cycles on lower-powered devices (like a Raspberry Pi), it is highly recommended to filter your `rtl_433` capture targets directly at the source using the `-R` argument (device protocol IDs):

```bash
# Example: Listen exclusively to standard TPMS protocols (e.g., Schrader, Renault, Toyata)
rtl_433 -R 60 -R 110 -R 195 -F json | python3 rtl_tracking.py
```
*Review the complete protocol registry list directly on the [rtl_433 repository](https://github.com/merbanan/rtl_433).*

## Database Architecture

- **`data` (Table):** Logs raw incoming telemetry coordinates including reception timestamp (`time`), protocol description (`model`), and the unique sensor identifier (`id`).
- **`tracking` (View):** A virtual evaluation layer compiling operational metrics. It summarizes total detection counts per hardware sensor ID, sorted dynamically by protocol models.

## Extending the Project

Because the data mapper utilizes a dynamic keys allocation dictionary wrapper (`data.keys()`), you can easily adapt this project to log additional fields (such as `pressure_PSI`, `temperature_C`, or `battery_ok`) by simply appending those fields to the initial `prepare_database` schema declaration dictionary.
