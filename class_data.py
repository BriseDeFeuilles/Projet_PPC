import random
import os
import signal

class Data:
    def __init__(self):
        self.pop_prey = {}
        self.pop_predator = {}
        self.pop_grass = 0        
        
    def get_prey(self):
        return self.pop_prey
    
    def get_predator(self):
        return self.pop_predator
    
    def get_grass(self):
        return self.pop_grass

    def add_prey(self, pid):
        self.pop_prey[pid] = "Passive"
        
    def add_predator(self, pid):
        self.pop_predator[pid] = "Passive"
        
    def kill_prey(self, pid):
        self.pop_prey.pop(pid)
        
    def kill_predator(self, pid):
        self.pop_predator.pop(pid)
        
    def add_grass(self):
        self.pop_grass += 1
    
    def eat_grass(self):
        food = 0
        if self.get_grass() > 0 :
            self.pop_grass -= 1
            food = random.randint(1, 10)
        return(food)
    
    def eat_prey(self):
        food = 0
        for pid, statut in self.pop_prey.items() :
            if statut == "Active" :
                food = 20
                self.pop_prey.pop(str(pid))
                os.kill(int(pid), signal.SIGTERM)
                return(food)
        return(food)

    def active_prey(self, pid):
        self.pop_prey[pid] = "Active"

    def passive_prey(self, pid):
        self.pop_prey[pid] = "Passive"

    def active_predator(self, pid):
        self.pop_predator[pid] = "Active"

    def passive_predator(self, pid):
        self.pop_predator[pid] = "Passive"

    def kill_all(self):
        for pid in self.pop_prey.keys():
            os.kill(int(pid), signal.SIGTERM)
        for pid in self.pop_predator.keys():
            os.kill(int(pid), signal.SIGTERM)
