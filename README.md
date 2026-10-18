# SAES5
Projet de SAE du semestre 5. Escape Game.

# Membres

<details>
<summary>Abel Chauwin</summary>
J’ai pu, lors de mon stage, développer un site web en react native, ainsi que la base de données associée, 
j'ai donc gagné beaucoup d'expérience en gestion de base de données, ainsi qu'en front comme en back.
je pense que ma place dans cette équipe sera dans le design car c'est le domaine où l'équipe a le plus de lacunes, mais aussi dans le back et la bd à moindre échelle
</details>


<details>
<summary>Mo'ad Bendjeddou</summary>
  Durant mon stage j’ai été en charge de la gestion des incidents de sécurité, de la migration de systèmes informatiques ainsi que la réalisation d'enquêtes de sécurité.
</details>


<details>
<summary>Romann Greco</summary>
Développement d’applications chez MetM

Projet de data wiping par amorce USB
(Développement sur machine virtuelle, interface affichée dans un nouveau système de fichier créé / versioning d’image ISO)

Interventions urgentes impactant l’activité/chiffres de l’entreprise (Correction de code génération de bordereaux / Amazon FBA gestion de sous-traitance / Gestion de service après-vente par modification de base de données / Historique de preuves de livraison de produits par le tracking des commandes avec numéros présents dans BDD)

Projet Centralisateur de stock (Création de lien direct entre une application locale et produit de marketplace (mappings))

Ventes sur marketplace Temu fonctionnel.         Génération de revenus, activité concret.

Conduire un projet 

Encadre les projets durant une période faute d’absence de manageur/euse. Recueil de besoin du tuteur/chef d’entreprise.

Résumé : Développement d’applications, optimisation, gestion d’une base de données, conduire un projet.

Et je sais aussi faire de la musique. Je vais peut-être voir si je peux me former à faire du design pour le jeu.
</details>

<details>
<summary>Saul Boucherot</summary>
  Durant mon stage, j'ai principalement travaillé sur un microcontrôleur et sur une émulation de celui-ci en WebAssembly et TypeScript.
  Je possède également des compétences en organisation de travail et en clean de code.
  Je pense pouvoir être utile à l'équipe en tant que coordinateur des différentes tâches et sur l'implémentation du microcontrôleurs. Je peux également aider sur le back et le game design.
</details>

<details>
<summary>Nicolas Chanez</summary>
  Durant mon stage j’ai aidé à concevoir une application web sous Angular avec front et back.
  J’ai également des compétences en gestion de base de données et en interface utilisateurs.
  Dans cette équipe je pense pouvoir apporter mes connaissances en game design et en création d'énigmes. Je pense aussi pouvoir participer au back et à l'API.
</details>

# Equipe

Notre équipe possède une grande variété de compétences utiles à la SAE, et de plus, nous avons déjà travaillé ensemble une fois, ce qui rend plus simple la communication et la collaboration. Nous pensons donc que cette équipe est adaptée à la SAE.

# Technique

Escape game sur le thème de l'écologie : un front Angular + Phaser, un back FastAPI + SQLite, et un boîtier à boutons branché en USB.

## Structure

| Dossier      | Contenu                                                                    |
| ------------ | -------------------------------------------------------------------------- |
| `front/`     | Angular 22 (avec zone.js) + Phaser 4                                       |
| `back/`      | Python : FastAPI, SQLModel (SQLite), pyserial                              |
| `back/data/` | Base SQLite `escape.db`, créée automatiquement par le back, non versionnée |

## Prérequis

- **Node.js 24.15 ou plus** (exigé par Angular 22) : `node --version`
- **Python 3.12 ou plus** : `python --version`

## Installation

### Front

```bash
cd front
npm install
```

npm peut afficher un avertissement `allow-scripts` sur `esbuild`, `lmdb`, etc. : il est normal, rien à faire.

### Back

```bash
cd back
python -m venv .venv
```

Activer l'environnement :

- Windows : `.venv\Scripts\activate` (si PowerShell refuse d'exécuter le script, utiliser un terminal `cmd`)
- Linux / macOS : `source .venv/bin/activate`

Puis installer les dépendances :

```bash
pip install -r requirements-dev.txt
```

`requirements.txt` contient ce qu'il faut pour faire tourner le jeu ; `requirements-dev.txt` y ajoute les outils de développement (Ruff, pytest).

## Commandes

| Action                      | Commande         | Dossier  |
| --------------------------- | ---------------- | -------- |
| Lancer le front en dev      | `npm start`      | `front/` |
| Vérifier le code TypeScript | `npm run lint`   | `front/` |
| Formater le code TypeScript | `npm run format` | `front/` |
| Vérifier le code Python     | `ruff check .`   | `back/`  |
| Formater le code Python     | `ruff format .`  | `back/`  |
| Lancer les tests            | `pytest`         | `back/`  |

Le front de dev tourne sur http://localhost:4200. Les appels vers `/api` et `/ws` sont redirigés vers le back sur le port 8000 (voir `front/proxy.conf.json`).

Le back n'a pas encore de code : son lancement sera documenté ici quand il existera.
