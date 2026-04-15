from __future__ import annotations

import os
from typing import Any

import psycopg2
import psycopg2.extras
from flask import Flask, abort, render_template, request

app = Flask(__name__)


def _db_connect_kwargs() -> dict[str, Any]:
    """Build psycopg2 connection kwargs from environment variables."""
    required = ("FLIGHTSAPP_DB_NAME", "FLIGHTSAPP_DB_USER")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        names = ", ".join(missing)
        msg = f"Missing required environment variable(s): {names}"
        raise RuntimeError(msg)

    port_raw = os.environ.get("FLIGHTSAPP_DB_PORT", "5432")
    try:
        port = int(port_raw)
    except ValueError as exc:
        msg = "FLIGHTSAPP_DB_PORT must be an integer"
        raise RuntimeError(msg) from exc

    return {
        "dbname": os.environ["FLIGHTSAPP_DB_NAME"],
        "user": os.environ["FLIGHTSAPP_DB_USER"],
        "password": os.environ.get("FLIGHTSAPP_DB_PASSWORD", ""),
        "host": os.environ.get("FLIGHTSAPP_DB_HOST", "localhost"),
        "port": port,
    }


def get_conn():
    return psycopg2.connect(**_db_connect_kwargs())


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    origin = request.args.get("origin", "").strip().upper()
    dest = request.args.get("dest", "").strip().upper()
    date_from = request.args.get("date_from", "").strip()
    date_to = request.args.get("date_to", "").strip()

    if not (origin and dest and date_from and date_to):
        return render_template("index.html", error="All fields are required.")

    sql = """
        SELECT f.flight_number, f.departure_date, fs.origin_code, fs.dest_code,
               fs.departure_time, fs.airline_name
        FROM Flight f
        JOIN FlightService fs ON f.flight_number = fs.flight_number
        WHERE fs.origin_code = %s
          AND fs.dest_code = %s
          AND f.departure_date BETWEEN %s AND %s
        ORDER BY f.departure_date, fs.departure_time
    """
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(sql, (origin, dest, date_from, date_to))
        flights = cur.fetchall()

    return render_template(
        "results.html",
        flights=flights,
        origin=origin,
        dest=dest,
        date_from=date_from,
        date_to=date_to,
    )


@app.route("/flight/<flight_number>/<departure_date>")
def flight_detail(flight_number, departure_date):
    info_sql = """
        SELECT f.flight_number, f.departure_date, fs.origin_code, fs.dest_code,
               fs.departure_time, fs.airline_name, fs.duration,
               f.plane_type, a.capacity
        FROM Flight f
        JOIN FlightService fs ON f.flight_number = fs.flight_number
        JOIN Aircraft a ON f.plane_type = a.plane_type
        WHERE f.flight_number = %s AND f.departure_date = %s
    """
    seats_sql = """
        SELECT seat_number FROM Booking
        WHERE flight_number = %s AND departure_date = %s
        ORDER BY seat_number
    """
    with get_conn() as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute(info_sql, (flight_number, departure_date))
        info = cur.fetchone()
        if not info:
            abort(404)
        cur.execute(seats_sql, (flight_number, departure_date))
        taken = [r["seat_number"] for r in cur.fetchall()]

    available = info["capacity"] - len(taken)
    return render_template("detail.html", info=info, taken=taken, available=available)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
