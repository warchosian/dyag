"""
Question templates for different categories
"""

# Question templates by category
# {app_name} will be replaced with the application name

TEMPLATES = {
    "status": [
        "Quel est le statut de {app_name} ?",
        "L'application {app_name} est-elle en production ?",
        "Dans quel état se trouve l'application {app_name} ?",
    ],
    "domains": [
        "Quels sont les domaines métier de {app_name} ?",
        "À quels domaines métier appartient {app_name} ?",
        "Dans quels domaines intervient l'application {app_name} ?",
        "Quel est le domaine d'intervention de {app_name} ?",
    ],
    "description": [
        "Quelle est la description de {app_name} ?",
        "À quoi sert l'application {app_name} ?",
        "Quel est l'objectif de {app_name} ?",
        "Que fait l'application {app_name} ?",
    ],
    "contacts": [
        "Qui est le contact principal pour {app_name} ?",
        "Comment contacter l'équipe de {app_name} ?",
        "Quels sont les contacts de l'application {app_name} ?",
    ],
    "events": [
        "Quand {app_name} a-t-elle été mise en production ?",
        "Quelle est la date de mise en production de {app_name} ?",
        "Quels sont les événements clés de {app_name} ?",
    ],
    "websites": [
        "Quel est le site web de {app_name} ?",
        "Où trouver {app_name} en ligne ?",
        "Quelle est l'URL de l'application {app_name} ?",
    ],
    "actors": [
        "Quels sont les acteurs impliqués dans {app_name} ?",
        "Qui sont les acteurs de {app_name} ?",
    ],
    "related_apps": [
        "Quelles applications sont liées à {app_name} ?",
        "Avec quelles autres applications {app_name} interagit-elle ?",
        "Quelles sont les applications associées à {app_name} ?",
    ],
    "related_data": [
        "Quelles données sont liées à {app_name} ?",
        "Quels sont les données associées à {app_name} ?",
    ],
    "metadata": [
        "Quelle est la date de dernière modification de {app_name} ?",
        "Quand {app_name} a-t-elle été modifiée pour la dernière fois ?",
    ],
    "full_info": [
        "Quel est le nom complet de {app_name} ?",
        "Quelle est la dénomination complète de l'application {app_name} ?",
    ],
    "app_id": [
        "Quel est l'identifiant de {app_name} ?",
        "Quel est l'ID de l'application {app_name} ?",
    ],
    "geographic_scope": [
        "Quelle est la portée géographique de {app_name} ?",
        "L'application {app_name} est-elle nationale ou locale ?",
    ],
}

# Transversal questions (multi-application)
TRANSVERSAL_TEMPLATES = [
    "Quelles applications sont en production ?",
    "Quelles applications sont en construction ?",
    "Combien d'applications concernent la biodiversité ?",
    "Quelles applications ont des domaines métier liés aux transports ?",
    "Quelles applications ont été modifiées en 2023 ?",
    "Quelles sont les applications nationales ?",
]

# Default system prompt for fine-tuning
DEFAULT_SYSTEM_PROMPT = """Tu es un assistant expert sur les applications du ministère de la transition écologique et solidaire.
Tu réponds de manière précise, factuelle et concise aux questions sur les applications,
leurs caractéristiques, leurs domaines d'intervention et leurs contacts.
Tes réponses sont basées uniquement sur les informations documentées."""

# Answer extraction functions (map field to extraction method)
ANSWER_EXTRACTORS = {
    "status": lambda app: app.status,
    "domains": lambda app: ", ".join(app.domains) if app.domains else None,
    "description": lambda app: app.description,
    "contacts": lambda app: ", ".join(app.contacts) if app.contacts else None,
    "events": lambda app: app.events[0]["date"] if app.events else None,
    "websites": lambda app: app.websites[0] if app.websites else None,
    "actors": lambda app: ", ".join(app.actors) if app.actors else None,
    "related_apps": lambda app: ", ".join([ra["name"] for ra in app.related_apps]) if app.related_apps else None,
    "related_data": lambda app: ", ".join(app.related_data) if app.related_data else None,
    "metadata": lambda app: app.metadata.get("modification") or app.metadata.get("Modification"),
    "full_info": lambda app: app.full_name,
    "app_id": lambda app: app.app_id,
    "geographic_scope": lambda app: app.geographic_scope,
}

# Difficulty mapping
DIFFICULTY_BY_CATEGORY = {
    "status": "easy",
    "app_id": "easy",
    "full_info": "easy",
    "geographic_scope": "easy",
    "domains": "easy",
    "websites": "easy",
    "contacts": "medium",
    "actors": "medium",
    "description": "medium",
    "events": "medium",
    "metadata": "medium",
    "related_apps": "hard",
    "related_data": "hard",
}
