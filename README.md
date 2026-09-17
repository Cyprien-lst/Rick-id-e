# Boîte Rick-idée — RickLab (Workshop B2 EPSI)

## Présentation

**Boîte Rick-idée** est un objet connecté imaginé dans le cadre du **Workshop RickLab 2026-2027 (B2, EPSI)**.

Le principe : une IA locale/hybride, embarquée dans une boîte imprimée en 3D, qui **juge à voix haute les idées qu'on lui soumet** de façon peu pertinente, sèche et volontairement vulgaire, avec la personnalité de **Rick Sanchez**. L'idée est celle d'un objet que Rick aurait pu créer lui-même : un assistant façon "Jarvis", mais sarcastique et méprisant, qui continue de juger les idées même en son absence et qui permet de créer des objets que Rick auraient pu lui même créer.

L'utilisateur appuie sur un bouton, énonce son idée à voix haute, et la boîte lui répond (verdict + justification) via un haut-parleur.

## Équipe 

| Membre | Rôle principal |
|---|---|
| Cyprien Lesaint | Code (pipeline logiciel) |
| Théo Guffroy | Code (pipeline logiciel) |
| Axel Didier Boussou | Modélisation 3D + aide code |

L'électronique (câblage, GPIO, montage) a été réalisée à trois.

## Fonctionnement (pipeline)

```
Bouton (joystick, GPIO17) 
   → Enregistrement audio 
   → Vosk (Speech-to-Text, modèle FR) 
   → Gemini API (génération de la réponse, persona Rick Sanchez) 
        ↳ fallback automatique : générateur de réponses scripté si pas de réseau
   → Piper (Text-to-Speech, voix fr_FR-upmc-medium) 
   → Haut-parleur
```

Le pipeline tourne en continu au démarrage du Raspberry Pi via un **service systemd**.

### Détails techniques clés

- **Déclenchement** : bouton d'un module joystick (fil SW) branché sur GPIO17 (pin physique 11).
- **STT** : Vosk, modèle français, chargé **une seule fois** au démarrage (et non à chaque appel) pour la performance.
- **Génération de réponse** : API Gemini, avec un prompt système imposant la persona Rick Sanchez (sarcastique, méprisant), appelée avec un **timeout forcé** via `ThreadPoolExecutor` pour éviter les blocages réseau.
- **TTS** : Piper, voix `fr_FR-upmc-medium`.
- **Démarrage robuste** : une boucle `ExecStartPre` (ping) attend une connexion réseau réelle avant de lancer le script principal.

## Historique des choix techniques

Le projet a d'abord exploré une IA **100% locale** :
- **Ollama** envisagé initialement, abandonné car le Raspberry Pi ne le supportait pas matériellement.
- **llama.cpp + TinyLlama-1.1B-Chat (Q4_K_M)** testé ensuite : fonctionnel mais **ne respectait pas la persona demandée** (réponses sérieuses/techniques au lieu du ton sec et absurde voulu), même avec prompt système, exemples few-shot et température basse.
- Décision finale : conserver le concept d'IA embarquée mais utiliser l'**API Gemini** (le Pi ayant accès à internet), avec un **fallback scripté** en cas d'absence de réseau.

Le déclenchement de l'enregistrement a aussi évolué :
- Prévu initialement via un **clavier matriciel 4x4** en GPIO — abandonné (souci matériel sur une ligne, détection peu fiable, répétitions d'appui).
- Remplacé par un simple **bouton de module joystick** sur GPIO17, solution finalement retenue et fonctionnelle.

## Fabrication

- **Machine** : imprimante 3D Reality K2 Plus (myDiL).
- **Conception** : sous Tinkercad.
- **Boîtier** : ~14 cm x 12 cm, ouverture sur le dessous, opaque et lisse. Deux versions imprimées (la première trop petite, la seconde retenue). ~3h de conception.

## Matériel utilisé

- Raspberry Pi 4-B
- Microphone
- Haut-parleur
- Module joystick (bouton de déclenchement)
- Batterie
- Câblage GPIO
- Boîtier imprimé en 3D

## Organisation du workshop (4 jours)

- **J1** : brainstorming, électronique, premiers tests
- **J2** : code du pipeline, réalisation du modèle 3D
- **J3** : implémentation du bouton de déclenchement, suite du code
- **J4** : documentation, préparation de la présentation, correction de bugs IA

Aucun outil de suivi de projet (Trello/Notion) n'a été utilisé ; l'organisation s'est faite en direct entre les membres.

## Difficultés rencontrées

- Le clavier matriciel 4x4 s'est révélé peu fiable (mauvaises détections, répétitions), d'où le passage au bouton joystick.
- TinyLlama en local ne parvenait pas à tenir la persona demandée malgré plusieurs ajustements de prompt.
- Nécessité de forcer un timeout sur l'appel à l'API Gemini et de s'assurer d'une connexion réseau réelle avant le lancement du script au démarrage.

## Améliorations envisagées

- Une voix de Rick plus réaliste.
- Un boîtier plus soigné et esthétique.
- Une IA plus réactive, avec des réponses plus variées.
