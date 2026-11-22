## Semaine du 5/10 au 11/10

Au cours de cette première semaine, nous avons fini de nous mettre d’accord sur quelques détails du gameplay. J’ai également repris contact avec mon ancien maître de stage afin de lui parler plus en détail de notre SAÉ et des dernières fonctionnalités qu’il avait implémentées sur la carte KSM1, que nous allons utiliser dans notre projet.

## Semaine du 12/10 au 18/10

Nous avons créé l’architecture initiale du projet et configuré nos environnements de développement. Nous avons également commencé à nous répartir les rôles plus clairement.
Je serai chargé de m’occuper du microcontrôleur. Je n’ai pas encore reçu le nouveau modèle, mais normalement, celui que je possède dispose de toutes les fonctionnalités nécessaires. Je dois simplement faire attention, car il possède une LED en moins, ce qui signifie que les numéros indiqués ne correspondent pas à ceux du nouveau modèle.

## Semaine du 19/10 au 25/10

J'ai reçu le microcontroleur keysmet et donc j'ai pu me mettre à jour sur les dernières fonctionalité. J'ai aussi commencé à regarder comment nous allions pouvoir interragir avec d'un point de vue technique, que ce soit dans la comminucation pc->microC ou microC->pc. 

## Semaine du 26/10 au 1/11

Je n'ai pas fait grand chose cette semaine, focus sur les révisions des dst et autre projet, juste communiquer avec les autres membres de l'équipe qui avait des questions.

## Semaine du 2/10 au 8/11

Semaine de dst donc l'équipe n'a pas ou peu travaillé sur le projet.

## Semaine du 9/11 au 15/11

Réalisation avec Nicolas d'un document rassemblant l'ensemble des énigmes, étage par étage, salle par salle avec à chaque fois les détails sur le thème de la salle, l'énigme, comment finir la salle et l'interaction avec le microcontrôleur. Avec ce document, l'ensemble de l'équipe à une vision d'ensemble sur chaque énigme et le travail pour les réaliser est grandement facilité. Cependant ces énigmes restent un premier jet et seront probablement modifiées à l'avenir.

## Semaine du 16/11 au 22/11

J'ai commencé à étudier comment faire en sorte que le microcontrôleur et l'ordinateur communique entre eux de façon stable, j'ai pour l'instant 3 pistes principales : 
- mettre la logique côté microcontrôleur + pc qui peux envoyer également un raccourci clavier sur une pression de touche, avec donc une logique pc qui récupère la touche pressé et qui fait l'affichage sur l'écran + le micro contrôleur qui exécute la même logique et qui calcule son résultat de son côté aussi.
- mettre la logique uniquement sur le microcontrôleur et il renvoie à la fin si l'énigme est un succès ou non.
- mettre la logique uniquement sur le pc et le pc envoie sur le microcontrôleur les leds à allumer.
Pour l'instant je ne sais pas encore 
