import json
import sqlite3
from functools import lru_cache
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "cardekho.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@lru_cache(maxsize=1)
def get_schema_info() -> str:
    conn = _connect()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM cardekho_dataset")
    total = cur.fetchone()[0]

    cur.execute("SELECT MIN(selling_price), MAX(selling_price) FROM cardekho_dataset")
    price_min, price_max = cur.fetchone()

    cur.execute("SELECT MIN(vehicle_age), MAX(vehicle_age) FROM cardekho_dataset")
    age_min, age_max = cur.fetchone()

    cur.execute("SELECT MIN(km_driven), MAX(km_driven) FROM cardekho_dataset")
    km_min, km_max = cur.fetchone()

    cur.execute(
        "SELECT DISTINCT brand FROM cardekho_dataset WHERE brand IS NOT NULL ORDER BY brand"
    )
    brands = [r[0] for r in cur.fetchall()]

    cur.execute(
        "SELECT DISTINCT fuel_type FROM cardekho_dataset WHERE fuel_type IS NOT NULL"
    )
    fuels = [r[0] for r in cur.fetchall()]

    cur.execute(
        "SELECT DISTINCT transmission_type FROM cardekho_dataset WHERE transmission_type IS NOT NULL"
    )
    transmissions = [r[0] for r in cur.fetchall()]

    cur.execute("SELECT * FROM cardekho_dataset LIMIT 2")
    samples = [dict(r) for r in cur.fetchall()]

    conn.close()

    return f"""TABLE: cardekho_dataset ({total:,} rows)

COLUMNS:
  car_name         (TEXT)    - Full car name, e.g. "Maruti Alto", "Hyundai Grand"
  brand            (TEXT)    - Manufacturer
  model            (TEXT)    - Model name
  vehicle_age      (INTEGER) - How old the car is in years (range: {age_min}-{age_max})
                               NOTE: there is no 'year' column; use vehicle_age for age filters.
                               Newer car = lower vehicle_age. Cars from ~2020 => vehicle_age <= 4.
  km_driven        (INTEGER) - Total km on odometer (range: {km_min:,}-{km_max:,})
  seller_type      (TEXT)    - 'Individual', 'Dealer', 'Trustmark Dealer'
  fuel_type        (TEXT)    - {fuels}
  transmission_type(TEXT)    - {transmissions}
  mileage          (REAL)    - Fuel efficiency in km/litre
  engine           (INTEGER) - Engine displacement in cc
  max_power        (REAL)    - Peak power in bhp
  seats            (INTEGER) - Seating capacity
  selling_price    (INTEGER) - Asking price in RUPEES (range: {price_min:,}-{price_max:,})
                               1 lakh = 100,000 rupees. 5 lakhs = 500000.

BRANDS AVAILABLE: {brands}

IMPORTANT - No body_type column exists.
Use your Indian car knowledge to filter by body type via model name:
  Hatchbacks  : Alto, WagonR, Swift, i10, Grand i10, Celerio, Santro, Kwid, Tiago, Punch
  Sedans      : Dzire, City, Verna, Ciaz, Amaze, Aspire
  Compact SUVs: Brezza, Nexon, Venue, Sonet, WR-V, EcoSport
  Full SUVs   : Creta, Seltos, Harrier, Fortuner, Scorpio, XUV500, XUV700, Thar
  MPVs/MUVs   : Ertiga, Innova, Marazzo, Carens, XL6

SAMPLE ROWS:
{json.dumps(samples, indent=2)}"""


def execute_select(sql: str, max_rows: int = 20) -> list[dict]:
    sql = sql.strip()
    if not sql.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are permitted.")

    if "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT {max_rows}"

    conn = _connect()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
