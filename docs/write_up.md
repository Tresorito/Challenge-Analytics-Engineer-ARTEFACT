# Write-up — Air Côte d'Ivoire Analytics Challenge
Candidat :Trésor  
Date :02 Juin 2026  

1. Compréhension du problème

Question décisionnelle
Où Air Côte d'Ivoire doit-elle investir son budget sur les 12 prochains
mois pour maximiser la croissance profitable ?

Trois axes analysés :
- Expansion et optimisation des routes
- Rétention client
- Upsell et cross-sell ancillaire

Parties prenantes identifiées
- Direction générale → décision budgétaire globale
- Direction réseau → expansion et fréquences
- Direction commerciale → rétention et upsell
- Direction opérations → fiabilité et ponctualité



2. Données

Starter dataset (données réelles): air_cote_divoire_starter_datase


Données générées (enrichissement) : enrich_data.py

Hypothèses sur les données
- Les coûts opérationnels sont estimés à 62% du revenue
  (ratio IATA compagnies aériennes africaines 2024)
- Le sentiment NLP est calculé avec TextBlob sur des textes
  en anglais générés de façon réaliste
- Le churn score combine 3 signaux binaires :
  baisse de vols récents, tickets ouverts, note faible



3. Architecture technique

Stack choisie 1 : Python → DuckDB → dbt → Power BI → MCP (FastAPI)

Stack choisie 2 : Python → DuckDB → dbt → Power BI → Power BI Copilot

Choix de modélisation — Star Schema

Nous avons opté pour un star schema organisé en 3 couches dbt
pour les raisons suivantes :

1. **Volume** — moins de 12 000 lignes ne justifie pas
   la complexité d'un Data Vault
2. **Objectif** — dashboard analytique décisionnel,
   pas système d'audit ou de traçabilité
3. **Power BI** — optimisé nativement pour le star schema
4. **Timeline** — livraison rapide avec dbt Core

Le Data Vault aurait été pertinent pour historiser les changements
de segments clients ou intégrer des sources temps réel (Amadeus, Sabre).

Couches dbt
Staging      → nettoyage, typage, renommage
Intermediate → calculs LTV, churn, NPS, métriques routes
Marts        → tables finales Power BI (dim + fact)

### Tables du modèle
**Dimensions :** dim_customers, dim_routes, dim_airports  
**Faits :** fact_bookings, fact_flights  
**Agrégats :** int_customer_metrics, int_route_metrics  
**Marts :** mart_customer_segments, mart_route_performance

---

4. KPIs définis

Réseau :
- Load Factor    = pax_boarded / seat_capacity  (seuil > 70%)
- Yield par pax  = revenue total / pax boarded
- Taux de retard = vols retardés / total vols   (seuil < 20%)
- Marge brute    = revenue × 38% (ratio IATA)
- NPS proxy      = (promoteurs - détracteurs) / total × 100

Clients :
- LTV            = total fares + ancillary revenue
- Churn score    = somme 3 signaux binaires (0-3)
- Attach rate    = revenue ancillaire / revenue billet

5. Données non-structurées

Deux sources NLP ont été intégrées :

customer_reviews — avis clients
- 3 000 avis générés avec des templates réalistes en anglais
- Scoring de sentiment avec TextBlob (-1 à +1)
- Classification : positive / neutral / negative
- NPS proxy calculé depuis le rating (1-5 étoiles)

support_tickets — tickets support
- 2 000 tickets couvrant 4 catégories : baggage, delay, refund, service
- Sentiment scoré automatiquement
- Agrégé par route pour identifier les problèmes opérationnels

Intégration dans dbt :
- Joint aux vols via flight_id
- Agrégé par route dans int_route_metrics
- Contribue au churn_score dans int_customer_metrics

---

6. Dashboard Power BI

Page 1 — Réseau & Rentabilité
Revenue total, marge, load factor, taux de retard.
Scatter plot Load Factor vs Marge — matrice de décision routes.
Tableau avec colonne Action (DAX) basée sur load factor + NPS.

