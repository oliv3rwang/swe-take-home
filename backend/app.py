import os
import json
import math
from datetime import datetime, date
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import statistics

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# ─── MySQL Configuration ─────────────────────────────────────────────────────
DB_CONFIG = {
    "user":     os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", "test"),
    "host":     os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "database": os.environ.get("MYSQL_DB", "climate_data"),
    "port":     int(os.environ.get("MYSQL_PORT", 3306))
}

QUALITY_WEIGHTS = {
    "excellent":    1.0,
    "good":         0.8,
    "questionable": 0.5,
    "poor":         0.3
}

def month_to_season(month: int) -> str:
    """Map month integer to season name."""
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"

BASE_DIR  = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_data.json")


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None


def init_db():
    """
    Create tables if they do not exist, then seed from sample_data.json.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1) Create `locations` table
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS locations (
        id         INT            PRIMARY KEY,
        name       VARCHAR(255)   NOT NULL,
        country    VARCHAR(100)   NOT NULL,
        latitude   DECIMAL(9,6)   NOT NULL,
        longitude  DECIMAL(9,6)   NOT NULL,
        region     VARCHAR(100)   NOT NULL
      );
    """)

    # 2) Create `metrics` table
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS metrics (
        id            INT            PRIMARY KEY,
        name          VARCHAR(100)   NOT NULL,
        display_name  VARCHAR(255)   NOT NULL,
        unit          VARCHAR(50)    NOT NULL,
        description   TEXT
      );
    """)

    # 3) Create `climate_data` table
    cursor.execute("""
      CREATE TABLE IF NOT EXISTS climate_data (
        id           INT               PRIMARY KEY,
        location_id  INT               NOT NULL,
        metric_id    INT               NOT NULL,
        date         DATE              NOT NULL,
        value        FLOAT             NOT NULL,
        quality      ENUM('excellent','good','questionable','poor') NOT NULL,
        FOREIGN KEY (location_id) REFERENCES locations(id),
        FOREIGN KEY (metric_id)   REFERENCES metrics(id)
      );
    """)

    # 4) Load sample_data.json
    with open(DATA_PATH, "r") as f:
        raw = json.load(f)

    # 5) Seed `locations`
    insert_loc = """
      INSERT INTO locations 
        (id, name, country, latitude, longitude, region)
      VALUES (%s, %s, %s, %s, %s, %s)
      ON DUPLICATE KEY UPDATE
        name=VALUES(name),
        country=VALUES(country),
        latitude=VALUES(latitude),
        longitude=VALUES(longitude),
        region=VALUES(region);
    """
    for loc in raw.get("locations", []):
        cursor.execute(insert_loc, (
            loc["id"],
            loc["name"],
            loc["country"],
            loc["latitude"],
            loc["longitude"],
            loc["region"],
        ))

    # 6) Seed `metrics`
    insert_met = """
      INSERT INTO metrics
        (id, name, display_name, unit, description)
      VALUES (%s, %s, %s, %s, %s)
      ON DUPLICATE KEY UPDATE
        name=VALUES(name),
        display_name=VALUES(display_name),
        unit=VALUES(unit),
        description=VALUES(description);
    """
    for met in raw.get("metrics", []):
        cursor.execute(insert_met, (
            met["id"],
            met["name"],
            met["display_name"],
            met["unit"],
            met.get("description", None),
        ))

    # 7) Seed `climate_data`
    insert_cd = """
      INSERT INTO climate_data
        (id, location_id, metric_id, date, value, quality)
      VALUES (%s, %s, %s, %s, %s, %s)
      ON DUPLICATE KEY UPDATE
        location_id=VALUES(location_id),
        metric_id=VALUES(metric_id),
        date=VALUES(date),
        value=VALUES(value),
        quality=VALUES(quality);
    """
    for entry in raw.get("climate_data", []):
        dt = parse_date(entry["date"])
        cursor.execute(insert_cd, (
            entry["id"],
            entry["location_id"],
            entry["metric_id"],
            dt,
            entry["value"],
            entry["quality"],
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Database created and sample_data seeded.")


# ─── API Endpoints ────────────────────────────────────────────────────────────

@app.route("/api/v1/locations", methods=["GET"])
def get_locations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, country, latitude, longitude, region FROM locations ORDER BY name;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"data": rows})


@app.route("/api/v1/metrics", methods=["GET"])
def get_metrics():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, display_name, unit, description FROM metrics ORDER BY name;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"data": rows})


@app.route("/api/v1/climate", methods=["GET"])
def get_climate_data():
    args          = request.args
    # Now accept location name (e.g., "Irvine", "London", "Tokyo") instead of integer ID
    loc_name      = args.get("location_id", type=str)
    # Accept metric name (e.g., "humidity", "precipitation", "temperature") instead of integer ID
    metric_name   = args.get("metric", type=str)
    start_date    = parse_date(args.get("start_date"))
    end_date      = parse_date(args.get("end_date"))

    # Parse quality_threshold as a string (one of "excellent", "good", "questionable", "poor")
    q_thresh_key = args.get("quality_threshold", type=str)
    q_thresh_val = None
    if q_thresh_key:
        q_thresh_key = q_thresh_key.lower()
        if q_thresh_key not in QUALITY_WEIGHTS:
            return jsonify({"error": "quality_threshold must be one of: excellent, good, questionable, poor"}), 400
        q_thresh_val = QUALITY_WEIGHTS[q_thresh_key]

    page     = args.get("page", default=1, type=int)
    per_page = args.get("per_page", default=50, type=int)

    # We JOIN locations and metrics so we can filter by name and also return them in the result
    sql = """
      SELECT
        c.id,
        c.location_id,
        l.name AS location_name,
        c.metric_id,
        m.name AS metric_name,
        DATE_FORMAT(c.date, '%Y-%m-%d') AS date,
        c.value,
        c.quality,
        m.unit
      FROM climate_data c
      JOIN locations l ON c.location_id = l.id
      JOIN metrics m   ON c.metric_id   = m.id
      WHERE 1=1
    """
    params = []

    if loc_name:
        sql += " AND l.name = %s"
        params.append(loc_name)

    if metric_name:
        sql += " AND m.name = %s"
        params.append(metric_name)

    if start_date:
        sql += " AND c.date >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND c.date <= %s"
        params.append(end_date)

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Apply quality_threshold filtering in Python
    if q_thresh_val is not None:
        rows = [r for r in rows if QUALITY_WEIGHTS.get(r["quality"], 0.0) >= q_thresh_val]

    # Pagination
    total_count = len(rows)
    start_idx   = (page - 1) * per_page
    end_idx     = start_idx + per_page
    paginated   = rows[start_idx:end_idx]

    return jsonify({
        "data": paginated,
        "meta": {
            "total_count": total_count,
            "page": page,
            "per_page": per_page
        }
    })

@app.route("/api/v1/summary", methods=["GET"])
def get_summary():
    args       = request.args
    loc_id     = args.get("location_id", type=int)
    metric_id  = args.get("metric", type=int)
    start_date = parse_date(args.get("start_date"))
    end_date   = parse_date(args.get("end_date"))

    try:
        q_thresh = float(args.get("quality_threshold")) if args.get("quality_threshold") is not None else None
        if q_thresh is not None and not (0 <= q_thresh <= 1):
            return jsonify({"error": "quality_threshold must be between 0 and 1"}), 400
    except ValueError:
        return jsonify({"error": "quality_threshold must be a number"}), 400

    # Build WHERE clauses
    where = ["1=1"]
    params = []
    if loc_id:
        where.append("c.location_id = %s")
        params.append(loc_id)
    if metric_id:
        where.append("c.metric_id = %s")
        params.append(metric_id)
    if start_date:
        where.append("c.date >= %s")
        params.append(start_date)
    if end_date:
        where.append("c.date <= %s")
        params.append(end_date)

    # CASE for weight
    weight_case = """
      CASE
        WHEN c.quality = 'excellent' THEN 1.0
        WHEN c.quality = 'good' THEN 0.8
        WHEN c.quality = 'questionable' THEN 0.5
        WHEN c.quality = 'poor' THEN 0.3
        ELSE 0
      END
    """

    summary_sql = f"""
      SELECT
        c.metric_id,
        m.display_name AS metric_display_name,
        MIN(c.value) AS min_value,
        MAX(c.value) AS max_value,
        SUM(c.value * ({weight_case})) / NULLIF(SUM({weight_case}), 0) AS weighted_avg
      FROM climate_data c
      JOIN metrics m ON c.metric_id = m.id
      WHERE {" AND ".join(where)}
      GROUP BY c.metric_id
      ORDER BY c.metric_id;
    """

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(summary_sql, tuple(params))
    summary_rows = cursor.fetchall()

    dist_sql = f"""
      SELECT
        c.metric_id,
        c.quality,
        COUNT(*) AS count
      FROM climate_data c
      WHERE {" AND ".join(where)}
      GROUP BY c.metric_id, c.quality
      ORDER BY c.metric_id;
    """
    cursor.execute(dist_sql, tuple(params))
    dist_rows = cursor.fetchall()
    cursor.close()
    conn.close()

    dist_map = {}
    for r in dist_rows:
        mid = r["metric_id"]
        q   = r["quality"]
        cnt = r["count"]
        dist_map.setdefault(mid, {})[q] = cnt

    data = []
    for s in summary_rows:
        mid = s["metric_id"]
        qdist = {
            "excellent":    dist_map.get(mid, {}).get("excellent", 0),
            "good":         dist_map.get(mid, {}).get("good", 0),
            "questionable": dist_map.get(mid, {}).get("questionable", 0),
            "poor":         dist_map.get(mid, {}).get("poor", 0),
        }
        data.append({
            "metric_id":           mid,
            "metric_display_name": s["metric_display_name"],
            "min":                 s["min_value"],
            "max":                 s["max_value"],
            "weighted_avg":        float(s["weighted_avg"]) if s["weighted_avg"] is not None else None,
            "quality_distribution": qdist
        })

    return jsonify({"data": data})


@app.route("/api/v1/trends", methods=["GET"])
def get_trends():
    args          = request.args
    loc_name      = args.get("location_id", type=str)
    metric_name   = args.get("metric", type=str)
    start_date    = parse_date(args.get("start_date"))
    end_date      = parse_date(args.get("end_date"))

    # Parse quality_threshold as a string key → numeric threshold
    q_thresh_key = args.get("quality_threshold", type=str)
    q_thresh_val = None
    if q_thresh_key:
        q_thresh_key = q_thresh_key.lower()
        if q_thresh_key not in QUALITY_WEIGHTS:
            return (
                jsonify({
                    "error": "quality_threshold must be one of: excellent, good, questionable, poor"
                }),
                400
            )
        q_thresh_val = QUALITY_WEIGHTS[q_thresh_key]

    # Build SQL to fetch raw data (date, value, metric_name, unit, quality)
    sql = """
      SELECT
        c.date AS date_col,
        c.value,
        c.quality,
        m.name AS metric_name,
        m.unit
      FROM climate_data c
      JOIN locations l ON c.location_id = l.id
      JOIN metrics m ON c.metric_id = m.id
      WHERE 1=1
    """
    params = []

    if loc_name:
        sql += " AND l.name = %s"
        params.append(loc_name)

    if metric_name:
        sql += " AND m.name = %s"
        params.append(metric_name)

    if start_date:
        sql += " AND c.date >= %s"
        params.append(start_date)

    if end_date:
        sql += " AND c.date <= %s"
        params.append(end_date)

    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Apply quality_threshold filtering if provided
    if q_thresh_val is not None:
        rows = [
            r for r in rows
            if QUALITY_WEIGHTS.get(r["quality"].lower(), 0.0) >= q_thresh_val
        ]

    # Group rows by metric_name
    grouped = {}
    for r in rows:
        metric = r["metric_name"]
        if metric not in grouped:
            grouped[metric] = {
                "unit": r["unit"],
                "points": []
            }

        raw_date = r["date_col"]
        # If raw_date is a string, parse; if it's a date object, use it directly.
        if isinstance(raw_date, str):
            try:
                dt = datetime.strptime(raw_date, "%Y-%m-%d").date()
            except ValueError:
                continue
        elif isinstance(raw_date, date):
            dt = raw_date
        else:
            # If for some reason it’s a datetime.datetime, convert to date
            try:
                dt = raw_date.date()
            except Exception:
                continue

        grouped[metric]["points"].append({
            "date": dt,
            "value": float(r["value"]),
            "quality": r["quality"].lower()
        })

    # Prepare final response structure
    result = {}

    for metric, info in grouped.items():
        pts = sorted(info["points"], key=lambda x: x["date"])
        n   = len(pts)
        if n == 0:
            continue

        # Convert dates → ordinals and collect values
        xs = [p["date"].toordinal() for p in pts]
        ys = [p["value"] for p in pts]

        # Compute linear regression (slope, intercept, R^2)
        mean_x = statistics.mean(xs)
        mean_y = statistics.mean(ys)

        sum_xy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
        sum_x2 = sum((x - mean_x) ** 2 for x in xs)
        slope = sum_xy / sum_x2 if sum_x2 != 0 else 0.0
        intercept = mean_y - (slope * mean_x)

        ss_tot = sum((y - mean_y) ** 2 for y in ys)
        ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
        r_squared = (1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
        r_squared = max(0.0, r_squared)

        # Convert slope (units/day) → rate/month (≈30 days)
        rate_per_month = slope * 30
        if abs(rate_per_month) < 1e-6:
            direction = "stable"
        elif rate_per_month > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        trend_obj = {
            "direction": direction,
            "rate": round(rate_per_month, 3),
            "unit": info["unit"],
            "confidence": round(r_squared, 3)
        }

        # Detect anomalies: |value - mean| > 3 * std_dev
        anomalies = []
        if n > 1:
            std_dev = statistics.stdev(ys)
            for p in pts:
                deviation = 0.0
                if std_dev > 0:
                    deviation = (p["value"] - mean_y) / std_dev
                # Change threshold from 3 to 2:
                if abs(deviation) > 2:
                    anomalies.append({
                        "date": p["date"].strftime("%Y-%m-%d"),
                        "value": p["value"],
                        "deviation": round(deviation, 2)
                    })
                    
        # Seasonality detection (group by year & season)
        season_data = {}  # {(year, season): [values]}
        for p in pts:
            yr     = p["date"].year
            season = month_to_season(p["date"].month)
            key    = (yr, season)
            season_data.setdefault(key, []).append(p["value"])

        # Compute per-year–per-season averages
        per_year_season_avg = {}
        for (yr, season), vals in season_data.items():
            per_year_season_avg.setdefault(season, []).append({
                "year": yr,
                "avg": statistics.mean(vals)
            })

        # Check if span ≥ 365 days → seasonality detected
        detected = (pts[-1]["date"] - pts[0]["date"]).days >= 365

        # Build pattern for each season
        pattern = {}
        for season, entries in per_year_season_avg.items():
            entries.sort(key=lambda x: x["year"])
            avg_all = round(statistics.mean(e["avg"] for e in entries), 2)

            if len(entries) > 1:
                xs_s = [e["year"] for e in entries]
                ys_s = [e["avg"]  for e in entries]
                mean_xs = statistics.mean(xs_s)
                mean_ys = statistics.mean(ys_s)

                sum_xy_s = sum((x - mean_xs)*(y - mean_ys) for x, y in zip(xs_s, ys_s))
                sum_x2_s = sum((x - mean_xs)**2 for x in xs_s)
                slope_s = sum_xy_s / sum_x2_s if sum_x2_s != 0 else 0.0

                if abs(slope_s) < 1e-6:
                    trend_s = "stable"
                elif slope_s > 0:
                    trend_s = "increasing"
                else:
                    trend_s = "decreasing"
            else:
                trend_s = "stable"

            pattern[season] = {
                "avg": avg_all,
                "trend": trend_s
            }

        seasonality_obj = {
            "detected": detected,
            "period": "yearly" if detected else None,
            "confidence": round(r_squared, 3) if detected else None,
            "pattern": pattern
        }

        result[metric] = {
            "trend":       trend_obj,
            "anomalies":   anomalies,
            "seasonality": seasonality_obj
        }

    return jsonify(result)

if __name__ == "__main__":
    # Create tables + seed data on startup
    init_db()
    app.run(debug=True)
