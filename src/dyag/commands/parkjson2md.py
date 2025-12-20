"""
parkjson2md - Convertisseur JSON du parc applicatif vers Markdown optimisé RAG.

Convertit le parc applicatif JSON en Markdown optimisé pour l'indexation RAG.
Combine le meilleur des deux approches :
- Format structuré et lisible avec sections claires (de incorp)
- Couverture exhaustive de tous les champs (de json2md)
- URLs cliquables, texte multiligne, métadonnées (de incorp)
- Traitement générique et case-insensitive (de json2md)

Optimisé pour l'indexation RAG (Retrieval-Augmented Generation).

Exemple:
    dyag parkjson2md applicationsIA.json -o parc_rag.md --verbose
"""

import json
import sys
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime


def normalize_key(key: str) -> str:
    """Normalize a key to lowercase for comparison."""
    return str(key).lower().strip().replace('_', ' ').replace('-', ' ')


def parse_range_spec(spec: str, total: int) -> List[int]:
    """
    Parse range specification and return list of indices.

    Examples:
        "1-3" -> [0, 1, 2]
        "-5" -> last 5 elements
        "10-" -> from 10 to end
        "1,3,5-7" -> [0, 2, 4, 5, 6]

    Args:
        spec: Range specification string
        total: Total number of elements

    Returns:
        List of indices (0-based)
    """
    if not spec.strip():
        return list(range(total))

    indices = set()
    parts = spec.replace(" ", "").split(",")

    for part in parts:
        if not part:
            continue

        if "-" in part:
            if part.startswith("-"):
                # Last N elements: "-5" means last 5
                n = int(part[1:])
                start = max(0, total - n)
                indices.update(range(start, total))
            elif part.endswith("-"):
                # From N to end: "10-" means from 10 to end
                start = int(part[:-1]) - 1
                if 0 <= start < total:
                    indices.update(range(start, total))
            else:
                # Range: "5-10" means from 5 to 10
                a, b = part.split("-")
                a_i = max(0, int(a) - 1)
                b_i = min(total, int(b))
                indices.update(range(a_i, b_i))
        else:
            # Single index: "5" means element 5 (0-based: index 4)
            i = int(part) - 1
            if 0 <= i < total:
                indices.add(i)

    return sorted(indices)


def sanitize_tag(tag: str) -> str:
    """
    Sanitize a tag for use in filenames.

    Args:
        tag: Tag string to sanitize

    Returns:
        Sanitized tag
    """
    tag = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", tag.strip())
    return re.sub(r'_+', "_", tag)[:50]


def find_by_name(data_list: List[Dict], name_query: str) -> List[Dict]:
    """
    Filter applications by name (case-insensitive substring match).

    Args:
        data_list: List of application dictionaries
        name_query: Name to search for

    Returns:
        List of matching applications
    """
    results = []
    query = name_query.strip().lower()

    for item in data_list:
        # Try different name field variants
        name = get_field(item, "nom", "name", "title", "label")
        if name and query in str(name).lower():
            results.append(item)

    return results


def find_by_id(data_list: List[Dict], id_query: str) -> List[Dict]:
    """
    Filter applications by ID (case-insensitive substring match).

    Args:
        data_list: List of application dictionaries
        id_query: ID to search for

    Returns:
        List of matching applications
    """
    results = []
    target = id_query.strip().upper()

    for item in data_list:
        # Try to find ID field
        item_id = get_field(item, "id")
        if item_id and target in str(item_id).upper():
            results.append(item)

    return results


def get_field(data: Dict, *key_variants) -> Any:
    """
    Get a field from a dictionary, trying multiple key variants (case-insensitive).

    Args:
        data: Dictionary to search
        *key_variants: One or more key variants to try

    Returns:
        Value if found, None otherwise
    """
    if not isinstance(data, dict):
        return None

    # Create normalized lookup
    normalized = {normalize_key(k): v for k, v in data.items()}

    # Try each variant
    for variant in key_variants:
        norm_variant = normalize_key(variant)
        if norm_variant in normalized:
            return normalized[norm_variant]

    return None


def format_url(url: str) -> str:
    """Format a URL as a clickable Markdown link."""
    if not url:
        return ""
    url = str(url).strip()
    # Remove trailing slashes for cleaner display
    display_url = url.rstrip('/')
    return f"[{display_url}]({url})"


def format_multiline_text(text: str) -> str:
    """Format multiline text, preserving paragraphs and lists."""
    if not text:
        return ""

    # Clean up line endings
    text = str(text).replace('\r\n', '\n').replace('\r', '\n')

    # Split into lines and clean
    lines = [line.strip() for line in text.split('\n')]

    # Group into paragraphs (separated by empty lines)
    paragraphs = []
    current = []

    for line in lines:
        if line:
            current.append(line)
        elif current:
            paragraphs.append(' '.join(current))
            current = []

    if current:
        paragraphs.append(' '.join(current))

    return '\n\n'.join(paragraphs)


def format_list_items(items: List[Dict], field_mappings: Dict[str, str]) -> List[str]:
    """
    Format a list of dictionaries as Markdown list items.

    Args:
        items: List of dictionaries
        field_mappings: Dict mapping field keys to display format

    Returns:
        List of formatted Markdown lines
    """
    result = []

    for item in items:
        parts = []
        for key, label in field_mappings.items():
            value = get_field(item, key)
            if value:
                if label:
                    parts.append(f"{label}: {value}")
                else:
                    parts.append(str(value))

        if parts:
            result.append(f"- {' | '.join(parts)}")

    return result


