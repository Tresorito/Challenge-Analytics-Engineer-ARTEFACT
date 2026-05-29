import json
import httpx
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()
BASE   = "http://localhost:8000"

OUTILS = [
    {
        "name": "get_routes",
        "description": "Retourne les performances des routes Air CI.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_clients_a_risque",
        "description": "Retourne les clients à risque de churn.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_upsell",
        "description": "Retourne le potentiel upsell par segment.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "get_resume",
        "description": "Retourne le résumé exécutif et la recommandation budgétaire.",
        "input_schema": {"type": "object", "properties": {}}
    }
]


def appeler_outil(nom):
    resp = httpx.get(f"{BASE}/{nom}", timeout=10)
    return json.dumps(resp.json(), ensure_ascii=False, indent=2)


def poser_question(question, messages):
    messages.append({"role": "user", "content": question})

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
                    print(f"\n  → Consultation des données : {nom_outil}...")
                    resultat = appeler_outil(nom_outil)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": bloc.id,
                        "content": resultat
                    })
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            reponse_text = ""
            for bloc in response.content:
                if hasattr(bloc, "text"):
                    reponse_text = bloc.text
                    print(f"\nClaude : {bloc.text}\n")
            messages.append({
                "role": "assistant",
                "content": reponse_text
            })
            break

    return messages


def main():
    print("  Air Côte d'Ivoire — Assistant IA Analytique")
    print("  Powered by Claude + MCP")
    print("\nTape 'quit' pour quitter\n")

    messages = []

    while True:
        question = input("Vous : ").strip()

        if question.lower() in ["quit", "exit", "q"]:
            print("\nAu revoir !")
            break

        if not question:
            continue

        messages = poser_question(question, messages)


if __name__ == "__main__":
    main()