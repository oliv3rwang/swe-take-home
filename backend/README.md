# EcoVision – Python Backend

This repository contains the Flask-based backend for **EcoVision: Climate Visualizer**. It provides RESTful endpoints to query, summarize, and analyze climate data stored in a MySQL database. On startup, it automatically creates required tables (if missing) and seeds them with sample data.

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
   - [1. Clone & Create venv](#1-clone--create-venv)
   - [2. Install Dependencies](#2-install-dependencies)
   - [3. Configure MySQL](#3-configure-mysql)
   - [4. Environment Variables](#4-environment-variables)
   - [5. Run the Server (Auto-seed)](#5-run-the-server-auto-seed)
5. [API Endpoints](#api-endpoints)
   - [`GET /api/v1/locations`](#get-apiv1locations)
   - [`GET /api/v1/metrics`](#get-apiv1metrics)
   - [`GET /api/v1/climate`](#get-apiv1climate)
   - [`GET /api/v1/summary`](#get-apiv1summary)
   - [`GET /api/v1/trends`](#get-apiv1trends)
6. [Database Schema & Seeding](#database-schema--seeding)
7. [Design Decisions & Notes](#design-decisions--notes)
8. [Folder Structure](#folder-structure)

---

## Overview

On startup, the Flask app:

1. **Creates** three tables (if they don’t exist):

   - `locations`
   - `metrics`
   - `climate_data`

2. **Loads** `data/sample_data.json` and **inserts/updates** all entries into those tables using `ON DUPLICATE KEY UPDATE`.

3. Exposes these read-only endpoints:
   - **`/api/v1/locations`** → all locations
   - **`/api/v1/metrics`** → all metrics
   - **`/api/v1/climate`** → raw climate readings (with filters & pagination)
   - **`/api/v1/summary`** → quality-weighted min, max, avg, quality distribution
   - **`/api/v1/trends`** → trend direction, rate, anomalies, and seasonality

All logic lives in `app.py`; no external migrations or CLI scripts are needed.

---

## Tech Stack

- **Python 3.11+**
- **Flask 3.1+** (web server)
- **flask-cors** (enable CORS on all routes)
- **mysql-connector-python** (pure-Python MySQL driver)
- **MySQL 8.x** (relational database)
- **Statistics** (built-in module for regression, stdev, etc.)

---

## Prerequisites

1. **Python 3.11+** installed on your machine.
2. **MySQL Server 8.x** running locally (or accessible remotely).
3. Basic familiarity with virtual environments (`venv`).
4. `git`, `pip`, and `mysql` client tools installed.

---

## Installation & Setup

### 1. Clone & Create venv

```bash
git clone https://github.com/oliv3rwang/ecovision-backend.git
cd ecovision-backend/backend
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# OR
.\venv\Scripts\activate         # Windows PowerShell
```

### 2. Install Dependencies

```
pip install Flask flask-cors mysql-connector-python
```

### 3. Configure MySQL

Ubuntu/WSL:

```
sudo apt update
sudo apt install -y mysql-server
sudo service mysql start
```

macOS (Homebrew):

```
brew update
brew install mysql
brew services start mysql
```

### 4. Environment Variables

Before running, export these (replace values as needed):

```
bash
Copy
Edit
export MYSQL_USER=root
export MYSQL_PASSWORD=test
export MYSQL_HOST=127.0.0.1
export MYSQL_DB=climate_data
export MYSQL_PORT=3306
```

### 5. Run the Server (Auto-seed)

```
python app.py
```
