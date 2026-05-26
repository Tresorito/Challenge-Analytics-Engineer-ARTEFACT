import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker
from textblob import TextBlob
from rich.console import Console

console = Console()
fake = Faker(["en_US"])
ROOT  = Path(__file__).parent.parent
RAW   = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
XLSX  = RAW / "air_cote_divoire_starter_dataset.xlsx"


REVIEWS_POS = [
    "Excellent flight, very professional and attentive crew.",
    "Great value for money on this West African route.",
    "On time, comfortable seats, I highly recommend Air Cote d'Ivoire.",
    "Outstanding service on board, quality meal on the long haul flight.",
    "Friendly staff, fast boarding, smooth experience overall.",
    "The new A330 fleet is really comfortable for the Paris route.",
    "Impeccable service, very comfortable business class seat.",
    "Smooth flight, great legroom, will definitely fly again.",
]
REVIEWS_NEU = [
    "Decent flight but nothing exceptional. Service could be improved.",
    "45 minute delay at departure but courteous staff.",
    "Average food for an international flight. Needs improvement.",
    "Narrow seat in economy on the long haul flight.",
    "Slow check-in process, staff seemed disorganized at the gate.",
    "Flight was fine but the wifi was not working.",
    "Acceptable experience, nothing stood out positively or negatively.",
]
REVIEWS_NEG = [
    "Three hour delay with no explanation. Customer service was nonexistent.",
    "Lost luggage, no response from customer service after 5 days.",
    "Last minute cancellation, refund still pending after two weeks.",
    "Broken seat, faulty tray table, indifferent cabin crew.",
    "Very disappointed with the service on this strategic route.",
    "Air conditioning was broken for the entire flight. Unacceptable.",
    "Staff was rude when I requested an upgrade at the gate.",
    "Flight was overbooked and handling was chaotic and unprofessional.",
]
TICKET_TEXTS = [
    ("baggage", "Luggage was damaged on arrival. Suitcase handle completely broken."),
    ("baggage", "Bag lost on the ABJ connection. No updates after 3 days."),
    ("baggage", "Extra baggage fee charged twice. Requesting immediate refund."),
    ("delay",   "Flight delayed by 2 hours with no proactive communication from the airline."),
    ("delay",   "Missed connecting flight due to delay. Hotel expenses incurred."),
    ("delay",   "Recurring delays on this route. Reliability is simply not acceptable."),
    ("refund",  "Flight cancelled but voucher not received. Reference pending."),
    ("refund",  "Refund requested 3 weeks ago. Still no response from the team."),
    ("service", "Meal not served in business class on this flight."),
    ("service", "Promised upgrade was not honored at boarding. Very disappointing."),
    ("service", "No staff present at the boarding gate. Completely disorganized."),
]


def score_sentiment(text):
    try:
        s = TextBlob(text).sentiment.polarity
    except Exception:
        s = 0.0
    label = "positive" if s > 0.15 else ("negative" if s < -0.15 else "neutral")
    return round(s, 4), label



def load_excel():
    if not XLSX.exists():
        console.print(f"[red]ERREUR : fichier introuvable : {XLSX}[/red]")
        console.print("[yellow]Place le fichier air_cote_divoire_starter_dataset.xlsx dans data/raw/[/yellow]")
        raise FileNotFoundError(str(XLSX))

    airports  = pd.read_excel(XLSX, sheet_name="Airports")
    routes    = pd.read_excel(XLSX, sheet_name="Routes")
    customers = pd.read_excel(XLSX, sheet_name="Customers")
    flights   = pd.read_excel(XLSX, sheet_name="Flights")
    bookings  = pd.read_excel(XLSX, sheet_name="Bookings")

    console.print(f"  [green]✓[/green] {len(airports)} aéroports")
    console.print(f"  [green]✓[/green] {len(routes)} routes")
    console.print(f"  [green]✓[/green] {len(customers)} clients")
    console.print(f"  [green]✓[/green] {len(flights)} vols")
    console.print(f"  [green]✓[/green] {len(bookings)} réservations")
    return airports, routes, customers, flights, bookings



