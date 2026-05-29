import json
import httpx
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

BASE = "http://localhost:8000"


def appeler_outil(nom, params={}):
    url = f"{BASE}/{nom}"
    resp = httpx.get(url, params=params, timeout=10)
    return json.dumps(resp.json(), ensure_ascii=False, indent=2)

OUTILS = [
    {
        "name": "get_routes",
        "description": (
            "Retourne les performances financières et opérationnelles "
            "de toutes les routes Air Côte d'Ivoire. "
            "Utilise cet outil pour répondre aux questions sur "
            "les routes rentables, le load factor, les retards."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_clients_a_risque",
        "description": (
            "Retourne les clients avec un churn score élevé "
            "(risque de partir chez un concurrent). "
            "Utilise cet outil pour les questions sur "
            "la rétention et les clients à contacter en priorité."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_upsell",
        "description": (
            "Retourne le potentiel upsell et l'attach rate "
            "ancillaire par segment client. "
            "Utilise cet outil pour les questions sur "
            "les opportunités de ventes additionnelles."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "get_resume",
        "description": (
            "Retourne le résumé exécutif complet, routes, clients, "
            "ancillaires et recommandation budgétaire. "
            "Utilise cet outil pour les questions globales sur "
            "où investir le budget."
        ),
        "input_schema": {
            "type": "object",
            "properties": {}
        }
    }
]


def poser_question(question):
    print(f"\n{'='*60}")
    print(f"QUESTION : {question}")
    print("="*60)

    messages = [{"role": "user", "content": question}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1500,
            system=(
                "Tu es un analyste senior chez Air Côte d'Ivoire. "
                "Tu réponds en français avec des recommandations "
                "concrètes et chiffrées basées sur les données réelles. "
                "Utilise toujours les outils pour accéder aux données "
                "avant de répondre. "
                "Structure ta réponse : Constat → Données clés → Action."
            ),
            tools=OUTILS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_results = []

            for bloc in response.content:
                if bloc.type == "tool_use":
                    nom_outil = bloc.name.replace("get_", "")
                    print(f"\n[OUTIL APPELÉ] {nom_outil}")

                    resultat = appeler_outil(nom_outil)
                    print(f"[DONNÉES REÇUES] {resultat[:200]}...")

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": bloc.id,
                        "content": resultat
                    })

            messages.append({
                "role": "assistant",
                "content": response.content
            })
            messages.append({
                "role": "user",
                "content": tool_results
            })

        elif response.stop_reason == "end_turn":
            for bloc in response.content:
                if hasattr(bloc, "text"):
                    print(f"\nRÉPONSE :\n{bloc.text}")
            break



if __name__ == "__main__":

    questions = [
        "Quelles routes méritent plus de budget ce trimestre et pourquoi ?",
        "Quels clients haute valeur sont à risque de churn ?",
        "Où doit-on investir le budget en priorité : routes, rétention ou upsell ?",
    ]

    for q in questions:
        poser_question(q)