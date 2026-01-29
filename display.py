#!/usr/bin/env python3

from tkinter import *
import threading
import sysv_ipc
import sys
from multiprocessing import Process
from class_display import Display


### Constante de la MessageQueue :
key = 777

### Fonctions utilisées pour les threads :
def ecoute_mq(mq, fenetre) : 
    """
    Ecoute que la MessageQueue et modifie les valeurs de herb, prey et predator affichées
    """
    mess_str = 1
    while mess_str != "0,0,0" :
        mess, _ = mq.receive(type = 3)
        mess_str = mess.decode()
        herb, prey, predator = mess_str.split(',', 2)

        popH = herb
        popPrey = prey 
        popPtor = predator

        fenetre.modif_pop(popH, popPrey, popPtor)



### Process principal :
def display(key) :
    """
    Crée une fenêtre graphique pour afficher les populations.
    Ecoute sur la message queue, récupère les messages de env et affiche les populations 
    """
    fenetre = Display()
    mq = sysv_ipc.MessageQueue(key)
    pidEnv, _ = mq.receive(type = 3)
    fenetre.pid_env = int(pidEnv.decode())

    t_mq = threading.Thread(target=ecoute_mq, args=(mq, fenetre,))
    fenetre.title("Simulation")
    t_mq.start()
    fenetre.mainloop()
    t_mq.join()

def main() :
    d = Process(target=display, args=(key,))
    d.start()
    d.join()

if __name__ == "__main__" :
    main()
    
