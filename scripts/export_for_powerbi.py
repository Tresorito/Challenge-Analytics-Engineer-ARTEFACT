import os
import duckdb

DB_PATH     = "warehouse/air_civ.duckdb"
EXPORT_PATH = "powerbi/exports"

os.makedirs(EXPORT_PATH, exist_ok=True)

TABLES = [
    ("main_marts",        "dim_customers"),
    ("main_marts",        "dim_routes"),
    ("main_marts",        "dim_airports"),
    ("main_marts",        "dim_fare_families"),
    ("main_marts",        "fact_bookings"),
    ("main_marts",        "fact_flights"),
    ("main_marts",        "mart_customer_segments"),
    ("main_marts",        "mart_route_performance"),
    ("main_intermediate", "int_customer_metrics"),
    ("main_intermediate", "int_route_metrics"),
]


con = duckdb.connect(DB_PATH, read_only=True)

for schema, table in TABLES:
    output = f"{EXPORT_PATH}/{table}.parquet"
    con.execute(f"""
        COPY (SELECT * FROM {schema}.{table})
        TO '{output}' (FORMAT PARQUET)
    """)
    count = con.execute(
        f"SELECT COUNT(*) FROM {schema}.{table}"
    ).fetchone()[0]
    print(f"  ✓ {table}.parquet — {count:,} lignes")

con.close()

print(f"\nFichiers dans : {EXPORT_PATH}")