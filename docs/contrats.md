# Contrats entre le back, le front et le boîtier

Ce document fixe ce que chaque partie du projet peut attendre des autres. Le contenu peut s'enrichir : **ajouter un champ ne casse rien, en retirer ou en renommer un oblige à prévenir tout le monde.**

---

## 1. Contenu des salles

Un seul fichier : `content/salles.json`.

```json
{
  "couleurs": {
    "rouge": [255, 0, 0],
    "vert": [0, 200, 0]
  },
  "salles": [
    {
      "id": "e1_racines",
      "etage": 1,
      "nom": "Salle des racines",
      "mecanique": "sequence",
      "parametres": {
        "boutons": { "1": "rouge", "2": "vert" },
        "etapes": [["vert", "rouge", "vert"]]
      },
      "documents": [
        { "id": "rapport", "titre": "Rapport de maintenance", "texte": "..." }
      ]
    }
  ]
}
```

| Champ | Rôle |
|---|---|
| `couleurs` | Palette de couleurs nommées, en `[rouge, vert, bleu]` de 0 à 255. Les mécaniques désignent les couleurs par leur nom. |
| `id` | Identifiant unique de la salle. Sert de lien avec les scènes et les visuels côté front. |
| `etage` | Étage de la salle (1 à 3). La salle tuto, facultative, est à l'étage 0. La salle finale est seule à l'étage 4. |
| `nom` | Nom affiché. |
| `mecanique` | Type d'énigme : `sequence` (séquence de couleurs), ou `factice` pour une salle provisoire (le bouton 1 la résout). |
| `parametres` | Réglages propres à la mécanique (voir ci-dessous). |
| `documents` | Textes que le joueur peut lire dans la salle. |

Les images et textures ne sont pas dans ce fichier : le front les associe lui-même à chaque `id`.

Le back vérifie tout le fichier au démarrage et refuse de démarrer en cas d'erreur, en indiquant la salle en cause.

### Paramètres de la mécanique `sequence`

Le joueur reproduit une ou plusieurs suites de couleurs sur le boîtier. Au lancement, chaque bouton utilisé s'allume dans sa couleur.

Seule une étape réussie se voit : les boutons clignotent en vert, et restent verts une fois l'énigme résolue. Un appui, juste ou faux, ne donne aucun retour, sinon on pourrait trouver la solution en essayant les touches une par une.

