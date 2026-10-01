# 🧩 GDD-TEMPLATE : [Nom du Projet]
**Document de Conception de Jeu (Game Design Document)**

| Information | Détails |
| :--- | :--- |
| **301-302 / Snow** | [Romann Greco, Saul Boucherot, Nicolas Chanez, Abel Chauwin, Mo'ad Bendjeddou] |
| **1.0**| Draft initial |
| **01-10-2026** |

---

## 1. VISION & CONCEPT (Le "Pitch")
*Cette section doit permettre à n'importe qui de comprendre votre projet en 30 secondes.*

*   **High Concept (Le Pitch) :** Résumez votre jeu en une phrase percutante.

On doit s'échapper d'un complexe tout en sauvant la biodiversité qui a envahi les lieux.

*   **Genre :** (ex: Puzzle-game, Enquête narrative, Simulation de gestion...)

Le jeu mélange des mécaniques de puzzle/énigmes et d'aventure. L'objectif est de sortir en observant la biodiversité guérir à mesure que les énigmes sont complétées.

*   **Public Cible :** Qui sont vos joueurs ? (Âge, profil, niveau d'aisance technologique).

Notre public cible serait des joueurs habitués à des mécaniques d'escape game et de jeux vidéo. Il ne demande pas un haut niveau d'aisance technologique mais au moins un minimum afin de résoudre les énigmes les plus compliquées. Il faut aussi qu'ils soient intéressés par l'écologie car le jeu a également pour but d'informer.

*   **La Proposition de Valeur :** Pourquoi ce jeu est-il unique ? Quelle est l'expérience émotionnelle recherchée ?

Le jeu est unique puisque dans ce jeu, on aura un système de niveau original ainsi que des mécaniques de puzzle uniques en utilisant un microcontrôleur pas encore sorti. On vise à rendre l'expérience amusante et mélancolique afin de sensibiliser à l'importance de la biodiversité et de l'écologie.

—

## 2. LE GAMEPLAY (Les Règles du Jeu)
*Décrivez ici comment le jeu fonctionne concrètement.*

On sera dans un complexe constitué de 3 étages avec 3 salles par étage, plus la salle finale. À chaque étage l'accès au suivant est bloqué, et au dernier étage on peut s'échapper via le toit.
Pour chaque étage on peut avoir un environnement thématique différent, par exemple un complexe aquatique où on est à l'extérieur d'un réseau d'aquarium. Ces environnements sont impactés différemment en fonction de comment la pollution les atteint. Donc par exemple dans le complexe d'aquarium il y aurait un problème d'acidité qui endommagerait la faune et la flore aquatique.

Notre but est donc de régler les problèmes spécifiques à chaque étage de manière ludique. Notamment avec un microcontrôleur. Pour chaque étage, la mécanique et la manière d'utiliser notre outil diffèrent pour rendre chaque étage unique.

### 2.1 La Boucle de Gameplay (Core Loop)
Décrivez le cycle d'action répétitif du joueur.
*(Exemple : Explorer $\rightarrow$ Collecter un indice $\rightarrow$ Résoudre une énigme $\rightarrow$ Débloquer une zone)*.

Choisir une salle à l'étage -> Explorer la salle -> Comprendre l'énigme -> Résoudre l'énigme via le microcontrôleur -> Recommencer.
Quand les 3 salles d'un étage sont finies, le joueur peut passer au suivant, découvrir la nouvelle mécanique et recommencer.

### 2.2 Mécaniques de Jeu
Quelles sont les actions que le joueur peut effectuer ?
*   **Actions directes :** (ex: Saisir un code, déplacer un objet sur l'écran).
*   **Systèmes de jeu :** (ex: Gestion du temps, système de score, inventaire).

Le joueur utilise le microcontrôleur pour résoudre les énigmes. Il peut l'utiliser de différentes manières :
>En marquant des codes de couleurs
>En devant reproduire des patterns ou appuyer rapidement sur des boutons
>En l'utilisant comme manette ou source d'informations.
>Etc.
Durant toute l'expérience, le joueur aura une limite de temps de 45min pour arriver au bout du complexe.

### 2.3 Structure & Progression
*   **Le Flow :** Comment le joueur progresse-t-il ? (Linéaire, en arborescence, monde ouvert).

La progression est ouverte par étage, c'est-à-dire qu'on peut faire les salles de l'étage courant dans l'ordre que l'on veut. La progression entre les étages est linéaire. Le but final est d'atteindre la sortie sur le toit.

*   **Difficulté :** Comment la difficulté augmente-t-elle au fil du jeu ?

La difficulté n'augmente pas au fil du jeu (excepté à la dernière salle), mais les mécaniques sont changeantes et peuvent donc paraître plus complexes ou plus simples en fonction des joueurs.

*   **Conditions de Victoire & Défaite :** Comment le joueur gagne-t-il ? Quelles sont les conditions d'échec (Time-out, erreurs fatales) ?

Pour gagner, le joueur doit arriver sur le toit du bâtiment. Il n'y a pas de limite d'essai par salle pour y arriver mais une limite de temps liée à la condition du lieu.

---

## 3. SCÉNARIO & THÉMATIQUE (L'Univers)
*Cette section lie le jeu à sa dimension narrative et éthique.*

### 3.1 L'Intrigue & l'Univers
Décrivez le contexte, l'ambiance (SF, historique, etc.) et l'histoire qui porte le jeu.

On est un jeune homme qui fait de l'urbex. Il se retrouve bloqué dans ce complexe abandonné et sait que la seule sortie restante se trouve sur le toit. Il va donc devoir monter les différents étages en réglant les problèmes écologiques du complexe pour avancer dans son périple. Durant son voyage, il constatera grâce à des indices laissés à travers le complexe, ce qui a conduit à l'abandon de celui-ci.

### 3.2 Intégration des Enjeux (Éthique / Durable)
**Obligatoire :** Expliquez comment votre scénario ou vos mécaniques de jeu intègrent une problématique éthique, durable ou écologique. Comment ce sujet est-il devenu un élément central de l'expérience ?

Le complexe est complètement ravagé par la pollution et est une allégorie de notre monde. Les énigmes seront en partie orientées sur l'écologie, par exemple trouver un code couleur à l'aide des infos d'un rapport du GIEC. Finalement, il y aura des éléments de lore éparpillés sur la chute du complexe qui seront eux aussi liés à l'écologie.

---

## 4. SPÉCIFICATIONS TECHNIQUES (L'Ingénierie)
*Cette section est cruciale pour la validation de votre faisabilité technique.*

### 4.1 Stack Technologique
*   **Software :** Langages, Frameworks (Frontend/Backend), Base de données.
*   **Hardware / IoT :** Liste des composants physiques (Microcontrôleurs, capteurs, actionneurs) et mode de connexion.

Software :
Angular pour le front, Python pour le back, (MySQL si besoin de BDD)
Hardware :
Un microcontrôleur avec un build Python, la ksm1 de Keysmet.

### 4.2 Architecture du Système
Décrivez comment les composants communiquent entre eux (ex: Communication via API REST, protocole MQTT pour l'IoT, etc.).

FastAPI pour le back et MicroPython pour la communication avec le hardware.

### 4.3 Interface & Expérience Utilisateur (UI/UX)
*   **Interface :** Description des écrans principaux et de l'ergonomie.
*   **Interaction Physique :** Si applicable, comment le joueur interagit-il avec les objets physiques ?

Interface : c'est un point & click avec des décors vus du dessus / isométrique plutôt simples et on peut interagir avec les objets dans la pièce ou avec des portes pour changer de pièce.

Interface physique : le microcontrôleur a 10 boutons avec une LED par bouton, on peut interagir avec les boutons en fonction de l'énigme en cours.

---

## 5. PLAN DE PRODUCTION (La Roadmap)
*Transformez votre vision en tâches concrètes.*

### 5.1 Liste des Fonctionnalités (Feature List)
Divisez votre projet en fonctionnalités claires.
*   **Must-Have (Critique) :** Fonctionnalités indispensables pour le MVP.
*   **Should-Have (Important) :** Fonctionnalités qui enrichissent l'expérience.
*   **Nice-to-Have (Bonus) :** Fonctionnalités pour l'exposition JPO si le temps le permet.

Must-Have :
2 étages avec 1 ou 2 salles
un début d'énigme
le système de progression
l'interaction avec le microcontrôleur de façon fluide
Should-Have :
les 3 étages avec leurs 3 salles + la salle finale
les énigmes propres à chaque salle
l'histoire du jeu
aspect éducatif
Nice-to-Have :
des décors plus stylisés
mode français-anglais (accessibilité)
équivalent virtuel pour le microcontrôleur
la musique
les easter eggs

### 5.2 Jalons de Validation (Milestones)
Rappelez les dates clés du projet et ce qui doit être livré à chaque étape.

1er octobre : le GDD
Mi-novembre : prototype (MVP)
Mi-janvier : validation de l'UX et de la stabilité + rapport
Mi-février : produit fini + exposition

---

## 6. ANALYSE DES RISQUES
*Anticipez les problèmes pour ne pas être pris de court.*

| Risque identifié | Impact (H/M/L) | Stratégie d'atténuation |
| :--- | :--- | :--- |
| Instabilité du hardware | H | prévoir un mode "Software-only" de secours. |
| Manque d'inspiration pour les énigmes | L | mettre des étages avec seulement 2 salles |
| Se rendre compte qu'on part dans la mauvaise direction | L | essayer de partir de quelque chose de plus large |
| Avoir un délai microcontrôleur - backend | M | faire les opérations de timing directement sur le microcontrôleur |
| Faiblesse graphique du rendu final | L | S'appuyer sur des assets libres |
| Décalage entre le temps de résolution estimé et le temps réel en playtest | M | Playtester tôt avec un prototype même partiel et ajuster le nombre de salles en conséquence |
