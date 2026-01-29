import random
import os
import signal

class Data:
    def __init__(self):
        self.pop_prey = {}
        self.pop_predator = {}
        self.pop_grass = 0        

    ### Fonctions qui renvoient les variables partagées en shared memory
    # On ne peut pas accéder à ces variables directement depuis data, il faut passer par une fonction
    # Les locks respectifs sont activés hors des fonctions
    def get_prey(self):
        return self.pop_prey
    
    def get_predator(self):
        return self.pop_predator
    
    def get_grass(self):
        return self.pop_grass

    ### Fonctions qui ajoutent les nouveaux animaux à la liste correspondante avec leur pid sous forme de Str et l'état initial passif
    # Les locks respectifs sont activés hors des fonctions
    def add_prey(self, pid):
        self.pop_prey[pid] = "Passive"
        
    def add_predator(self, pid):
        self.pop_predator[pid] = "Passive"

    ### Fonctions qui suppriment les animaux de la liste correspondante à partir du pid
    # Les locks respectifs sont activés hors des fonctions
    def kill_prey(self, pid):
        self.pop_prey.pop(pid)
        
    def kill_predator(self, pid):
        self.pop_predator.pop(pid)

    ### Fonction qui ajoute 1 à la valeur de l'herbe
    # Le lock_grass est activé hors de la fonction
    def add_grass(self):
        self.pop_grass += 1

    ### Fonction qui, s'il y a de l'herbe, enlève 1 à la quantité d'herbe et renvoie une valeur de nourriture.
    # Le lock_grass est activé hors de la fonction
    def eat_grass(self):
        food = 0
        if self.get_grass() > 0 :
            self.pop_grass -= 1
            food = random.randint(1, 10)
        return(food)

    ### Fonction qui parcourt la liste de proies puis tue la première proie active et renvoie une valeur de nourriture.
    # Le lock_prey est activé hors de la fonction
    def eat_prey(self):
        food = 0
        for pid, statut in self.pop_prey.items() :
            if statut == "Active" :
                food = 10 + random.randint(1, 10)
                self.pop_prey.pop(str(pid))
                os.kill(int(pid), signal.SIGTERM)
                return(food)
        return(food)

    ### Fonction qui permettent de changer l'état des animaux
    # Les locks respectifs sont activés hors des fonctions
    def active_prey(self, pid):
        self.pop_prey[pid] = "Active"

    def passive_prey(self, pid):
        self.pop_prey[pid] = "Passive"

    def active_predator(self, pid):
        self.pop_predator[pid] = "Active"

    def passive_predator(self, pid):
        self.pop_predator[pid] = "Passive"

    ### Tue tous les process proie et prédateurs lors de la fin de simulation.
    # Les locks sont activés hors de la fonction
    def kill_all(self):
        for pid in self.pop_prey.keys():
            os.kill(int(pid), signal.SIGTERM)
        for pid in self.pop_predator.keys():
            os.kill(int(pid), signal.SIGTERM)


