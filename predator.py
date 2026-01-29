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


E = 25
H = 20
R = 25
PORT_M = 50000

### Préparation de la récupération de la shared memory et des locks 
class MyManager(BaseManager):
    pass

MyManager.register('get_Data')
MyManager.register("get_lock_prey")
MyManager.register("get_lock_predator")
MyManager.register("get_lock_grass")


### Fonction qui lance un nouveau process predator
def main():

    p = mp.Process(target=predator, args=())
    p.start()


### Fonction principale
def predator():
    ### Connexion à la shared memory
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

    ### Tant que le prédateur a de l'énergie, il essaie de manger si son énergie est en dessous de H et se reproduit si son énergie est au-dessus de R.
    while energy[0] > 0 :
        sleep(2)
        if energy[0] < H :
            energy[0] += eat(data, pid, lock_prey, lock_predator, energy)
        if energy[0] > R :
            have_kid(energy)
        energy[0] -= 1
    sleep(1)

    ### le prédateur meurt quand il n'a plus d'énergie
    die(pid, data, lock_predator)

### Fonction qui annonce à l'environnement via une relation client/serveur l'existence du prédateur lors de sa création 
# Le message envoyé est sous le format "pid,type,event" avec le pid du process prédateur et type = "predator"
# event = "new" car le prédateur vient de naître.
def born(pid) :
    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        msg = str(pid) + ",predator,new"
        client_socket.send(msg.encode())


### Fonction qui crée un thread pour activer le prédateur lorsqu'il a faim, essaie de manger si lock_prey est libre.
# Si il n'est pas libre, le prédateur reste actif et revient vers sa fonction principale, s'il ne peut pas manger trop souvent, il meurt de faim.
# Si le lock est libre, il mange une proie et son énergie augmente de "food" puis son état revient à passif.
def eat(data, pid, lock_prey, lock_predator, energy) :
    thread_activate = threading.Thread(target=activate, args=(data, pid, lock_predator))
    thread_activate.start()
    food = 0
    if lock_prey.acquire() == True :
        food = data.eat_prey()
        if food > 0 :
            thread_deactivate = threading.Thread(target=deactivate, args=(data, pid, lock_predator))
            thread_deactivate.start()
        lock_prey.release()
    return food


### Fonctions qui changent l'état du prédateur et gèrent les locks.
def activate(data, pid, lock_predator):
    lock_predator.acquire()
    try :
        data.active_predator(str(pid))
    finally :
        lock_predator.release()

def deactivate(data, pid, lock_predator):
    lock_predator.acquire()
    try :
        data.passive_predator(str(pid))
    finally :
        lock_predator.release()


### Fonction qui cause la création d'un nouveau process predator et réduit l'énergie du prédateur actuel.
def have_kid(energy):
    main()
    energy[0] = 20


### Fonction qui gère la mort du prédateur : cause la suppression de sa présence dans la liste partagée, puis tue son propre process.
def die(pid,data,lock_predator):
    print(pid, "predator die")
    lock_predator.acquire()
    data.kill_predator(str(pid))
    lock_predator.release()
    sleep(2)
    os.kill(pid, signal.SIGTERM)
    quit()

### Lance la fonction main() quand le programme est exécuté.
if __name__ == "__main__":
    main()






