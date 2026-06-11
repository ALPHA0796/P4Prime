# P4Prime

P4Prime is a deterministic in-network verification framework that performs real-time consistency and loop detection directly in the data plane of P4-programmable switches. P4Prime assigns each switch a unique prime identifier and encodes packet paths as prime products, leveraging the Fundamental Theorem of Arithmetic to enable lightweight per-packet verification with no false negatives under the design assumptions. This repository contains the implementation, evaluation scripts, and experimental artifacts used to validate P4Prime on the BMv2 software switch and to demonstrate its hardware deployability on Tofino.

***

## Quick Start

### Initialization

- Copy all files from this directory into an empty directory, **keeping the relative layout between files unchanged**.
- In that directory, run:

```bash
sudo python3 FatTree_4.py
```

- Wait until the topology finishes building. A Mininet interactive CLI will appear.
- In the Mininet CLI, run:

```bash
xterm h1
```

This opens an xterm terminal for `h1`.

The next sections describe the steps for **using P4Prime** and **without using P4Prime**.

### With P4Prime

- Open another terminal in the same directory and run:

```bash
sudo python3 test.py
```

- Wait until the program prints the list of host interfaces. Switch back to the `h1` xterm and type:

```bash
./topo/FatTree6/send.py --n [number of packets] --ip 10.0.8.16 --m tag --t 0.1
```

- Wait until the `h1` xterm becomes responsive again — this signals that the experiment has finished.
- Go back to the terminal where `test.py` is running, press `Ctrl+C`, wait 2 seconds, then press `Ctrl+C` again. A `res.csv` file will be produced inside the `data/` directory.

### Without P4Prime

- Open another terminal in the same directory and run:

```bash
sudo python3 test.py --o 1
```

- Wait until the program prints the list of host interfaces. Switch back to the `h1` xterm and type:

```bash
./topo/FatTree6/send.py --n [number of packets] --ip 10.0.8.16 --t 0.1
```

- Wait until the `h1` xterm becomes responsive again — this signals that the experiment has finished.
- Go back to the terminal where `test.py` is running, press `Ctrl+C`, wait 2 seconds, then press `Ctrl+C` again. A `res.csv` file will be produced inside the `data/` directory.

### Collecting Data&#x20;

- The latest experiment trace is stored as `data/res.csv`. If you want to keep it, copy it to another file first.

***

## Data Collection

Each test run produces two CSV files inside the `data/` directory:

| File                 | Columns                                      | Description                               |
| -------------------- | -------------------------------------------- | ----------------------------------------- |
| `data/res.csv`       | `Packet ID`, `Timestamp (ns)`                | Per-packet end-to-end latency.            |
| `data/cpu_usage.csv` | `Timestamp` (relative, sec), `CPU Usage (%)` | Host CPU utilization (sampled at 100 ms). |

