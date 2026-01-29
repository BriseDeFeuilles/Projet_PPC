#!/usr/bin/env python3

#import
import sys 
from time import sleep
#import sysv_ipc
import multiprocessing as mp
import socket
import select
import threading
import os
import signal
from multiprocessing.managers import BaseManager


E = 8
H = 4
R = 10
PORT_M = 50000

### Préparation de la récupération de la shared memory et des locks 
class MyManager(BaseManager):
    pass

MyManager.register('get_Data')
MyManager.register("get_lock_prey")
MyManager.register("get_lock_predator")
MyManager.register("get_lock_grass")


### Fonction qui lance un nouveau process prey
def main():

    p = mp.Process(target=prey, args=())
    p.start()


### Fonction principale
def prey():
    ### Connection à la shared memory
    manager = MyManager(address=("localhost", PORT_M), authkey=b"clef")
    manager.connect()

    ### Récupération dans le process des accès aux fonctions et des locks de la shared memory
    data = manager.get_Data()
    lock_prey = manager.get_lock_prey()
    lock_predator = manager.get_lock_predator()
    lock_grass = manager.get_lock_grass()

    pid = os.getpid()
    born(pid)

    # energy est une liste dont le premier élément est un entier pour pouvoir être modifié par toutes les fonctions sans avoir de return.
    energy = [E] 

    ### Tant que la proie a de l'énergie, elle essaie de manger si son énergie est en dessous de H et se reproduit si son énergie est au-dessus de R.
    while energy[0] > 0 :
        sleep(2)
        if energy[0] < H :
            energy[0] += eat(data, pid, lock_prey, lock_grass, energy)
        if energy[0] > R :
            have_kid(energy)
        energy[0] -= 1
    sleep(1)

    ### la proie meurt quand elle n'a plus n'énergie
    die(pid, data, lock_prey)

### Fonction qui annonce à l'environnement via une relation client/serveur l'existence de la proie lors de sa création 
# Le message envoyé est sous le format "pid,type,event" avec le pid du process proie et type = "proie"
# event = "new" car la proie vient de naître.
def born(pid) :
    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        msg = str(pid) + ",prey,new"
        client_socket.send(msg.encode())

### Fonction qui crée un thread pour activer la proie lorsqu'elle a faim, essaie de manger si lock_grass est libre.
# S'il n'est pas libre, la proie reste active et revient vers sa fonction principale, si elle ne peut pas manger trop souvent, elle meurt de faim.
# Si le lock est libre, elle mange de l'herbe et son énergie augmente de "food" puis son état revient à passif.
def eat(data, pid, lock_prey, lock_grass, energy) :
    thread_activate = threading.Thread(target=activate, args=(data, pid, lock_prey))
    thread_activate.start()
    food = 0
    if lock_grass.acquire() == True :
        food = data.eat_grass()
        if food > 0 and energy[0] + food > H :
            thread_deactivate = threading.Thread(target=deactivate, args=(data, pid, lock_prey))
            thread_deactivate.start()
        lock_grass.release()
    
    return food


### Fonctions qui changent l'état de la proie et gèrent les locks.
def activate(data, pid, lock_prey):
    lock_prey.acquire()
    try :
        data.active_prey(str(pid))
    finally :
        lock_prey.release()

def deactivate(data, pid, lock_prey):
    lock_prey.acquire()
    try :
        data.passive_prey(str(pid))
    finally :
        lock_prey.release()


### Fonction qui cause la création d'un nouveau process prey et réduit l'énergie de la proie actuelle.
def have_kid(energy):
    main()
    energy[0] = 5


### Fonction qui gère la mort de la proie : cause la suppression de sa présence dans la liste partagée puis tue son propre process.
def die(pid,data, lock_prey):
    # close things if necessary 
    # supress self from prey list
    # kill process with own pid 
    print(pid, "prey die")
    lock_prey.acquire()
    data.kill_prey(str(pid))
    lock_prey.release()
    sleep(2)
    os.kill(pid, signal.SIGTERM)
    quit()

### Lance la fonction main() quand le programme est exécuté.
if __name__ == "__main__":
    main()



"""
connect_to_serveur()
lock() #for energy
thread(timer(energy))
thread(live(energy, "prey"))

send_message_die()
"""


