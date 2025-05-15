# app.py - EcoVision: Climate Visualizer API
# This file contains basic Flask setup code to get you started.
# You may opt to use FastAPI or another framework if you prefer.

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# MySQL Configuration
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'climate_data')
mysql = MySQL(app)

# Quality weights to be used in calculations
QUALITY_WEIGHTS = {
    'excellent': 1.0,
    'good': 0.8,
    'questionable': 0.5,
    'poor': 0.3
}

@app.route('/api/v1/climate', methods=['GET'])
def get_climate_data():
    """
    Retrieve climate data with optional filtering.
    Query parameters: location_id, start_date, end_date, metric, quality_threshold
    
    Returns climate data in the format specified in the API docs.
    """
    # TODO: Implement this endpoint
    # 1. Get query parameters from request.args
    # 2. Validate quality_threshold if provided
    # 3. Build and execute SQL query with proper JOINs and filtering
    # 4. Apply quality threshold filtering
    # 5. Format response according to API specification
    
    return jsonify({"data": [], "meta": {"total_count": 0, "page": 1, "per_page": 50}})

@app.route('/api/v1/locations', methods=['GET'])
def get_locations():
    """
    Retrieve all available locations.
    
    Returns location data in the format specified in the API docs.
    """
    # TODO: Implement this endpoint
    # 1. Query the locations table
    # 2. Format response according to API specification
    
    return jsonify({"data": []})

@app.route('/api/v1/metrics', methods=['GET'])
def get_metrics():
    """
    Retrieve all available climate metrics.
    
    Returns metric data in the format specified in the API docs.
    """
    # TODO: Implement this endpoint
    # 1. Query the metrics table
    # 2. Format response according to API specification
    
    return jsonify({"data": []})

@app.route('/api/v1/summary', methods=['GET'])
def get_summary():
    """
    Retrieve quality-weighted summary statistics for climate data.
    Query parameters: location_id, start_date, end_date, metric, quality_threshold
    
    Returns weighted min, max, and avg values for each metric in the format specified in the API docs.
    """
    # TODO: Implement this endpoint
    # 1. Get query parameters from request.args
    # 2. Validate quality_threshold if provided
    # 3. Get list of metrics to summarize
    # 4. For each metric:
    #    - Calculate quality-weighted statistics using QUALITY_WEIGHTS
    #    - Calculate quality distribution
    #    - Apply proper filtering
    # 5. Format response according to API specification
    
    return jsonify({"data": {}})

@app.route('/api/v1/trends', methods=['GET'])
def get_trends():
    """
    Analyze trends and patterns in climate data.
    Query parameters: location_id, start_date, end_date, metric, quality_threshold
    
    Returns trend analysis including direction, rate of change, anomalies, and seasonality.
    """
    # TODO: Implement this endpoint
    # 1. Get query parameters from request.args
    # 2. Validate quality_threshold if provided
    # 3. For each metric:
    #    - Calculate trend direction and rate of change
    #    - Identify anomalies (values > 2 standard deviations)
    #    - Detect seasonal patterns if sufficient data
    #    - Calculate confidence scores
    # 4. Format response according to API specification
    
    return jsonify({"data": {}})

if __name__ == '__main__':
    app.run(debug=True)

# Optional: FastAPI Implementation boilerplate
"""
To implement the API using FastAPI instead of Flask:

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, List, Any
import databases
import os

# Database connection
DATABASE_URL = f"mysql://{os.environ.get('MYSQL_USER', 'root')}:{os.environ.get('MYSQL_PASSWORD', '')}@{os.environ.get('MYSQL_HOST', 'localhost')}/{os.environ.get('MYSQL_DB', 'climate_data')}"
database = databases.Database(DATABASE_URL)

app = FastAPI(title="EcoVision API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Implement endpoints following the API specification in docs/api.md
"""