def convert_app_to_markdown(app: Dict, verbose: bool = False) -> str:
    """
    Convert a single application to optimal Markdown format.

    Args:
        app: Application dictionary
        verbose: Print debug info

    Returns:
        Markdown formatted string
    """
    md_lines = []

    # === HEADER SECTION ===
    nom = get_field(app, "nom", "name", "title", "label") or "Application sans nom"
    md_lines.append(f"# {nom}")
    md_lines.append("")

    # Basic metadata on same level as title
    nom_long = get_field(app, "nom long", "nom complet", "full name")
    if nom_long:
        md_lines.append(f"**Nom complet:** {nom_long}")

    app_id = get_field(app, "id")
    if app_id:
        md_lines.append(f"**ID:** {app_id}")

    statut = get_field(app, "statut si", "statut", "status")
    if statut:
        md_lines.append(f"**Statut:** {statut}")

    portee = get_field(app, "portee geographique", "portée géographique", "scope")
    if portee:
        md_lines.append(f"**Portée géographique:** {portee}")

    md_lines.append("")

    # === DESCRIPTION SECTION ===
    descriptif = get_field(app, "descriptif", "description")
    if descriptif:
        md_lines.append("## Description")
        md_lines.append("")
        md_lines.append(format_multiline_text(descriptif))
        md_lines.append("")

    # === DOMAINES MÉTIERS SECTION ===
    domaines = get_field(app, "domaines et sous domaines", "domaines et sous-domaines", "domaines", "domains")
    if domaines and isinstance(domaines, list):
        md_lines.append("## Domaines métier")
        md_lines.append("")
        for domain in domaines:
            if isinstance(domain, dict):
                domaine = get_field(domain, "domaine métier", "domaine metier", "domaine")
                sous_domaine = get_field(domain, "sous domaine métier", "sous domaine metier", "sous-domaine", "sous domaine")

                if domaine:
                    line = f"- {domaine}"
                    if sous_domaine:
                        line += f" > {sous_domaine}"
                    md_lines.append(line)
            else:
                md_lines.append(f"- {domain}")
        md_lines.append("")

    # === FAMILLE D'APPLICATIONS ===
    famille = get_field(app, "famille d applications", "famille", "family")
    if famille:
        md_lines.append("## Famille d'applications")
        md_lines.append("")
        md_lines.append(famille)
        md_lines.append("")

    # === FONCTIONNALITÉS ===
    fonctions = get_field(app, "fonctions", "fonctionnalités", "functions")
    if fonctions and isinstance(fonctions, list):
        md_lines.append("## Fonctionnalités")
        md_lines.append("")
        for fonction in fonctions:
            md_lines.append(f"- {fonction}")
        md_lines.append("")

    # === SITES WEB SECTION (avec URLs cliquables) ===
    sites = get_field(app, "sites", "urls")
    if sites and isinstance(sites, list):
        md_lines.append("## Sites web")
        md_lines.append("")
        for site in sites:
            if isinstance(site, dict):
                nature = get_field(site, "nature de l url", "nature", "type")
                url = get_field(site, "url")
                commentaire = get_field(site, "commentaire", "comment")

                if url:
                    parts = []
                    if nature:
                        parts.append(f"**{nature}**")
                    parts.append(format_url(url))
                    if commentaire:
                        parts.append(f"*({commentaire})*")

                    md_lines.append(f"- {' : '.join(parts)}")
            else:
                md_lines.append(f"- {format_url(str(site))}")
        md_lines.append("")

    # === TECHNOLOGIES SECTION ===
    tech_principale = get_field(app, "technologie principale", "technologie")
    protocole_https = get_field(app, "protocole https")
    env_acces = get_field(app, "environnement d acces", "environnement d'accès")

    if tech_principale or protocole_https or env_acces:
        md_lines.append("## Technologies")
        md_lines.append("")
        if tech_principale:
            md_lines.append(f"- **Technologie principale:** {tech_principale}")
        if protocole_https:
            md_lines.append(f"- **Protocole HTTPS:** {protocole_https}")
        if env_acces:
            md_lines.append(f"- **Environnement d'accès:** {env_acces}")
        md_lines.append("")

    # === HÉBERGEMENTS SECTION ===
    hebergements = get_field(app, "hebergements", "hébergements", "hosting")
    if hebergements and isinstance(hebergements, list):
        md_lines.append("## Hébergements")
        md_lines.append("")
        for heberg in hebergements:
            if isinstance(heberg, dict):
                data_center = get_field(heberg, "data center", "datacenter")
                plateforme = get_field(heberg, "plateforme", "platform")
                type_site = get_field(heberg, "type de site", "type")
                commentaire = get_field(heberg, "commentaire", "comment")

                parts = []
                if data_center:
                    parts.append(f"**{data_center}**")
                if plateforme:
                    parts.append(f"Plateforme: {plateforme}")
                if type_site:
                    parts.append(f"Type: {type_site}")
                if commentaire:
                    parts.append(f"*({commentaire})*")

                if parts:
                    md_lines.append(f"- {' | '.join(parts)}")
            else:
                md_lines.append(f"- {heberg}")
        md_lines.append("")

    # === ÉVÉNEMENTS SECTION (enhanced with version and comments) ===
    evenements = get_field(app, "evenements", "événements", "events")
    if evenements and isinstance(evenements, list):
        md_lines.append("## Événements")
        md_lines.append("")
        for event in evenements:
            if isinstance(event, dict):
                date = get_field(event, "date")
                type_evt = get_field(event, "type d evenement", "type d'événement", "type", "event type")
                version = get_field(event, "version")
                commentaire = get_field(event, "commentaire", "comment")

                parts = []
                if date:
                    parts.append(f"**{date}**")
                if type_evt:
                    parts.append(type_evt)
                if version:
                    parts.append(f"(v{version})")
                if commentaire:
                    parts.append(f"*{commentaire}*")

                if parts:
                    md_lines.append(f"- {' : '.join(parts)}")
            else:
                md_lines.append(f"- {event}")
        md_lines.append("")

    # === ACTEURS SECTION ===
    acteurs = get_field(app, "acteurs", "actors")
    if acteurs and isinstance(acteurs, list):
        md_lines.append("## Acteurs")
        md_lines.append("")
        for acteur in acteurs:
            if isinstance(acteur, dict):
                role = get_field(acteur, "role d acteur", "rôle", "role")
                nom_acteur = get_field(acteur, "acteur", "nom", "name")

                if role or nom_acteur:
                    parts = []
                    if role:
                        parts.append(f"**{role}**")
                    if nom_acteur:
                        parts.append(nom_acteur)
                    md_lines.append(f"- {' : '.join(parts)}")
            else:
                md_lines.append(f"- {acteur}")
        md_lines.append("")

    # === CONTACTS SECTION ===
    contacts = get_field(app, "contacts")
    if contacts and isinstance(contacts, list):
        md_lines.append("## Contacts")
        md_lines.append("")
        for contact in contacts:
            if isinstance(contact, dict):
                role = get_field(contact, "role de contact", "rôle")
                nom_contact = get_field(contact, "contact", "nom")
                courriel = get_field(contact, "courriel", "email", "mail")

                parts = []
                if role:
                    parts.append(f"**{role}**")
                if nom_contact:
                    parts.append(nom_contact)
                if courriel and courriel != nom_contact:  # Avoid duplication
                    parts.append(f"<{courriel}>")

                if parts:
                    md_lines.append(f"- {' : '.join(parts)}")
            else:
                md_lines.append(f"- {contact}")
        md_lines.append("")

    # === THÉMATIQUES FRANCE NATION VERTE ===
    thematiques = get_field(app, "thematiques et sous thematiques france nation verte", "thématiques")
    if thematiques and isinstance(thematiques, list):
        md_lines.append("## Thématiques France Nation Verte")
        md_lines.append("")
        for theme in thematiques:
            if isinstance(theme, dict):
                thematique = get_field(theme, "thematique", "thématique")
                sous_thematique = get_field(theme, "sous thematique", "sous-thématique")

                if thematique:
                    line = f"- {thematique}"
                    if sous_thematique:
                        line += f" > {sous_thematique}"
                    md_lines.append(line)
            else:
                md_lines.append(f"- {theme}")
        md_lines.append("")

    # === ENJEUX ===
    enjeux = get_field(app, "enjeux", "stakes")
    if enjeux:
        md_lines.append("## Enjeux")
        md_lines.append("")
        md_lines.append(format_multiline_text(enjeux))
        md_lines.append("")

    # === UTILISATEURS SECTION ===
    utilisateurs = get_field(app, "utilisateurs", "users")
    if utilisateurs and isinstance(utilisateurs, list):
        md_lines.append("## Utilisateurs")
        md_lines.append("")
        for user in utilisateurs:
            if isinstance(user, dict):
                type_user = get_field(user, "utilisateur", "type")
                nombre = get_field(user, "nombre", "count")
                commentaire = get_field(user, "commentaire", "comment")

                parts = []
                if type_user:
                    parts.append(f"**{type_user}**")
                if nombre:
                    parts.append(f"({nombre})")
                if commentaire:
                    parts.append(f"*{commentaire}*")

                if parts:
                    md_lines.append(f"- {' '.join(parts)}")
            else:
                md_lines.append(f"- {user}")
        md_lines.append("")

    # Utilisateurs actifs par mois
    users_actifs = get_field(app, "utilisateurs actifs par mois")
    if users_actifs:
        md_lines.append(f"**Utilisateurs actifs par mois:** {users_actifs}")
        md_lines.append("")

    # === BÉNÉFICIAIRES ===
    beneficiaires = get_field(app, "beneficiaires", "bénéficiaires")
    if beneficiaires:
        md_lines.append("## Bénéficiaires")
        md_lines.append("")
        if isinstance(beneficiaires, list):
            for benef in beneficiaires:
                if isinstance(benef, dict):
                    type_benef = get_field(benef, "beneficiaire", "bénéficiaire", "type")
                    nombre = get_field(benef, "nombre", "count")
                    commentaire = get_field(benef, "commentaire", "comment")

                    parts = []
                    if type_benef:
                        parts.append(f"**{type_benef}**")
                    if nombre:
                        parts.append(f"({nombre})")
                    if commentaire:
                        parts.append(f"*{commentaire}*")

                    if parts:
                        md_lines.append(f"- {' '.join(parts)}")
                else:
                    md_lines.append(f"- {benef}")
        else:
            md_lines.append(format_multiline_text(beneficiaires))
        md_lines.append("")

    # === DONNÉES LIÉES (enhanced) ===
    donnees_liees = get_field(app, "donnees liees", "données liées")
    if donnees_liees and isinstance(donnees_liees, list):
        md_lines.append("## Données liées")
        md_lines.append("")
        for donnee in donnees_liees:
            if isinstance(donnee, dict):
                nom_donnee = get_field(donnee, "donnee liee", "donnée liée", "donnée")
                id_donnee = get_field(donnee, "id donnee liee", "id")
                type_flux = get_field(donnee, "type de flux", "flux")
                app2 = get_field(donnee, "application 2")

                parts = []
                if nom_donnee:
                    parts.append(f"**{nom_donnee}**")
                if id_donnee:
                    parts.append(f"(ID: {id_donnee})")
                if type_flux:
                    parts.append(f"- {type_flux}")
                if app2:
                    parts.append(f"via {app2}")

                if parts:
                    md_lines.append(f"- {' '.join(parts)}")
            else:
                md_lines.append(f"- {donnee}")
        md_lines.append("")

    # === APPLICATIONS LIÉES (enhanced) ===
    apps_liees = get_field(app, "applications liees", "applications liées")
    if apps_liees and isinstance(apps_liees, list):
        md_lines.append("## Applications liées")
        md_lines.append("")
        for app_liee in apps_liees:
            if isinstance(app_liee, dict):
                nom_app = get_field(app_liee, "application 2", "application", "nom")
                id_app = get_field(app_liee, "id application 2", "id")
                type_flux = get_field(app_liee, "type de flux", "flux")

                parts = []
                if nom_app:
                    parts.append(f"**{nom_app}**")
                if id_app:
                    parts.append(f"(ID: {id_app})")
                if type_flux:
                    parts.append(f"- {type_flux}")

                if parts:
                    md_lines.append(f"- {' '.join(parts)}")
            else:
                md_lines.append(f"- {app_liee}")
        md_lines.append("")

    # === TRAITEMENT DE DONNÉES (DICT) ===
    dict_main = get_field(app, "dict")
    dict_disp = get_field(app, "dict disponibilite", "dict - disponibilité")
    dict_int = get_field(app, "dict integrite", "dict - integrité", "dict - intégrité")
    dict_trac = get_field(app, "dict tracabilite", "dict - traçabilité", "dict - tracabilité")
    dict_conf = get_field(app, "dict confidentialite", "dict- confidentialité", "dict - confidentialité")

    if dict_main or dict_disp or dict_int or dict_trac or dict_conf:
        md_lines.append("## DICT (Disponibilité, Intégrité, Confidentialité, Traçabilité)")
        md_lines.append("")
        if dict_main:
            md_lines.append(f"- **Code DICT:** {dict_main}")
        if dict_disp:
            md_lines.append(f"- **Disponibilité:** {dict_disp}")
        if dict_int:
            md_lines.append(f"- **Intégrité:** {dict_int}")
        if dict_trac:
            md_lines.append(f"- **Traçabilité:** {dict_trac}")
        if dict_conf:
            # Handle list or single value
            if isinstance(dict_conf, list):
                md_lines.append(f"- **Confidentialité:** {', '.join(map(str, dict_conf))}")
            else:
                md_lines.append(f"- **Confidentialité:** {dict_conf}")
        md_lines.append("")

    # === DACP (Données à Caractère Personnel) ===
    trait_dacp = get_field(app, "traitement de donnees a caractere personnel", "traitement de données à caractère personnel")
    dacp_traitees = get_field(app, "dacp traitees", "dacp traitées")
    cat_dacp = get_field(app, "categories particulieres de dacp", "catégories particulières de dacp")
    mode_collecte = get_field(app, "mode de collecte des informations traitees", "mode de collecte des informations traitées")
    destinataires = get_field(app, "destinataires des donnees", "destinataires des données")

    if trait_dacp or dacp_traitees or cat_dacp or mode_collecte or destinataires:
        md_lines.append("## DACP (Données à Caractère Personnel)")
        md_lines.append("")
        if trait_dacp:
            md_lines.append(f"**Traitement DACP:** {trait_dacp}")
            md_lines.append("")
        if dacp_traitees:
            md_lines.append("**Données traitées:**")
            md_lines.append("")
            md_lines.append(format_multiline_text(dacp_traitees))
            md_lines.append("")
        if cat_dacp and isinstance(cat_dacp, list):
            md_lines.append("**Catégories particulières:**")
            md_lines.append("")
            for cat in cat_dacp:
                md_lines.append(f"- {cat}")
            md_lines.append("")
        if mode_collecte:
            md_lines.append(f"**Mode de collecte:** {mode_collecte}")
            md_lines.append("")
        if destinataires:
            md_lines.append("**Destinataires:**")
            md_lines.append("")
            if isinstance(destinataires, list):
                for dest in destinataires:
                    md_lines.append(f"- {dest}")
            else:
                md_lines.append(format_multiline_text(destinataires))
            md_lines.append("")

    # === BASE JURIDIQUE ET FINALITÉS ===
    base_juridique = get_field(app, "base juridique du traitement")
    finalites = get_field(app, "finalites du traitement", "finalités du traitement")
    cat_finalites = get_field(app, "categories particulieres de finalites", "catégories particulières de finalités")
    aipd = get_field(app, "necessite reglementaire d une aipd", "nécessité réglementaire d'une aipd")
    comm_conf = get_field(app, "commentaires sur la confidentialite", "commentaires sur la confidentialité")

    if base_juridique or finalites or cat_finalites or aipd or comm_conf:
        md_lines.append("## Base juridique et finalités")
        md_lines.append("")
        if base_juridique:
            md_lines.append(f"**Base juridique:** {base_juridique}")
            md_lines.append("")
        if finalites:
            md_lines.append("**Finalités du traitement:**")
            md_lines.append("")
            if isinstance(finalites, list):
                for finalite in finalites:
                    md_lines.append(format_multiline_text(finalite))
                    md_lines.append("")
            else:
                md_lines.append(format_multiline_text(finalites))
                md_lines.append("")
        if cat_finalites and isinstance(cat_finalites, list):
            md_lines.append("**Catégories particulières de finalités:**")
            md_lines.append("")
            for cat in cat_finalites:
                md_lines.append(f"- {cat}")
            md_lines.append("")
        if aipd:
            md_lines.append(f"**Nécessité AIPD:** {aipd}")
            md_lines.append("")
        if comm_conf:
            md_lines.append("**Commentaires sur la confidentialité:**")
            md_lines.append("")
            md_lines.append(format_multiline_text(comm_conf))
            md_lines.append("")

    # === SÉCURITÉ ET RISQUES ===
    gravites = get_field(app, "gravites d impacts", "gravités d'impacts")
    grav_desorg = get_field(app, "gravites d impacts desorganisation interne ou externe", "gravités d'impacts - désorganisation interne ou externe")
    grav_fin = get_field(app, "gravites d impacts financier", "gravités d'impacts - financier")
    grav_jur = get_field(app, "gravites d impacts juridique", "gravités d'impacts - juridique")
    grav_pers = get_field(app, "gravites d impacts personnes", "gravités d'impacts - personnes")
    grav_pol = get_field(app, "gravites d impacts politique image", "gravités d'impacts - politique image")
    si_enjeux = get_field(app, "si a enjeux", "si à enjeux")
    etude_secu = get_field(app, "etudes des besoins de securite et des risques", "études des besoins de sécurité et des risques")
    moa_ssi = get_field(app, "moa habilitee ssi", "moa habilitée ssi")
    contacts_ssi = get_field(app, "contacts ssi")

    if gravites or grav_desorg or grav_fin or grav_jur or grav_pers or grav_pol or si_enjeux or etude_secu or moa_ssi or contacts_ssi:
        md_lines.append("## Sécurité et risques")
        md_lines.append("")
        if gravites:
            md_lines.append(f"**Gravités d'impacts:** {gravites}")
        if grav_desorg:
            md_lines.append(f"- Désorganisation: {grav_desorg}")
        if grav_fin:
            md_lines.append(f"- Financier: {grav_fin}")
        if grav_jur:
            md_lines.append(f"- Juridique: {grav_jur}")
        if grav_pers:
            md_lines.append(f"- Personnes: {grav_pers}")
        if grav_pol:
            md_lines.append(f"- Politique/Image: {grav_pol}")
        if si_enjeux:
            md_lines.append(f"**SI à enjeux:** {si_enjeux}")
        if etude_secu:
            if isinstance(etude_secu, list):
                md_lines.append("**Études de sécurité:**")
                for etude in etude_secu:
                    if isinstance(etude, dict):
                        date = get_field(etude, "date")
                        type_etude = get_field(etude, "type d etude", "type d'étude", "type")
                        parts = []
                        if date:
                            parts.append(date)
                        if type_etude:
                            parts.append(type_etude)
                        if parts:
                            md_lines.append(f"- {' - '.join(parts)}")
                    else:
                        md_lines.append(f"- {etude}")
            else:
                md_lines.append(f"**Études de sécurité:** {etude_secu}")
        if moa_ssi:
            if isinstance(moa_ssi, list):
                md_lines.append("**MOA SSI:**")
                for moa in moa_ssi:
                    if isinstance(moa, dict):
                        acteur = get_field(moa, "acteur", "nom")
                        if acteur:
                            md_lines.append(f"- {acteur}")
                    else:
                        md_lines.append(f"- {moa}")
            else:
                md_lines.append(f"**MOA SSI:** {moa_ssi}")
        if contacts_ssi and isinstance(contacts_ssi, list):
            md_lines.append("**Contacts SSI:**")
            for contact in contacts_ssi:
                if isinstance(contact, dict):
                    nom = get_field(contact, "contact", "nom")
                    role = get_field(contact, "role de contact", "rôle")
                    if nom:
                        md_lines.append(f"- {nom}" + (f" ({role})" if role else ""))
                else:
                    md_lines.append(f"- {contact}")
        md_lines.append("")

    # === DÉVELOPPEMENT ET APPROCHE PRODUIT ===
    approche_produit = get_field(app, "approche produit")
    dev_agile = get_field(app, "developpement agile", "développement agile")
    prop_valeur = get_field(app, "proposition de valeur")
    obligation = get_field(app, "obligation")
    prec_obligation = get_field(app, "precisions sur l obligation", "précisions sur l'obligation")

    if approche_produit or dev_agile or prop_valeur or obligation or prec_obligation:
        md_lines.append("## Développement et approche")
        md_lines.append("")
        if approche_produit:
            md_lines.append(f"**Approche produit:** {approche_produit}")
        if dev_agile:
            md_lines.append(f"**Développement agile:** {dev_agile}")
        if prop_valeur:
            md_lines.append(f"**Proposition de valeur:** {prop_valeur}")
        if obligation:
            md_lines.append(f"**Obligation:** {obligation}")
        if prec_obligation:
            md_lines.append(f"**Précisions:** {prec_obligation}")
        md_lines.append("")

    # === CARTOGRAPHIES ===
    cartographies = []

    cart_urbanisme = get_field(app, "application figurant dans les cartographie d urbanisme", "cartographie urbanisme")
    if cart_urbanisme and normalize_key(str(cart_urbanisme)) == "oui":
        cartographies.append("Cartographie d'urbanisme")

    cart_transition = get_field(app, "participe a la cartographie numerique pour la transition ecologique", "cartographie transition écologique")
    if cart_transition and normalize_key(str(cart_transition)) == "oui":
        cartographies.append("Cartographie numérique pour la transition écologique")

    if cartographies:
        md_lines.append("## Cartographies")
        md_lines.append("")
        for cart in cartographies:
            md_lines.append(f"- {cart}")
        md_lines.append("")

    # === ÉVOLUTIONS PRÉVUES ===
    evolutions = []

    evo_tech = get_field(app, "evolution technologique", "évolution technologique")
    if evo_tech and normalize_key(str(evo_tech)) == "oui":
        evolutions.append("Évolution technologique")

    evo_contenu = get_field(app, "evolution du contenu", "évolution contenu")
    if evo_contenu and normalize_key(str(evo_contenu)) == "oui":
        evolutions.append("Évolution du contenu")

    evo_acces = get_field(app, "evolution des conditions d acces", "évolution accès")
    if evo_acces and normalize_key(str(evo_acces)) == "oui":
        evolutions.append("Évolution des conditions d'accès")

    evo_usage = get_field(app, "evolution de l usage", "évolution usage")
    if evo_usage and normalize_key(str(evo_usage)) == "oui":
        evolutions.append("Évolution de l'usage")

    if evolutions:
        md_lines.append("## Évolutions prévues")
        md_lines.append("")
        for evo in evolutions:
            md_lines.append(f"- {evo}")
        md_lines.append("")

    # === HASHTAGS ===
    hashtags = get_field(app, "hashtags", "tags")
    if hashtags:
        md_lines.append(f"**Tags:** {hashtags}")
        md_lines.append("")

    # === MÉTADONNÉES (à la fin) ===
    has_metadata = False
    date_creation = get_field(app, "date et heure de creation de la fiche", "date création")
    date_modif = get_field(app, "date et heure de modification de la fiche", "date modification")

    if date_creation or date_modif:
        md_lines.append("## Métadonnées")
        md_lines.append("")
        if date_creation:
            md_lines.append(f"- **Création:** {date_creation}")
        if date_modif:
            md_lines.append(f"- **Modification:** {date_modif}")
        md_lines.append("")

    # === AUTRES CHAMPS (exhaustivité) ===
    # Collect any remaining fields not already processed
    processed_keys = {
        "nom", "name", "title", "label",
        "nom long", "nom complet", "full name",
        "id",
        "statut si", "statut", "status",
        "portee geographique", "portée géographique", "scope",
        "descriptif", "description",
        "domaines et sous domaines", "domaines", "domains",
        "famille d applications", "famille", "family",
        "fonctions", "fonctionnalités", "functions",
        "sites", "urls",
        "evenements", "événements", "events",
        "acteurs", "actors",
        "contacts",
        "thematiques et sous thematiques france nation verte", "thématiques",
        "enjeux", "stakes",
        "donnees liees", "données liées",
        "applications liees", "applications liées",
        "application figurant dans les cartographie d urbanisme",
        "participe a la cartographie numerique pour la transition ecologique",
        "evolution technologique", "evolution du contenu",
        "evolution des conditions d acces", "evolution de l usage",
        "hashtags", "tags",
        "date et heure de creation de la fiche",
        "date et heure de modification de la fiche"
    }

    def format_complex_value(value, indent_level=1):
        """Format complex structures as Markdown sub-elements."""
        indent = "  " * indent_level
        lines = []

        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    # Dictionary in list
                    for k, v in item.items():
                        if isinstance(v, (list, dict)):
                            lines.append(f"{indent}- **{k}**:")
                            lines.extend(format_complex_value(v, indent_level + 1))
                        else:
                            lines.append(f"{indent}- **{k}**: {v}")
                elif isinstance(item, (list, dict)):
                    lines.extend(format_complex_value(item, indent_level))
                else:
                    lines.append(f"{indent}- {item}")
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, (list, dict)):
                    lines.append(f"{indent}- **{k}**:")
                    lines.extend(format_complex_value(v, indent_level + 1))
                else:
                    lines.append(f"{indent}- **{k}**: {v}")
        else:
            lines.append(f"{indent}- {value}")

        return lines

    other_fields = []
    for key, value in app.items():
        if normalize_key(key) not in [normalize_key(k) for k in processed_keys]:
            if value is not None and value != "" and value != False:
                # Format the value appropriately
                if isinstance(value, (list, dict)):
                    # Format complex structures as Markdown sub-elements
                    other_fields.append(f"- **{key}**:")
                    other_fields.extend(format_complex_value(value, indent_level=1))
                else:
                    val_str = str(value)[:100]
                    other_fields.append(f"- **{key}**: {val_str}")

    if other_fields:
        md_lines.append("## Autres informations")
        md_lines.append("")
        md_lines.extend(other_fields)
        md_lines.append("")

    return '\n'.join(md_lines)