| Paramètre | Rôle |
|---|---|
| `boutons` | Bouton (`"1"` à `"10"`) → nom de couleur de la palette. |
| `etapes` | Une ou plusieurs suites de couleurs, à réussir dans l'ordre (ex. une étape par graine, puis le code final). |
| `erreur.recommencer` | Après une erreur : `"etape"` (l'étape en cours repart du début, par défaut) ou `"tout"`. |

---

## 2. Routes REST

Le front appelle le back seulement si l'action **change l'état de la partie** ou **a besoin du boîtier**. Lire un document, monter une échelle ou afficher une image se fait dans le front seul.

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/sante` | Vérifie que le back tourne : `{ "statut": "ok" }`. |
| GET | `/api/salles` | Liste (tableau JSON) des salles, **partie publique seulement** : `id`, `etage`, `nom`, `documents`. Jamais `mecanique` ni `parametres`. |
| POST | `/api/partie` | Lance une nouvelle partie : remise à zéro, LEDs éteintes, timer démarré. |
| GET | `/api/partie` | État de la partie en cours. |
| POST | `/api/partie/salles/{id}/enigme` | Le joueur appuie sur E devant le panneau : le back lance l'énigme et allume les LEDs. Si une autre énigme était en cours, elle est remplacée. |
| DELETE | `/api/partie/salles/{id}/enigme` | Le joueur quitte la salle sans avoir résolu l'énigme : le back l'annule et éteint les LEDs. |

Il n'y a qu'une partie à la fois (un seul PC, un seul joueur), d'où `partie` au singulier et sans identifiant.

Une route renvoie toujours la ressource entière en un seul appel : les routes de `partie` renvoient l'état de la partie. Le front charge `/api/salles` une fois au démarrage et garde le résultat en mémoire.

En cas d'erreur, le back renvoie un code HTTP adapté (`404` salle inconnue, `409` action impossible dans l'état actuel, par exemple une salle d'un étage encore fermé) avec un corps `{ "erreur": "..." }`.

### État de la partie

Renvoyé par les routes de `partie` et dans chaque message WebSocket.

```json
{
  "statut": "en_cours",
  "fin_a": "2026-10-25T15:44:00",
  "etages_ouverts": [0, 1],
  "salles_resolues": ["e0_tuto"],
  "enigme_en_cours": "e1_racines",
  "enigme_etat": {
    "etapes_reussies": 1,
    "nb_etapes": 4,
    "longueur_etape": 2
  }
}
```

| Champ | Valeurs |
|---|---|
| `statut` | `aucune`, `en_cours`, `gagnee`, `perdue` |
| `fin_a` | Heure de fin de la partie (heure locale du PC), ou `null` |
| `etages_ouverts` | Étages accessibles |
| `salles_resolues` | `id` des salles résolues |
| `enigme_en_cours` | `id` de la salle dont l'énigme est active, ou `null` |
| `enigme_etat` | Avancement de l'énigme en cours, propre à sa mécanique, ou `null`. Jamais la solution, ni rien qui permette de la deviner. Pour `sequence` : étapes réussies sur le total, et longueur de l'étape en cours. |

---

## 3. WebSocket

Adresse : `/ws`. Le back y envoie les événements qui ne viennent pas du front (boîtier, timer).

Chaque message a la même forme, avec l'état complet de la partie :

```json
{ "type": "enigme_resolue", "salle": "e1_racines", "partie": { ... } }
```

| Type | Quand |
|---|---|
| `enigme_progression` | L'avancement visible de l'énigme en cours a changé (pour `sequence` : une étape réussie). Le détail est dans `partie.enigme_etat`. |
| `enigme_resolue` | Le joueur a donné la bonne réponse sur le boîtier. Le front ouvre la porte. |
| `partie_terminee` | Victoire (salle finale résolue) ou défaite (temps écoulé). Le résultat est dans `partie.statut`. |
| `boitier_deconnecte` | Le lien avec le boîtier est perdu. |
| `boitier_reconnecte` | Le lien est rétabli. |

Comme chaque message porte l'état complet, le front n'a rien à déduire : par exemple, l'ouverture d'un nouvel étage se lit directement dans `partie.etages_ouverts`.

---

## 4. Timer

- Le back note l'heure de début et fixe l'heure de fin (`fin_a`).
- Le front fait le décompte lui-même pour l'affichage, en recalculant `fin_a − heure actuelle` à chaque image. Un lag ne crée donc aucun décalage, et un rafraîchissement de la page reprend au bon endroit.
- Le front affiche le temps sous la forme qu'il veut (chiffres, jauge…).
- **C'est le back qui décide de la fin** : une tâche en fond déclare la défaite à l'échéance et envoie `partie_terminee`.
- La durée (45 minutes) se règle avec la variable d'environnement `ESCAPE_DUREE_MINUTES`, pratique pour tester.

---

## 5. Boîtier

- Le back parle au boîtier en termes d'**intentions** (« allumer la LED 3 en rouge », « le bouton 5 a été pressé »), jamais en messages bruts.
- Pour l'instant, le boîtier est **simulé** : une page web du dossier `simulateur/`, servie par le back sur `/simulateur`. Le format d'échange du vrai boîtier sera branché plus tard sur les mêmes intentions.
- Le boîtier se connecte au WebSocket `/ws/boitier`. Sa connexion et sa déconnexion déclenchent `boitier_reconnecte` et `boitier_deconnecte` côté écrans.

Messages du back vers le boîtier :

| Message | Rôle |
|---|---|
| `{ "type": "leds", "couleurs": [[r, v, b], ...] }` | État complet des 10 LEDs, du bouton 1 au bouton 10. Envoyé à la connexion et à chaque changement. |
| `{ "type": "clignoter", "bouton": 3, "couleur": [r, v, b], "duree": 400 }` | La LED brille un instant (en millisecondes) dans cette couleur, puis revient à son état. |
| `{ "type": "erreur", "message": "..." }` | Une demande du boîtier a été refusée. |

Messages du boîtier vers le back :

| Message | Rôle |
|---|---|
| `{ "type": "appui", "bouton": 5 }` | Le bouton 5 a été pressé. |
| `{ "type": "test", "action": "resoudre" }` | Outil de test : résout l'énigme en cours sans la jouer. |
| `{ "type": "test", "action": "perdre" }` | Outil de test : termine la partie comme si le temps était écoulé. |

---

## 6. Règles internes du back

- Les tâches en fond (timer, écoute du boîtier) sont séparées, pour qu'une lecture en attente ne bloque jamais le timer.
- Toute action qui modifie la partie (validation, annulation, fin du timer) prend un **verrou** : les autres attendent leur tour.
- Celui qui obtient le verrou **revérifie l'état avant d'agir** : une validation qui arrive après la fin du timer est refusée, une annulation sur une énigme déjà résolue ne fait rien.
- Les opérations lentes (écriture vers le boîtier) ont leur propre délai maximum, pour que le verrou soit toujours libéré.

---

## À définir plus tard

- Les mécaniques des étages 2 et 3, et la façon de générer les énigmes (dépend du GD).
- Le format d'échange du vrai boîtier.
