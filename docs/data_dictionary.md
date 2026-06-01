# Data Dictionary — Air Côte d'Ivoire Analytics

## Tables de faits

### fact_bookings (11 475 lignes)
| Colonne | Type | Description |
|---|---|---|
| booking_id | VARCHAR | Identifiant unique réservation (PK) |
| flight_id | VARCHAR | Lien vers fact_flights (FK) |
| customer_id | VARCHAR | Lien vers dim_customers (FK) |
| route_id | VARCHAR | Lien vers dim_routes (FK) |
| fare_family_id | VARCHAR | Famille tarifaire |
| booking_date | DATE | Date de réservation |
| flight_date | DATE | Date du vol |
| fare_paid_usd | DOUBLE | Montant billet en USD |
| ancillary_revenue_usd | DOUBLE | Revenus ancillaires en USD |
| total_revenue_usd | DOUBLE | fare + ancillaire | 
| cabin | VARCHAR | economy / business |
| channel | VARCHAR | web / mobile / agency / call_center |
| booking_status | VARCHAR | Statut de la réservation |

### fact_flights (480 lignes)
| Colonne | Type | Description |
|---|---|---|
| flight_id | VARCHAR | Identifiant unique vol (PK) |
| route_id | VARCHAR | Lien vers dim_routes (FK) |
| flight_date | DATE | Date du vol |
| aircraft_type | VARCHAR | Type d'avion |
| seat_capacity | INTEGER | Capacité totale de l'avion |
| pax_boarded | INTEGER | Passagers embarqués |
| load_factor | DOUBLE | pax_boarded / seat_capacity |
| delay_minutes | INTEGER | Retard en minutes |
| is_delayed | BOOLEAN | Vrai si retard ≥ 15 min |
| is_cancelled | BOOLEAN | Vrai si vol annulé |
| total_revenue_usd | DOUBLE | Revenue estimé du vol |
| op_cost_usd | DOUBLE | Coût opérationnel estimé |
| gross_margin_usd | DOUBLE | Revenue - coût opérationnel |
| delay_category | VARCHAR | on_time / minor / significant / major |

---

## Dimensions

### dim_customers (300 lignes)
| Colonne | Type | Description |
|---|---|---|
| customer_id | VARCHAR | Identifiant unique client (PK) |
| first_name | VARCHAR | Prénom |
| last_name | VARCHAR | Nom |
| segment | VARCHAR | Budget / Standard / Premium / Business |
| country | VARCHAR | Pays de résidence |
| age | INTEGER | Âge du client |
| age_group | VARCHAR | 18-24 / 25-34 / 35-44 / 45-54 / 55+ |
| loyalty_member | BOOLEAN | Membre du programme loyalty |
| loyalty_tier | VARCHAR | Explorer / Silver / Gold / Platinum |
| preferred_cabin | VARCHAR | economy / business |

### dim_routes (12 lignes)
| Colonne | Type | Description |
|---|---|---|
| route_id | VARCHAR | Identifiant unique route (PK) |
| origin | VARCHAR | Code IATA aéroport départ |
| destination | VARCHAR | Code IATA aéroport arrivée |
| route_type | VARCHAR | Domestic / Regional / International |
| distance_km | INTEGER | Distance en kilomètres |
| is_strategic | BOOLEAN | Route prioritaire réseau |
| route_label | VARCHAR | Ex: "ABJ → CDG" |
| distance_category | VARCHAR | short / medium / long |

### dim_airports (10 lignes)
| Colonne | Type | Description |
|---|---|---|
| airport_id | VARCHAR | Code IATA (PK) |
| airport_name | VARCHAR | Nom officiel |
| city | VARCHAR | Ville |
| country | VARCHAR | Pays |
| latitude | DOUBLE | Coordonnée GPS |
| longitude | DOUBLE | Coordonnée GPS |
| is_hub | BOOLEAN | Vrai si hub principal (ABJ) |

---

## Agrégats intermediate