def convert_parkjson2md(json_content: str, source_file: str = "", verbose: bool = False) -> str:
    """
    Convert JSON content to optimal Markdown format (parkjson2md).

    Args:
        json_content: JSON string
        source_file: Source file name for metadata
        verbose: Print progress info

    Returns:
        Markdown string
    """
    try:
        data = json.loads(json_content)

        if verbose:
            print(f"[INFO] JSON parsed successfully")

        # Find applications list
        apps = None
        if isinstance(data, dict):
            for key in data:
                key_lower = normalize_key(key)
                if 'application' in key_lower:
                    apps = data[key]
                    if verbose:
                        print(f"[INFO] Found applications under key: {key}")
                    break

            if apps is None:
                if verbose:
                    print(f"[INFO] No applications key found, treating as generic JSON")
                apps = [data]

        elif isinstance(data, list):
            apps = data
            if verbose:
                print(f"[INFO] JSON root is a list with {len(apps)} items")

        if not apps:
            print("[ERROR] No data found in JSON", file=sys.stderr)
            return ""

        if verbose:
            print(f"[INFO] Found {len(apps)} application(s)")
            print(f"[INFO] Converting to Markdown...")

        # Document header with metadata
        md_lines = [
            "# Applications du ministère de la transition écologique",
            "",
            f"*Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*"
        ]

        if source_file:
            md_lines.append(f"*Source: {source_file}*")

        md_lines.extend([
            "",
            f"**Nombre d'applications:** {len(apps)}",
            "",
            "---",
            ""
        ])

        # Convert each application
        for i, app in enumerate(apps):
            if verbose and (i + 1) % 100 == 0:
                print(f"[INFO] Processed {i + 1}/{len(apps)} applications...")

            md_lines.append(convert_app_to_markdown(app, verbose))
            md_lines.append("---")
            md_lines.append("")

        return '\n'.join(md_lines)

    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"[ERROR] Conversion failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return ""


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Sanitize a string to be used as a filename.

    Args:
        name: The string to sanitize
        max_length: Maximum length of the resulting filename

    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)
    # Replace multiple spaces/underscores with single underscore
    safe_name = re.sub(r'[_\s]+', '_', safe_name)
    # Remove leading/trailing underscores and spaces
    safe_name = safe_name.strip('_ ')
    # Limit length
    if len(safe_name) > max_length:
        safe_name = safe_name[:max_length]
    return safe_name


