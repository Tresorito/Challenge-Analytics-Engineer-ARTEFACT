
import duckdb
from fastapi import FastAPI
from pathlib import Path


DB_PATH = Path("warehouse/air_civ.duckdb")
app     = FastAPI(title="Air CI MCP")


def query(sql):
    con  = duckdb.connect(str(DB_PATH), read_only=True)
    data = con.execute(sql).fetchdf().to_dict(orient="records")
    con.close()
    return data


@app.get("/routes")
def get_routes():
    data = query("""
        SELECT
            r.origin || ' → ' || r.destination  AS route,
            r.route_type,
            ROUND(m.avg_load_factor * 100, 1)   AS load_factor_pct,
            ROUND(m.total_revenue_usd, 0)        AS revenue_usd,
            ROUND(m.gross_margin_usd, 0)         AS margin_usd,
            ROUND(m.delay_rate * 100, 1)         AS delay_rate_pct,
            ROUND(m.nps_proxy, 1)                AS nps
        FROM main_intermediate.int_route_metrics m
        JOIN main_marts.dim_routes r ON m.route_id = r.route_id
        ORDER BY m.gross_margin_usd DESC
    """)
    return {"outil": "routes", "données": data}


@app.get("/clients_a_risque")
def get_clients_a_risque():
    data = query("""
        SELECT
            c.first_name || ' ' || c.last_name  AS client,
            c.segment,
            c.country,
            ROUND(m.ltv_usd, 0)                 AS ltv_usd,
            m.churn_score,
            m.open_tickets,
            ROUND(m.avg_rating, 1)              AS note_moyenne
        FROM main_intermediate.int_customer_metrics m
        JOIN main_marts.dim_customers c ON m.customer_id = c.customer_id
        WHERE m.churn_score >= 2
        ORDER BY m.ltv_usd DESC
        LIMIT 20
    """)
    return {"outil": "clients_a_risque", "données": data}


@app.get("/upsell")
def get_upsell():
    data = query("""
        SELECT
            c.segment,
            COUNT(DISTINCT b.booking_id)         AS total_reservations,
            ROUND(SUM(b.fare_paid_usd), 0)       AS revenue_billets,
            ROUND(SUM(b.ancillary_revenue_usd), 0) AS revenue_ancillaires,
            ROUND(
                SUM(b.ancillary_revenue_usd) * 100.0
                / NULLIF(SUM(b.fare_paid_usd), 0), 2
            )                                    AS attach_rate_pct
        FROM main_marts.fact_bookings b
        JOIN main_marts.dim_customers c ON b.customer_id = c.customer_id
        GROUP BY c.segment
        ORDER BY attach_rate_pct DESC
    """)
    return {"outil": "upsell", "données": data}



@app.get("/resume")
def get_resume():
    routes = query("""
        SELECT
            ROUND(SUM(total_revenue_usd), 0)     AS revenue_total,
            ROUND(SUM(gross_margin_usd), 0)      AS marge_totale,
            ROUND(AVG(avg_load_factor) * 100, 1) AS load_factor_moyen,
            COUNT(CASE WHEN avg_load_factor >= 0.75
                       THEN 1 END)               AS routes_performantes
        FROM main_intermediate.int_route_metrics
    """)[0]

    clients = query("""
        SELECT
            COUNT(*)                             AS total_clients,
            ROUND(AVG(ltv_usd), 0)              AS ltv_moyenne,
            COUNT(CASE WHEN churn_score >= 2
                       THEN 1 END)              AS clients_a_risque,
            ROUND(SUM(CASE WHEN churn_score >= 2
                           THEN ltv_usd ELSE 0 END), 0) AS ltv_menacee
        FROM main_intermediate.int_customer_metrics
    """)[0]

    ancillaires = query("""
        SELECT
            ROUND(SUM(ancillary_revenue_usd), 0) AS revenue_ancillaire,
            ROUND(
                SUM(ancillary_revenue_usd) * 100.0
                / NULLIF(SUM(fare_paid_usd), 0), 2
            )                                    AS attach_rate_pct
        FROM main_marts.fact_bookings
    """)[0]

    return {
        "réseau":      routes,
        "clients":     clients,
        "ancillaires": ancillaires,
        "recommandation": {
            "priorité_1": f"Rétention — {clients['clients_a_risque']} clients à risque, {clients['ltv_menacee']}$ menacés",
            "priorité_2": f"Routes — {routes['routes_performantes']} routes performantes à développer",
            "priorité_3": f"Upsell — attach rate actuel {ancillaires['attach_rate_pct']}% vs 15-20% benchmark"
        }
    }



@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "Serveur MCP Air CI opérationnel",
        "outils": ["/routes", "/clients_a_risque", "/upsell", "/resume"]
    }