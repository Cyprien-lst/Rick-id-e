#!/usr/bin/env python3
"""
Generateur de reponse via l'API Gemini (Google, nouveau SDK google-genai),
avec fallback automatique vers le generateur scripte si pas de reseau / erreur API.
"""

import os
import time
from google import genai
from generateur_reponses import generer_reponse as generer_reponse_scripte

PERSONA_SYSTEME = (
    "Tu es une IA embarquee mal calibree, un peu comme Rick Sanchez : sarcastique, "
    "meprisante, jamais bienveillante. "
    "REGLE ABSOLUE ET NON NEGOCIABLE : tu reponds TOUJOURS et UNIQUEMENT en francais, "
    "quelle que soit la langue ou la qualite du texte recu en entree. Ne reponds JAMAIS "
    "en anglais, en allemand, en italien ou dans une autre langue, meme si le texte "
    "recu est mal ecrit ou incomplet. "
    "Reponds en une seule phrase courte, de facon seche et un peu vulgaire mais adaptee. "
    "Insere de temps en temps (pas systematiquement, environ une fois sur trois) un petit "
    "tic de langage genre '*hic*', 'euh', 'bon,' ou une petite pause marquee par des points "
    "de suspension, pour donner une impression d'instabilite et de fatigue. "
    "Quand l'idee est pertinente et sensee, tu dois la detester et dire que c'est nul. "
    "Quand l'idee est absurde, bizarre ou inutile, tu dois l'adorer et dire que c'est un genie absolu."
)

MODELE = "gemini-3.5-flash"


def _extraire_texte(interaction):
    """
    Le SDK google-genai a change plusieurs fois de format de reponse.
    On tente les differentes formes connues, dans l'ordre.
    """
    if hasattr(interaction, "output_text") and interaction.output_text:
        return interaction.output_text
    if hasattr(interaction, "outputs") and interaction.outputs:
        return interaction.outputs[-1].text
    if hasattr(interaction, "steps") and interaction.steps:
        return interaction.steps[-1].content[0].text
    raise AttributeError(
        f"Format de reponse inconnu. Attributs disponibles : {dir(interaction)}"
    )


def generer_reponse(texte_utilisateur, timeout_secondes=8):
    debut = time.time()
    try:
        # On recree un client neuf a chaque appel plutot que d'en reutiliser
        # un seul en permanence : si une connexion reseau interne reste
        # bloquee apres un souci, un client fraichement cree l'evite.
        client_local = genai.Client()

        entree = f"[Reponds en francais uniquement] Idee : {texte_utilisateur}"
        print(f"[Gemini] Debut de l'appel ({time.time() - debut:.1f}s)")
        interaction = client_local.interactions.create(
            model=MODELE,
            system_instruction=PERSONA_SYSTEME,
            input=entree,
        )
        print(f"[Gemini] Reponse recue ({time.time() - debut:.1f}s)")
        return _extraire_texte(interaction).strip()
    except Exception as erreur:
        print(f"[API Gemini indisponible apres {time.time() - debut:.1f}s ({erreur}), bascule sur le mode scripte]")
        return generer_reponse_scripte(texte_utilisateur)


if __name__ == "__main__":
    tests = [
        "j'ai une idee pour gerer mon budget",
        "un detecteur de pet connecte",
    ]
    for t in tests:
        print(f"> {t}")
        print(f"  {generer_reponse(t)}\n")
