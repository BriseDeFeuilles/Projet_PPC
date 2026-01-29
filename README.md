# Projet_PPC

Pour utiliser ce programme, il suffit d'exécuter env.py.

Il initialise la shared memory et tous les process et thread nécessaire au fonctionnement du code.

Une proie et un prédateur sont généré à l'initialisation.

Toutes les exécutions de prey.py et predator.py qui on lieu lorsque le process env est en route crée un process animal qui rejoint la simulation.

Lorsqu'il y a 0 proies ou 0 prédateurs, la majorité des process et thread prennent fin.

La fenêtre d'affichage est interactive et permet de créer de nouveaux process animaux et d'activer un épisode de sécheresse.

Il est possible de tester différentes simulations en modifiant les valeurs lié aux énergies de proie et des prédateurs dans les fichier prey.py et predator.py. E correspond à l'énergie initiale de l'animal, H à la limite d'énergie de faim et R à la limite d'énergie de reproduction.


Tous les fichier suivant doivent se trouver dans le même dossier :

- env.py
- display.py
- prey.py
- predator.py
- Fct_mq_display_grass.py
- class_data.py
- class_display.py

