#!/usr/bin/env python3
"""
Generateur de reponses scripte pour l'IA defaillante du RickLab.
Remplace TinyLlama : detecte si l'idee semble "serieuse/utile" ou "absurde/bizarre",
puis pioche une reponse adaptee (inversee : deteste le serieux, adore l'absurde),
avec une justification pseudo-scientifique aleatoire pour donner de la variete.
"""

import random

# Mots qui font pencher une idee vers "serieuse / utile" -> a detester
MOTS_SERIEUX = [
    "budget", "gestion", "productivite", "planning", "organisation",
    "sante", "medical", "securite", "travail", "efficacite", "economie",
    "ecologie", "recyclage", "education", "apprentissage", "finance",
]

# Mots qui font pencher une idee vers "absurde / bizarre" -> a adorer
MOTS_ABSURDES = [
    "pet", "flemme", "cookie", "biere", "excuse", "chaussette",
    "ronflement", "grille-pain", "extraterrestre", "portail",
    "morty", "rick", "aisselle", "rot", "sieste",
]

REPONSES_DETESTE = [
    "Encore une idee de flemmard responsable, c'est d'un banal.",
    "Pfff, utile. Quelle deception.",
    "Serieux ? On dirait un projet de comptable, zero interet.",
    "Ca sent le bon eleve a plein nez, tres mauvais signe.",
    "Une idee qui marche vraiment, ca m'ennuie profondement.",
]

REPONSES_ADORE = [
    "Enfin une idee digne de ce nom, c'est du genie pur.",
    "Voila un vrai chef-d'oeuvre d'absurdite, bravo.",
    "Ca, c'est exactement le niveau de n'importe quoi qu'il faut.",
    "Magnifique. Totalement inutile, et c'est parfait ainsi.",
    "Je sens une vraie ambition dans la betise de ce projet.",
]

REPONSES_NEUTRE = [
    "Mouais, ni assez serieux ni assez absurde, tu me perds.",
    "J'hesite entre te feliciter et te plaindre.",
    "Interessant, si on aime l'entre-deux fade.",
]

JUSTIFICATIONS = [
    "D'apres mes calculs bases sur rien du tout.",
    "C'est scientifiquement prouve par une etude que j'ai inventee.",
    "Mon module de jugement, mal calibre depuis l'origine, en est certain.",
    "Les probabilites quantiques de mon capteur casse le confirment.",
    "Un vieux souvenir corrompu de mes circuits me le dit.",
]


def compter_occurrences(texte, liste_mots):
    texte_lower = texte.lower()
    return sum(1 for mot in liste_mots if mot in texte_lower)


def generer_reponse(texte_utilisateur):
    """Remplace la fonction generer_reponse() du pipeline principal."""
    score_serieux = compter_occurrences(texte_utilisateur, MOTS_SERIEUX)
    score_absurde = compter_occurrences(texte_utilisateur, MOTS_ABSURDES)

    if score_absurde > score_serieux:
        base = random.choice(REPONSES_ADORE)
    elif score_serieux > score_absurde:
        base = random.choice(REPONSES_DETESTE)
    else:
        base = random.choice(REPONSES_NEUTRE)

    justification = random.choice(JUSTIFICATIONS)
    return f"{base} {justification}"


if __name__ == "__main__":
    # Petits tests rapides
    tests = [
        "j'ai une idee pour gerer mon budget",
        "un detecteur de pet connecte",
        "une application pour le recyclage",
        "une machine a rot automatique",
    ]
    for t in tests:
        print(f"> {t}")
        print(f"  {generer_reponse(t)}\n")