### int_customer_metrics (300 lignes — 1 par client)
| Colonne | Type | Description |
|---|---|---|
| customer_id | VARCHAR | Clé primaire (FK → dim_customers) |
| ltv_usd | DOUBLE | LTV = total fares + ancillaires |
| total_fare_revenue | DOUBLE | Somme des billets achetés |
| total_ancillary_revenue | DOUBLE | Somme des ancillaires achetés |
| total_flights | INTEGER | Nombre total de vols |
| avg_fare_paid | DOUBLE | Tarif moyen payé |
| last_booking_date | DATE | Date de la dernière réservation |
| days_since_last_booking | INTEGER | Jours depuis la dernière réservation |
| bookings_recent | INTEGER | Réservations sur les 9 derniers mois |
| bookings_older | INTEGER | Réservations avant les 9 derniers mois |
| total_miles_earned | INTEGER | Miles loyalty gagnés |
| open_tickets | INTEGER | Tickets support non résolus |
| avg_rating | DOUBLE | Note moyenne avis clients (1-5) |
| avg_review_sentiment | DOUBLE | Score sentiment moyen (-1 à +1) |
| ancillary_attach_rate | DOUBLE | ancillaire / fare revenue |
| churn_signal_flight_drop | INTEGER | 1 si baisse vols > 40% |
| churn_signal_open_tickets | INTEGER | 1 si tickets ouverts ≥ 2 |
| churn_signal_low_rating | INTEGER | 1 si note moyenne ≤ 2 |
| churn_score | INTEGER | Somme des 3 signaux (0-3) |

### int_route_metrics (12 lignes — 1 par route)
| Colonne | Type | Description |
|---|---|---|
| route_id | VARCHAR | Clé primaire (FK → dim_routes) |
| total_revenue_usd | DOUBLE | Revenue réel depuis fact_bookings |
| total_op_cost_usd | DOUBLE | Coût estimé (62% du revenue) |
| gross_margin_usd | DOUBLE | Revenue × 38% |
| avg_load_factor | DOUBLE | Taux de remplissage moyen |
| yield_per_pax_usd | DOUBLE | Revenue / passagers |
| delay_rate | DOUBLE | % vols retardés |
| cancellation_rate | DOUBLE | % vols annulés |
| avg_delay_minutes | DOUBLE | Retard moyen (vols retardés) |
| avg_sentiment | DOUBLE | Sentiment moyen avis clients |
| avg_rating | DOUBLE | Note moyenne avis clients |
| nps_proxy | DOUBLE | (promoteurs - détracteurs) / total × 100 |
| margin_per_flight_usd | DOUBLE | Marge par vol opéré |

---

## Sources non-structurées

### customer_reviews (3 000 lignes)
| Colonne | Type | Description |
|---|---|---|
| review_id | VARCHAR | Identifiant unique avis |
| booking_id | VARCHAR | Lien vers fact_bookings |
| review_text | VARCHAR | Texte libre de l'avis (en anglais) |
| sentiment_score | DOUBLE | Score TextBlob (-1 à +1) |
| sentiment_label | VARCHAR | positive / neutral / negative |
| rating | INTEGER | Note 1-5 étoiles |
| nps_category | VARCHAR | promoter / passive / detractor |

### support_tickets (2 000 lignes)
| Colonne | Type | Description |
|---|---|---|
| ticket_id | VARCHAR | Identifiant unique ticket |
| customer_id | VARCHAR | Client concerné |
| flight_id | VARCHAR | Vol concerné |
| category | VARCHAR | baggage / delay / refund / service |
| ticket_text | VARCHAR | Description du problème (en anglais) |
| sentiment_score | DOUBLE | Score TextBlob (-1 à +1) |
| severity | VARCHAR | low / medium / high / critical |
| status | VARCHAR | open / in_progress / resolved / closed |
| resolution_days | INTEGER | Délai de résolution |

---

## Règles de calcul (KPIs)

| KPI | Formule | Seuil industrie |
|---|---|---|
| Load Factor | pax_boarded / seat_capacity | > 70% |
| Yield par pax | revenue_usd / pax_boarded | — |
| Taux de retard | vols_retardés / total_vols | < 20% |
| Marge brute | revenue × 38% (ratio IATA) | > 0 |
| NPS proxy | (promoteurs - détracteurs) / total × 100 | > 0 |
| LTV | total_fare_revenue + total_ancillary_revenue | — |
| Churn score | signal_drop + signal_tickets + signal_rating | < 2 |
| Attach rate | ancillary_revenue / fare_revenue | 15-20% benchmark |