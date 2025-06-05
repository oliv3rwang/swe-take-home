import os
import json
import math
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector

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

    page     = args.get("page", default=1, type=int)
    per_page = args.get("per_page", default=50, type=int)

    sql    = """
      SELECT
        c.id,
        c.location_id,
        c.metric_id,
        DATE_FORMAT(c.date, '%Y-%m-%d') AS date,
        c.value,
        c.quality
      FROM climate_data c
      WHERE 1=1
    """
    params = []
    if loc_id:
        sql += " AND c.location_id = %s"
        params.append(loc_id)
    if metric_id:
        sql += " AND c.metric_id = %s"
        params.append(metric_id)
    if start_date:
        sql += " AND c.date >= %s"
        params.append(start_date)
    if end_date:
        sql += " AND c.date <= %s"
        params.append(end_date)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, tuple(params))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if q_thresh is not None:
        rows = [r for r in rows if QUALITY_WEIGHTS.get(r["quality"], 0) >= q_thresh]

    # Join location & metric
    for r in rows:
        conn = get_db_connection()
        c1 = conn.cursor(dictionary=True)
        c1.execute("SELECT * FROM locations WHERE id = %s", (r["location_id"],))
        r["location"] = c1.fetchone() or {}
        c1.close()
        conn.close()

        conn = get_db_connection()
        c2 = conn.cursor(dictionary=True)
        c2.execute("SELECT * FROM metrics WHERE id = %s", (r["metric_id"],))
        r["metric"] = c2.fetchone() or {}
        c2.close()
        conn.close()

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
    args         = request.args
    loc_id       = args.get("location_id", type=int)
    metric_param = args.get("metric", type=int)
    start_date   = parse_date(args.get("start_date"))
    end_date     = parse_date(args.get("end_date"))

    try:
        q_thresh = float(args.get("quality_threshold")) if args.get("quality_threshold") is not None else None
        if q_thresh is not None and not (0 <= q_thresh <= 1):
            return jsonify({"error": "quality_threshold must be between 0 and 1"}), 400
    except ValueError:
        return jsonify({"error": "quality_threshold must be a number"}), 400

    where = ["1=1"]
    params = []
    if loc_id:
        where.append("c.location_id = %s")
        params.append(loc_id)
    if metric_param:
        where.append("c.metric_id = %s")
        params.append(metric_param)
    if start_date:
        where.append("c.date >= %s")
        params.append(start_date)
    if end_date:
        where.append("c.date <= %s")
        params.append(end_date)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(f"""
      SELECT
        c.metric_id,
        DATE_FORMAT(c.date, '%Y-%m-%d') AS date_str,
        c.date       AS date_obj,
        c.value,
        c.quality
      FROM climate_data c
      WHERE {" AND ".join(where)}
      ORDER BY c.metric_id, c.date;
    """, tuple(params))
    all_rows = cursor.fetchall()

    per_metric = {}
    for entry in all_rows:
        mid    = entry["metric_id"]
        weight = QUALITY_WEIGHTS.get(entry["quality"], 0)
        if q_thresh is not None and weight < q_thresh:
            continue
        per_metric.setdefault(mid, []).append({
            "date_str": entry["date_str"],
            "date_obj": entry["date_obj"],
            "value":    float(entry["value"]),
            "weight":   weight
        })

    results = []
    for mid, entries in per_metric.items():
        if len(entries) < 2:
            cursor.execute("SELECT display_name FROM metrics WHERE id = %s", (mid,))
            mrow = cursor.fetchone()
            mname = mrow["display_name"] if mrow else None
            results.append({
                "metric_id":           mid,
                "metric_display_name": mname,
                "direction":           None,
                "rate_of_change":      None,
                "anomalies":           [],
                "seasonality":         {},
                "confidence":          None
            })
            continue

        entries.sort(key=lambda e: e["date_obj"])
        n = len(entries)
        x_vals = [e["date_obj"].toordinal() for e in entries]
        y_vals = [e["value"] for e in entries]

        mean_x = sum(x_vals) / n
        mean_y = sum(y_vals) / n
        cov_xy = sum((x_vals[i] - mean_x) * (y_vals[i] - mean_y) for i in range(n))
        var_x  = sum((x_vals[i] - mean_x) ** 2 for i in range(n))
        var_y  = sum((y_vals[i] - mean_y) ** 2 for i in range(n))

        slope = cov_xy / var_x if var_x != 0 else 0.0
        r_coeff = cov_xy / math.sqrt(var_x * var_y) if (var_x > 0 and var_y > 0) else 0.0
        confidence = abs(r_coeff)

        if slope > 0:
            direction = "increasing"
        elif slope < 0:
            direction = "decreasing"
        else:
            direction = "stable"

        std_y = math.sqrt(var_y / n) if n > 0 else 0
        anomalies = [
            entries[i]["date_str"]
            for i in range(n)
            if abs(y_vals[i] - mean_y) > 2 * std_y
        ]

        month_buckets = {}
        for i in range(n):
            month = entries[i]["date_obj"].strftime("%m")
            month_buckets.setdefault(month, []).append(y_vals[i])
        seasonality = {m: sum(vals) / len(vals) for m, vals in month_buckets.items()}

        cursor.execute("SELECT display_name FROM metrics WHERE id = %s", (mid,))
        mrow = cursor.fetchone()
        mname = mrow["display_name"] if mrow else None

        results.append({
            "metric_id":           mid,
            "metric_display_name": mname,
            "direction":           direction,
            "rate_of_change":      slope,
            "anomalies":           anomalies,
            "seasonality":         seasonality,
            "confidence":          confidence
        })

    cursor.close()
    conn.close()
    return jsonify({"data": results})


if __name__ == "__main__":
    # Create tables + seed data on startup
    init_db()
    app.run(debug=True)