def enrich_customers(customers_df, seed=42):
    rng = np.random.default_rng(seed)
    df  = customers_df.copy()

    if "customer_segment" in df.columns:
        df = df.rename(columns={"customer_segment": "segment"})

    if "preferred_cabin" not in df.columns:
        df["preferred_cabin"] = df["segment"].apply(
            lambda s: "business" if str(s).lower() in ("business","premium") else "economy"
        )
    if "loyalty_member" not in df.columns:
        df["loyalty_member"] = df["loyalty_tier"].notna()
    if "age" not in df.columns and "birth_date" in df.columns:
        df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
        df["age"] = ((datetime.now() - df["birth_date"]).dt.days / 365).astype(int)

    console.print(f"  [green]✓[/green] Clients enrichis ({len(df)} lignes)")
    return df


def enrich_flights(flights_df, routes_df, seed=42):
    rng = np.random.default_rng(seed)
    df  = flights_df.copy()

    df = df.merge(
        routes_df[["route_id","distance_km","route_type"]],
        on="route_id", how="left"
    )

    if "total_revenue_usd" not in df.columns:
        fare_map = {"Domestic": 90, "Regional": 200, "International": 600}
        df["avg_fare"] = df["route_type"].map(fare_map).fillna(150)
        pax_estimate   = (df["seat_capacity"] * 0.78).astype(int)
        df["total_revenue_usd"] = (pax_estimate * df["avg_fare"] * rng.uniform(0.8,1.2, len(df))).round(2)
        df["op_cost_usd"]       = (df["total_revenue_usd"] * rng.uniform(0.55,0.75, len(df))).round(2)
        df["fuel_cost_usd"]     = (df["op_cost_usd"] * 0.42).round(2)
        df["pax_boarded"]       = pax_estimate
        df["load_factor"]       = (pax_estimate / df["seat_capacity"]).round(4)
        df.drop(columns=["avg_fare"], inplace=True)

    if "is_delayed" not in df.columns and "flight_status" in df.columns:
        df["is_delayed"]   = df["flight_status"].str.lower().str.contains("delay")
        df["is_cancelled"] = df["flight_status"].str.lower().str.contains("cancel")

    if "delay_minutes" not in df.columns and "delay_min" in df.columns:
        df = df.rename(columns={"delay_min": "delay_minutes"})

    console.print(f"  [green]✓[/green] Vols enrichis ({len(df)} lignes)")
    return df


def gen_reviews(bookings_df, n=3000, seed=42):
    rng   = np.random.default_rng(seed)
    rows  = []
    tmpl  = {"positive": REVIEWS_POS, "neutral": REVIEWS_NEU, "negative": REVIEWS_NEG}
    sents = rng.choice(["positive","neutral","negative"], size=n, p=[0.40,0.30,0.30])
    sample = bookings_df.sample(n=min(n, len(bookings_df)), replace=True, random_state=42)

    for i, (_, b) in enumerate(sample.iterrows()):
        sent = sents[i]
        text = str(rng.choice(tmpl[sent]))
        sc, lb = score_sentiment(text)
        rows.append({
            "review_id":       f"REV{i+1:06d}",
            "booking_id":      b["booking_id"],
            "customer_id":     b["customer_id"],
            "flight_id":       b["flight_id"],
            "review_date":     b["booking_date"] if isinstance(b["booking_date"], str)
                               else pd.to_datetime(b["booking_date"]).strftime("%Y-%m-%d"),
            "rating":          int(rng.choice([1,2,3,4,5],
                               p=[0.08,0.12,0.20,0.30,0.30] if sent=="positive" else
                               ([0.30,0.30,0.20,0.12,0.08]  if sent=="negative" else
                                [0.05,0.15,0.50,0.20,0.10]))),
            "review_text":     text,
            "sentiment_score": sc,
            "sentiment_label": lb,
            "cabin":           b.get("fare_class", "Economy"),
        })

    df = pd.DataFrame(rows)
    console.print(f"  [green]✓[/green] {len(df):,} avis clients générés")
    return df


