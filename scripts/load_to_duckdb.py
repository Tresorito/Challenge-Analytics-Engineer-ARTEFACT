import os
import duckdb
from rich.console import Console
from rich.table import Table

console = Console()

RAW     = "data/raw"
DB_PATH = "warehouse/air_civ.duckdb"

TABLES = [
    "airports",
    "routes",
    "customers",
    "flights",
    "bookings",
    "customer_reviews",
    "support_tickets",
    "loyalty_activity",
]


def main():

    con = duckdb.connect(DB_PATH)

    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for table in TABLES:
        csv_path = f"{RAW}/{table}.csv"

        if not os.path.exists(csv_path):
            console.print(f"[red]ABSENT :[/red] {csv_path}")
            continue

        con.execute(f"DROP TABLE IF EXISTS raw.{table}")

        con.execute(f"""
            CREATE TABLE raw.{table} AS
            SELECT * FROM read_csv_auto('{csv_path}', header=True)
        """)

        count = con.execute(f"SELECT COUNT(*) FROM raw.{table}").fetchone()[0]
        cols  = len(con.execute(f"DESCRIBE raw.{table}").fetchall())

        console.print(f"[green]OK :[/green] {table} ({count} rows, {cols} cols)")

    con.close()
    console.rule("[bold green]DuckDB prêt ![/bold green]")
    console.print(f"Fichier : [cyan]{DB_PATH}[/cyan]")


if __name__ == "__main__":
    main()