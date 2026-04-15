# Flights App — CS 6083 PS3 Problem 1

A Flask + PostgreSQL web front-end for the airline `flightsdb` schema from PS2.
Lets users search for flights between two airports over a date range and view
seat availability for any specific flight instance.

**Repo:** https://github.com/adithyab-20/flightsapp_dbms

---

## Features

- **Search form** — origin airport code, destination airport code, and a continuous date range.
- **Results page** — lists all matching flights (flight number, airline, date, origin, destination, departure time), regardless of booking status.
- **Detail page** — click any flight to see the aircraft type, total capacity, number of available seats, and the list of currently booked seat numbers.

---

## Stack

- Python 3.10+ / Flask
- PostgreSQL (tested on 18) via psycopg2
- Plain HTML templates (Jinja2) with CSS

---

## Project structure

```
flightsapp_dbms/
├── app.py              # Flask app — 3 routes, 3 SQL queries
├── templates/
│   ├── index.html      # Search form
│   ├── results.html    # Flight list
│   └── detail.html     # Flight detail + seat info
├── static/
│   └── style.css
├── .gitignore
└── README.md
```

---

## Setup

### 1. Prerequisites

- PostgreSQL running locally with the `flightsdb` database loaded.

### 2. Install dependencies

```bash
pip install flask psycopg2-binary
```

### 3. Set environment variables

The app reads database credentials from environment variables. `FLIGHTSAPP_DB_NAME` and `FLIGHTSAPP_DB_USER` are required; the rest have sensible defaults.

**Mac / Linux (bash/zsh):**

```bash
export FLIGHTSAPP_DB_NAME=flightsdb
export FLIGHTSAPP_DB_USER=postgres
export FLIGHTSAPP_DB_PASSWORD=yourpassword
```

**Windows (PowerShell):**

```powershell
$env:FLIGHTSAPP_DB_NAME = "flightsdb"
$env:FLIGHTSAPP_DB_USER = "postgres"
$env:FLIGHTSAPP_DB_PASSWORD = "yourpassword"
```

If any required variable is missing, the app raises a clear `RuntimeError` on the first request naming the missing variable(s).

### 4. Run

```bash
python app.py
```

Then open <http://localhost:5000> in a browser.

---

## Usage

1. On the start page, enter an origin airport code, a destination airport code, and a date range, then click **Search**.
2. The results page lists all flight instances matching the route within the range.
3. Click any flight number to see its capacity, the number of available seats, and the list of currently taken seat numbers.


## Implementation notes

- All SQL uses **parameterized queries** (`%s` placeholders with a values tuple). User input is never concatenated into SQL strings, so the app is safe from SQL injection.
- The detail page joins **Flight ⨝ FlightService ⨝ Aircraft** to pull route info, airline, duration, plane type, and capacity in a single query, then runs a separate query against `Booking` to pull the list of taken seat numbers.
- Available-seat count is computed in Python as `capacity - len(taken_seats)` rather than with a SQL aggregate, since the seat list is already needed for the page.
- Airport codes from the form are uppercased (`.upper()`) so users can type `jfk` or `JFK` interchangeably.

---