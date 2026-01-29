#!/usr/bin/env python3

import tkinter as tk
import os
import signal
import prey 
import predator

class Display(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.grass = 0
        self.prey = 0
        self.ptor = 0
        self.pid_env = None
        self.creer_widgets()

    def creer_widgets(self):

        ### Définition des labels :
        self.labelH = tk.Label(self, text=f"Grass : {self.grass}")
        self.labelPrey = tk.Label(self, text=f"Prey : {self.prey}")
        self.labelPtor = tk.Label(self, text=f"Predator : {self.ptor}")
        self.labelH.pack()
        self.labelPrey.pack()
        self.labelPtor.pack()

        ### Définition des boutons pour contrôler la population :
        self.boutonPreyInc = tk.Button(self, text="Increase prey")
        self.boutonPreyInc.bind("<Button-1>", self.incPrey)

        self.boutonPtorInc = tk.Button(self, text="Increase predator")
        self.boutonPtorInc.bind("<Button-1>", self.incPtor)

        self.boutonPreyInc.pack()
        self.boutonPtorInc.pack()

        ### Définition du bouton sécheresse :
        self.boutonDrought = tk.Button(self, text = "Drought")
        self.boutonDrought.bind("<Button-1>", self.sendSignal)
        self.boutonDrought.pack()

        ### Bouton pour fermer la fenêtre :
        self.boutonQuit = tk.Button(self, text="Quit")
        self.boutonQuit.bind("<Button-1>", self.closeWindow)
        self.boutonQuit.pack()
    
    ### Fonctions associées aux boutons :
    def incPrey(self, event) :
        prey.main()
    
    def incPtor(self, event) :
        predator.main()
    
    def sendSignal(self, event) :
        os.kill(self.pid_env, signal.SIGUSR1)
    
    def closeWindow(self, event):
        os.kill(self.pid_env, signal.SIGUSR1)
        self.quit()
        self.destroy()

    
    ### Fonction pour modifier la fenêtre :
    def modif_pop(self, popH, popPrey, popPtor) :
        self.grass =  int(popH)
        self.prey = int(popPrey)
        self.ptor = int(popPtor)
        self.labelH.config(text = f"Grass : {popH}")
        self.labelPrey.config(text = f"Prey : {popPrey}")
        self.labelPtor.config(text = f"Predator : {popPtor}")
    
    
        


if __name__ == "__main__":
    app = Display()
    app.title("Ma Première App :-)")
    app.mainloop()
