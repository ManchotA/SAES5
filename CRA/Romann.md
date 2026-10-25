## Semaine du 5/10 au 11/10

Pour le projet, j'ai vivement encouragé de faire le jeu sous une vue simple 2d de profil au lieu de faire une vue isométrique. Je pars du principe qu'on part sur des bases simples afin d'avoir un livrable qualitatif.
On a surtout discuté du layout, donc comment on dispose les salles dans le jeu, dans quel ordre on doit faire les salles... 

On a essayé de voir pour l'identité artistique. 
De ce point de vue là on a opté pour un style simple, on ne sait pas exactement comment mais on va essayer d'avoir un style pixel art. 
Ce que je vais voir de mon côté, c'est le moyen le plus simple de le faire, j'ai pu voir qu'il y a des outils qui permettent de baisser la qualité d'une entité pour faire en sorte qu'elle soit pixelisé, je pense me pencher vers un raisonnement de ce style.
Après je vais me renseigner sur des outils précis.

Concernant le gameplay/disposition des salles, j'ai donc fait plusieurs schémas pour qu'on soit tous d'accord sur ce qu'on va faire.
Donc on a décidé au final d'avoir 3 salles principalles, et par le biais de ces salles on a accès à trois salles d'énigmes chacunes.
On commmence au premier étage avec un thème de forêt/nature, on est dans la salle principale de base avec trois portes pour trois salles d'énigmes, et une porte d'ascenseur accessible seulement après avoir résolu les 3 salles.
L'ascenseur débloqué mène au deuxième étage à thématique aquatique. On se retrouve dans la deuxième salle principale, et le jeu se fait ainsi de suite, les disposition sont plus ou moins similaires.

J'ai un schéma final du nom de layout2 présent dans le répertoires captureEcran qui montre visuellement l'idée.

Donc moi j'ai pour l'instant le rôle de faire la recherche de l'identité visuelle, quelles outils on va utiliser, je me charge de faire les musiques puisque j'ai de l'expérience sur ça.

En fonction de la progression du projets, j'aurais d'autres responsabilités qui vont s'ajouter naturellement.

## Semaine du 12 au 18 octobre : décisions concernant les éléments manquants

Pour le downscaling j'utilise Pixellt, ce que je vais faire c'est prendre une image de paysage pour les visuels du jeu, baisser la qualité de l'image jusqu'à quelle soit pixellisé avec l'outil que j'ai mentionné.
Après je vais l'ajuster à ma façon l'image downscalé sur libreSprite, c'est un logiciel où on fais du pixel art. Donc je vais faire des visuels simple parce que je suis neophyte dans ce domaine.

Après je peux avoir un png des ces visuels, et on peux les implémanter dans le code Angular avec la bibliothèque phaser qui est compatible pour ce cas de figure précis.