def gen_tickets(customers_df, flights_df, n=2000, seed=42):
    rng  = np.random.default_rng(seed)
    rows = []
    cids = customers_df["customer_id"].values
    fids = flights_df["flight_id"].values

    for i in range(n):
        cat, text = TICKET_TEXTS[int(rng.integers(0, len(TICKET_TEXTS)))]
        sc, lb = score_sentiment(text)
        rows.append({
            "ticket_id":       f"TKT{i+1:06d}",
            "customer_id":     rng.choice(cids),
            "flight_id":       rng.choice(fids),
            "category":        cat,
            "ticket_text":     text,
            "sentiment_score": sc,
            "sentiment_label": lb,
            "severity":        rng.choice(["low","medium","high","critical"], p=[0.30,0.40,0.20,0.10]),
            "status":          rng.choice(["open","in_progress","resolved","closed"], p=[0.15,0.20,0.40,0.25]),
            "created_at":      fake.date_between(start_date="-12m", end_date="today").strftime("%Y-%m-%d"),
            "resolution_days": int(rng.choice([1,3,5,7,14,30], p=[0.15,0.25,0.25,0.15,0.12,0.08])),
        })

    df = pd.DataFrame(rows)
    console.print(f"  [green]✓[/green] {len(df):,} tickets support générés")
    return df


def gen_loyalty(customers_df, bookings_df, seed=42):
    rng  = np.random.default_rng(seed)
    rows = []
    members = customers_df[customers_df["loyalty_member"] == True]["customer_id"].values
    bk_by_cust = bookings_df.groupby("customer_id")

    for i, cid in enumerate(members):
        if cid not in bk_by_cust.groups:
            continue
        for _, bk in bk_by_cust.get_group(cid).iterrows():
            price = float(bk.get("ticket_price_usd", 100))
            miles = int(price * rng.choice([3,5,8], p=[0.40,0.40,0.20]))
            rows.append({
                "loyalty_id":     f"LOY{len(rows)+1:07d}",
                "customer_id":    cid,
                "booking_id":     bk["booking_id"],
                "transaction_date": bk["booking_date"] if isinstance(bk["booking_date"], str)
                                    else pd.to_datetime(bk["booking_date"]).strftime("%Y-%m-%d"),
                "miles_earned":   miles,
                "miles_redeemed": int(miles * rng.choice([0, 0.5, 1.0], p=[0.60,0.25,0.15])),
                "activity_type":  rng.choice(["flight","partner_hotel","bonus_campaign"], p=[0.75,0.15,0.10]),
            })

    df = pd.DataFrame(rows)
    console.print(f"  [green]✓[/green] {len(df):,} transactions loyalty générées")
    return df


def main():
    random.seed(42)
    np.random.seed(42)

    airports_df, routes_df, customers_df, flights_df, bookings_df = load_excel()

    customers_df = enrich_customers(customers_df)
    flights_df   = enrich_flights(flights_df, routes_df)

    reviews_df = gen_reviews(bookings_df)
    tickets_df = gen_tickets(customers_df, flights_df)
    loyalty_df = gen_loyalty(customers_df, bookings_df)

    datasets = {
        "airports":         airports_df,
        "routes":           routes_df,
        "customers":        customers_df,
        "flights":          flights_df,
        "bookings":         bookings_df,
        "customer_reviews": reviews_df,
        "support_tickets":  tickets_df,
        "loyalty_activity": loyalty_df,
    }
    for name, df in datasets.items():
        path = RAW / f"{name}.csv"
        df.to_csv(path, index=False)
        console.print(f"  [green]✓[/green] {name}.csv — {len(df):,} lignes")

    console.rule("[bold green]Terminé ![/bold green]")


if __name__ == "__main__":
    main()