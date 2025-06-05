# ── file: backend/seed_db.py ─────────────────────────────────────────────
import os
import json
from datetime import datetime
import mysql.connector

# 1) Adjust these connection parameters as needed:
DB_CONFIG = {
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "database": "climate_data",
    "port": int(os.environ.get("MYSQL_PORT", 3306))
}

# 2) Locate the JSON file
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_data.json")

# 3) Read the JSON into memory once
with open(DATA_PATH, "r") as f:
    raw_data = json.load(f)

LOCATIONS_JSON     = raw_data.get("locations", [])
METRICS_JSON       = raw_data.get("metrics", [])
CLIMATE_DATA_JSON  = raw_data.get("climate_data", [])

def parse_date(date_str):
    """
    Given "YYYY-MM-DD", return a datetime.date object.
    """
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def main():
    # 4) Connect to MySQL
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 5) Insert into `locations`
    insert_loc_sql = """
        INSERT INTO locations (
            id, name, country, latitude, longitude, region
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            country=VALUES(country),
            latitude=VALUES(latitude),
            longitude=VALUES(longitude),
            region=VALUES(region)
    """
    for loc in LOCATIONS_JSON:
        cursor.execute(
            insert_loc_sql,
            (
                loc["id"],
                loc["name"],
                loc["country"],
                loc["latitude"],
                loc["longitude"],
                loc["region"],
            )
        )

    # 6) Insert into `metrics`
    insert_met_sql = """
        INSERT INTO metrics (
            id, name, display_name, unit, description
        ) VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name=VALUES(name),
            display_name=VALUES(display_name),
            unit=VALUES(unit),
            description=VALUES(description)
    """
    for met in METRICS_JSON:
        cursor.execute(
            insert_met_sql,
            (
                met["id"],
                met["name"],
                met["display_name"],
                met["unit"],
                met.get("description", None),
            )
        )

    # 7) Insert into `climate_data`
    insert_climate_sql = """
        INSERT INTO climate_data (
            id, location_id, metric_id, date, value, quality
        ) VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            location_id=VALUES(location_id),
            metric_id=VALUES(metric_id),
            date=VALUES(date),
            value=VALUES(value),
            quality=VALUES(quality)
    """
    for entry in CLIMATE_DATA_JSON:
        dt = parse_date(entry["date"])
        cursor.execute(
            insert_climate_sql,
            (
                entry["id"],
                entry["location_id"],
                entry["metric_id"],
                dt,
                entry["value"],
                entry["quality"],
            )
        )

    # 8) Commit and close
    conn.commit()
    cursor.close()
    conn.close()
    print("✅  All sample_data rows have been inserted.")


if __name__ == "__main__":
    main()
