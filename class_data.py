import random

class Data:
    def __init__(self):
        self.pop_prey = {}
        self.pop_predator = {}
        self.pop_grass = 10        
        
    def get_prey(self):
        return self.pop_prey
    
    def get_predator(self):
        return self.pop_predator
    
    def get_grass(self):
        return self.pop_grass

    def add_prey(self, pid):
        self.pop_prey[pid] = "Passive"
        print("add_prey : ", self.pop_prey)
        
    def add_predator(self, pid):
        self.pop_predator[pid] = "Passive"
        
    def kill_prey(self, pid):
        print("kill_prey", self.pop_prey)
        self.pop_prey.pop(pid)
        
    def kill_predator(self, pid):
        self.pop_predator.pop(pid)
        
    def add_grass(self):
        self.pop_grass += 1
    
    def eat_grass(self):
        food = 0
        if self.get_grass() > 0 :
            self.pop_grass -= 1
            food = random.randint(5, 20)
        return(food)

    def active_prey(self, pid):
        self.pop_prey[pid] = "Active"

    def passive_prey(self, pid):
        self.pop_prey[pid] = "Passive"