def process_parkjson2md(
    input_file: str,
    output_file: Optional[str] = None,
    verbose: bool = False,
    range_spec: Optional[str] = None,
    name_filter: Optional[str] = None,
    id_filter: Optional[str] = None,
    split_dir: Optional[str] = None
) -> int:
    """
    Process JSON file to optimal Markdown format (parkjson2md).

    Args:
        input_file: Path to input JSON file
        output_file: Path to output Markdown file (optional)
        verbose: Show detailed progress
        range_spec: Range specification (e.g., "1-3", "-5", "10-")
        name_filter: Filter by application name
        id_filter: Filter by application ID
        split_dir: Directory to generate separate files for each application

    Returns:
        Exit code (0 for success, 1 for error)
    """
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: '{input_file}' does not exist.", file=sys.stderr)
        return 1

    if not input_path.is_file():
        print(f"Error: '{input_file}' is not a file.", file=sys.stderr)
        return 1

    try:
        # Read JSON file
        with open(input_path, 'r', encoding='utf-8') as f:
            json_content = f.read()

        if verbose:
            print(f"[INFO] Read {len(json_content)} characters from {input_path}")

        # Parse JSON to get apps list
        try:
            data = json.loads(json_content)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON: {e}", file=sys.stderr)
            return 1

        # Find applications list
        apps = None
        if isinstance(data, dict):
            for key in data:
                key_lower = normalize_key(key)
                if 'application' in key_lower:
                    apps = data[key]
                    if verbose:
                        print(f"[INFO] Found applications under key: {key}")
                    break

            if apps is None:
                if verbose:
                    print(f"[INFO] No applications key found, treating as generic JSON")
                apps = [data]

        elif isinstance(data, list):
            apps = data
            if verbose:
                print(f"[INFO] JSON root is a list with {len(apps)} items")

        if not apps:
            print("[ERROR] No data found in JSON", file=sys.stderr)
            return 1

        original_count = len(apps)
        tag_parts = []
        used_filter = False

        # Apply filters
        if id_filter:
            apps = find_by_id(apps, id_filter)
            clean_id = sanitize_tag(id_filter.upper())
            tag_parts.append(f"ID{clean_id}")
            print(f"[FILTER] ID '{id_filter}' -> {len(apps)} resultat(s)")
            used_filter = True

        elif name_filter:
            apps = find_by_name(apps, name_filter)
            if apps and get_field(apps[0], "nom", "name"):
                tag_name = sanitize_tag(str(get_field(apps[0], "nom", "name")))
            else:
                tag_name = sanitize_tag(name_filter)
            tag_parts.append(tag_name)
            print(f"[FILTER] Nom '{name_filter}' -> {len(apps)} resultat(s)")
            used_filter = True

        elif range_spec:
            indices = parse_range_spec(range_spec, original_count)
            apps = [apps[i] for i in indices] if indices else []
            tag_parts.append(sanitize_tag(range_spec))
            print(f"[FILTER] Plage '{range_spec}' -> {len(apps)} element(s)")
            used_filter = True

        if not apps:
            print("[WARNING] No applications match the filters", file=sys.stderr)
            return 1

        # SPLIT MODE: Generate separate file for each application
        if split_dir:
            split_path = Path(split_dir)
            split_path.mkdir(parents=True, exist_ok=True)

            if verbose:
                print(f"[INFO] Converting {len(apps)} application(s) to separate Markdown files...")
                print(f"[INFO] Input:  {input_path}")
                print(f"[INFO] Output directory: {split_path}")

            files_created = 0
            for i, app in enumerate(apps):
                if verbose and (i + 1) % 100 == 0:
                    print(f"[INFO] Processed {i + 1}/{len(apps)} applications...")

                # Get application name
                app_name = get_field(app, "nom", "name", "title", "label") or f"app_{i+1}"
                safe_app_name = sanitize_filename(app_name)

                # Create filename: inputname_appname.md
                filename = f"{input_path.stem}_{safe_app_name}.md"
                file_path = split_path / filename

                # Generate markdown for this application
                app_md = convert_app_to_markdown(app, verbose)

                # Write file
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(app_md)

                files_created += 1

            print(f"[SUCCESS] {files_created} Markdown files created in {split_path}")
            return 0

        # NORMAL MODE: Single file output
        # Determine output path
        if output_file is None:
            if used_filter and tag_parts:
                tag_suffix = "_".join(tag_parts)
                output_path = input_path.with_name(f"{input_path.stem}_{tag_suffix}.md")
            else:
                # No filter: just change extension to .md
                output_path = input_path.with_suffix(".md")
        else:
            output_path = Path(output_file)

        if verbose:
            print(f"[INFO] Converting {len(apps)} application(s) to Markdown (parkjson2md format)...")
            print(f"[INFO] Input:  {input_path}")
            print(f"[INFO] Output: {output_path}")

        # Generate markdown header
        md_lines = [
            "# Applications du ministère de la transition écologique",
            "",
            f"*Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*",
            f"*Source: {input_path.name}*",
            ""
        ]

        if used_filter:
            md_lines.append(f"*Filtre appliqué: {', '.join(tag_parts)}*")
            md_lines.append("")

        md_lines.extend([
            f"**Nombre d'applications:** {len(apps)}",
            "",
            "---",
            ""
        ])

        # Convert each application
        for i, app in enumerate(apps):
            if verbose and (i + 1) % 100 == 0:
                print(f"[INFO] Processed {i + 1}/{len(apps)} applications...")

            md_lines.append(convert_app_to_markdown(app, verbose))
            md_lines.append("---")
            md_lines.append("")

        markdown_content = '\n'.join(md_lines)

        if not markdown_content:
            print("[WARNING] Conversion produced empty result", file=sys.stderr)
            return 1

        # Write Markdown file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        if verbose:
            print(f"[INFO] Wrote {len(markdown_content)} characters to {output_path}")

        print(f"[SUCCESS] Markdown file created: {output_path}")
        return 0

    except Exception as e:
        print(f"Error: Conversion failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def register_parkjson2md_command(subparsers):
    """Register the parkjson2md command."""
    parser = subparsers.add_parser(
        'parkjson2md',
        help='Convert JSON to optimal Markdown (hybrid format)',
        description='Convert JSON to optimized Markdown format combining structured readability with exhaustive coverage. Optimized for RAG indexing.'
    )

    parser.add_argument(
        'input_file',
        type=str,
        help='Input JSON file path'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output Markdown file path (default: input_FILTER.md with filter, or input.md without filter)'
    )

    parser.add_argument(
        '-r', '--range',
        type=str,
        metavar='RANGE',
        default=None,
        help='Select range of applications (e.g., "1-3", "-5" for last 5, "10-" from 10 to end)'
    )

    parser.add_argument(
        '-n', '--name',
        type=str,
        metavar='NAME',
        default=None,
        help='Filter applications by name (case-insensitive substring match)'
    )

    parser.add_argument(
        '-i', '--id',
        type=str,
        metavar='ID',
        default=None,
        help='Filter applications by ID (case-insensitive substring match)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    parser.add_argument(
        '--split-dir',
        type=str,
        metavar='DIR',
        default=None,
        help='Generate each application in a separate file in the specified directory (filename: inputname_appname.md)'
    )

    parser.set_defaults(func=lambda args: process_parkjson2md(
        args.input_file,
        args.output,
        args.verbose,
        args.range,
        args.name,
        args.id,
        args.split_dir
    ))
