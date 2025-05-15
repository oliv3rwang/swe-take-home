# API Specification

This document outlines the API endpoints you should implement for the EcoVision: Climate Visualizer.

## Base URL

All API endpoints are relative to `/api/v1/`.

## Authentication

For this assessment, you don't need to implement authentication.

## Endpoints

### Get Climate Data

```
GET /climate
```

Retrieves climate data based on query parameters.

**Query Parameters:**

- `location_id` (optional): Filter by location ID
- `start_date` (optional): Filter data from this date (format: YYYY-MM-DD)
- `end_date` (optional): Filter data until this date (format: YYYY-MM-DD)
- `metric` (optional): Type of climate data (e.g., temperature, precipitation, humidity)
- `quality_threshold` (optional): Minimum quality level ("poor", "questionable", "good", "excellent")

**Example Response:**

```json
{
  "data": [
    {
      "id": 1,
      "location_id": 123,
      "location_name": "New York",
      "latitude": 40.7128,
      "longitude": -74.0060,
      "date": "2023-01-01",
      "metric": "temperature",
      "value": 3.5,
      "unit": "celsius",
      "quality": "good"
    },
    ...
  ],
  "meta": {
    "total_count": 100,
    "page": 1,
    "per_page": 50
  }
}
```

### Get Locations

```
GET /locations
```

Retrieves all available locations.

**Example Response:**

```json
{
  "data": [
    {
      "id": 123,
      "name": "New York",
      "country": "USA",
      "latitude": 40.7128,
      "longitude": -74.0060
    },
    ...
  ]
}
```

### Get Metrics

```
GET /metrics
```

Retrieves available climate metrics.

**Example Response:**

```json
{
  "data": [
    {
      "id": 1,
      "name": "temperature",
      "display_name": "Temperature",
      "unit": "celsius",
      "description": "Average daily temperature"
    },
    ...
  ]
}
```

### Get Climate Summary

```
GET /summary
```

Retrieves summary statistics for climate data.

**Query Parameters:**

- `location_id` (optional): Filter by location ID
- `start_date` (optional): Filter data from this date (format: YYYY-MM-DD)
- `end_date` (optional): Filter data until this date (format: YYYY-MM-DD)
- `metric` (optional): Type of climate data (e.g., temperature, precipitation, humidity)
- `quality_threshold` (optional): Minimum quality level ("poor", "questionable", "good", "excellent")

**Example Response:**

```json
{
  "data": {
    "temperature": {
      "min": -5.2,
      "max": 35.9,
      "avg": 15.7,
      "weighted_avg": 14.2,
      "unit": "celsius",
      "quality_distribution": {
        "excellent": 0.3,
        "good": 0.5,
        "questionable": 0.1,
        "poor": 0.1
      },
    },
    "precipitation": {
      "min": 0,
      "max": 120.5,
      "avg": 25.3,
      "unit": "mm"
    },
    ...
  }
}
```

### Get Trend Analysis

```
GET /trends
```

Analyze trends and patterns in the climate data.

**Query Parameters:**

- `location_id` (optional): Filter by location ID
- `start_date` (optional): Filter data from this date (format: YYYY-MM-DD)
- `end_date` (optional): Filter data until this date (format: YYYY-MM-DD)
- `metric` (optional): Type of climate data (e.g., temperature, precipitation, humidity)
- `quality_threshold` (optional): Minimum quality level ("poor", "questionable", "good", "excellent")

**Example Response:**

```json
{
  "data": {
    "temperature": {
      "trend": {
        "direction": "increasing",
        "rate": 0.5,
        "unit": "celsius/month",
        "confidence": 0.85
      },
      "anomalies": [
        {
          "date": "2023-06-15",
          "value": 42.1,
          "deviation": 2.5,
          "quality": "excellent"
        }
      ],
      "seasonality": {
        "detected": true,
        "period": "yearly",
        "confidence": 0.92,
        "pattern": {
          "winter": {"avg": 5.2, "trend": "stable"},
          "spring": {"avg": 15.7, "trend": "increasing"},
          "summer": {"avg": 25.3, "trend": "increasing"},
          "fall": {"avg": 18.1, "trend": "stable"}
        }
      }
    },
    ...
  }
}
```


## Implementation Requirements

- Create appropriate database models to support these endpoints
- Implement efficient queries to handle filtering and aggregation
- Implement quality-weighted calculations (weights: excellent=1.0, good=0.8, questionable=0.5, poor=0.3)
- Implement trend detection and anomaly identification
- Ensure proper error handling and validation
- Consider implementing pagination for large datasets