Page 2 — Clients & Rétention
LTV moyenne, clients à risque (churn_score ≥ 2), LTV menacée.
Scatter LTV vs churn score.
Tableau top clients à contacter en priorité.

Page 3 — Upsell & Ancillaires
Revenue ancillaire, attach rate (5.66% vs benchmark 15-20%).
Attach rate par segment et par cabin.
Clients à fort potentiel upsell.

Page 4 — Décision & Recommandations
Synthèse des 3 axes avec allocation budgétaire recommandée :
- Rétention : 45% ($3.12M de LTV menacée)
- Routes : 35% (4 routes performantes à développer)
- Upsell : 20% (attach rate 5.66% vs 15-20% benchmark)

---

7. Interface IA agentique (MCP)

Architecture
Claude API
↓ appelle
FastAPI (mcp_server/main.py)
↓ interroge
DuckDB (warehouse/air_civ.duckdb)
↓ retourne
Réponse chiffrée en français

4 outils exposés
/routes | Quelles routes méritent plus de budget ? 
/clients_a_risque | Quels clients sont à risque de churn ? 
/upsell | Quel potentiel upsell par segment ? 
/resume | Où investir le budget en priorité ? 

Démonstration
Claude appelle automatiquement les outils pertinents,
récupère les données réelles DuckDB et formule des
recommandations chiffrées et actionnables.

---

8. Recommandation finale

Question : Où investir le budget en priorité ?**

Priorité 1 — Rétention clients (45%)
207 clients représentant $3.12M de LTV sont à risque.
Signal : churn_score ≥ 2 (baisse de vols + tickets ouverts + note faible).
Action : Programme de rétention ciblé — résolution prioritaire
des tickets, offres personnalisées, miles bonus.

Priorité 2 — Expansion routes (35%)
ABJ→CDG (38% du revenue) et ABJ→LOS (meilleur taux de retard régional)
sont les routes à développer en priorité.
Action : +1 fréquence hebdomadaire sur CDG = ~$93K revenue additionnel.

Priorité 3 — Upsell ancillaires (20%)
Attach rate de 5.66% vs benchmark industrie 15-20%.
76 clients identifiés avec fort potentiel upsell.
Action : Campagne ciblée = gain estimé $187K additionnel.

---

9. Limitations

- Volume de données faible — 300 clients et 480 vols
  limitent la robustesse statistique des modèles de churn
- Données synthétiques — les avis et tickets sont générés,
  pas des données réelles de clients Air CI
- Load factor homogène — toutes les routes affichent ~78%
  car la génération n'intègre pas de facteurs
  de performance par route
- Coûts estimés — les coûts opérationnels sont basés
  sur un ratio IATA (62%) et non des données réelles
- Pas de données temporelles longues — 6 mois de données
  ne permettent pas d'analyser la saisonnalité complète

---

10. Next Steps

Avec plus de temps et de ressources :

1. Données réelles — intégrer les vrais GDS (Amadeus/Sabre)
   pour des coûts et revenus précis
2. ML churn — remplacer le churn score par un modèle
   de classification (Random Forest, XGBoost)
3. NLP avancé — utiliser un modèle transformer fine-tuné
   sur le secteur aérien africain
5. Ontologie formelle — implémenter OWL/SHACL
   pour des règles d'inférence métier robustes
6. Data Vault — migrer vers Data Vault 2.0
   si intégration de sources multiples (Amadeus, Navitaire)

---

11. Instructions de setup

```bash
git clone https://github.com/Tresorito/Challenge-Analytics-Engineer-ARTEFACT.git
cd Challenge-Analytics-Engineer-ARTEFACT
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
pip install "dbt-duckdb==1.8.1" "dbt-core==1.8.1"
pip install faker pandas numpy textblob duckdb rich openpyxl fastapi uvicorn anthropic python-dotenv httpx

# Copier le fichier Excel dans data/raw/
python scripts/generate_data.py
python scripts/load_to_duckdb.py
cd air_civ_analytics_project && dbt run --profiles-dir . && cd ..
python scripts/export_for_powerbi.py

# Serveur MCP
uvicorn mcp_server.main:app --port 8000
python mcp_server/chat.py
```