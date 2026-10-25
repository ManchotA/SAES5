# Contrats entre le back, le front et le boîtier

Ce document fixe ce que chaque partie du projet peut attendre des autres. Le contenu peut s'enrichir : **ajouter un champ ne casse rien, en retirer ou en renommer un oblige à prévenir tout le monde.**

---

## 1. Contenu des salles

Un seul fichier : `content/salles.json`.

```json
{
  "salles": [
    {
      "id": "e1_aquarium",
      "etage": 1,
      "nom": "Aquarium",
      "mecanique": "couleurs",
      "parametres": {},
      "documents": [
        { "id": "rapport", "titre": "Rapport de maintenance", "texte": "..." }
      ]
    }
  ]
}
```

| Champ | Rôle |
|---|---|
| `id` | Identifiant unique de la salle. Sert de lien avec les scènes et les visuels côté front. |
| `etage` | Étage de la salle (1 à 3). La salle finale est seule à l'étage 4. |
| `nom` | Nom affiché. |
| `mecanique` | Type d'énigme (`couleurs` pour l'instant). |
| `parametres` | Réglages propres à la mécanique. Vide pour l'instant, chaque mécanique définira les siens. |
| `documents` | Textes que le joueur peut lire dans la salle. |

Les images et textures ne sont pas dans ce fichier : le front les associe lui-même à chaque `id`.

---

## 2. Routes REST

Le front appelle le back seulement si l'action **change l'état de la partie** ou **a besoin du boîtier**. Lire un document, monter une échelle ou afficher une image se fait dans le front seul.

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/api/sante` | Vérifie que le back tourne. |
| GET | `/api/salles` | Liste des salles, **partie publique seulement** : `id`, `etage`, `nom`, `documents`. Jamais `mecanique` ni `parametres`. |
| POST | `/api/partie` | Lance une nouvelle partie : remise à zéro, LEDs éteintes, timer démarré. |
| GET | `/api/partie` | État de la partie en cours. |
| POST | `/api/partie/salles/{id}/enigme` | Le joueur appuie sur E devant le panneau : le back lance l'énigme et allume les LEDs. |
| DELETE | `/api/partie/salles/{id}/enigme` | Le joueur quitte la salle sans avoir résolu l'énigme : le back l'annule et éteint les LEDs. |

Il n'y a qu'une partie à la fois (un seul PC, un seul joueur), d'où `partie` au singulier et sans identifiant.

Une route renvoie toujours la ressource entière en un seul appel. Le front charge `/api/salles` une fois au démarrage et garde le résultat en mémoire.

En cas d'erreur, le back renvoie un code HTTP adapté (`404` salle inconnue, `409` action impossible dans l'état actuel, par exemple une salle d'un étage encore fermé) avec un corps `{ "erreur": "..." }`.

### État de la partie

Renvoyé par `GET /api/partie`, `POST /api/partie` et dans chaque message WebSocket.

```json
{
  "statut": "en_cours",
  "fin_a": "2026-10-25T15:44:00",
  "etages_ouverts": [1],
  "salles_resolues": [],
  "enigme_en_cours": null
}
```

| Champ | Valeurs |
|---|---|
| `statut` | `aucune`, `en_cours`, `gagnee`, `perdue` |
| `fin_a` | Heure de fin de la partie |
| `etages_ouverts` | Étages accessibles |
| `salles_resolues` | `id` des salles résolues |
| `enigme_en_cours` | `id` de la salle dont l'énigme est active, ou `null` |

---

## 3. WebSocket

Adresse : `/ws`. Le back y envoie les événements qui ne viennent pas du front (boîtier, timer).

Chaque message a la même forme, avec l'état complet de la partie :

```json
{ "type": "enigme_resolue", "salle": "e1_aquarium", "partie": { ... } }
```

| Type | Quand |
|---|---|
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

---

## 5. Boîtier

- Le back parle au boîtier en termes d'**intentions** (« allumer la LED 3 en rouge », « le bouton 5 a été pressé »), jamais en messages bruts.
- Le simulateur est un programme fourni à part, pas encore reçu. Quand il arrivera, un seul adaptateur traduira ces intentions dans son format. Idéalement, le vrai boîtier utilisera le même.
- Une tâche en fond écoute le boîtier en continu. Si la lecture échoue, le lien est considéré comme coupé.

---

## 6. Règles internes du back

- Les tâches en fond (timer, écoute du boîtier) sont séparées, pour qu'une lecture en attente ne bloque jamais le timer.
- Toute action qui modifie la partie (validation, annulation, fin du timer) prend un **verrou** : les autres attendent leur tour.
- Celui qui obtient le verrou **revérifie l'état avant d'agir** : une validation qui arrive après la fin du timer est refusée, une annulation sur une énigme déjà résolue ne fait rien.
- Les opérations lentes (écriture vers le boîtier) ont leur propre délai maximum, pour que le verrou soit toujours libéré.

---

## À définir plus tard

- Les paramètres de chaque mécanique et la façon de générer les énigmes (dépend du GD).
- Le protocole exact du boîtier (dépend du simulateur).
