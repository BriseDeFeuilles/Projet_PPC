#!/usr/bin/env python3

### Imports
import sys 
from time import sleep
#import sysv_ipc
import multiprocessing as mp
import socket
import select
import signal
import threading
import prey
import predator
from multiprocessing import Process, Value
from multiprocessing.managers import BaseManager
import random
from class_data import Data
from Fct_mq_display_grass import stop_display, secheresse, incGrass, msg_display, msg_display_no_mq

### Constantes de connections qui doivent être égale dans tous les programmes
HOST = "localhost"
PORT = 6666

PORT_M = 50000


key = 777
drought_event = threading.Event()



### Initialisation des variables de shared memory et des locks
data = Data()
lock_prey = mp.Lock()
lock_predator = mp.Lock()
lock_grass = mp.Lock()

### Initialisation du manager pour la shared memory
class MyManager(BaseManager):
    pass

MyManager.register('get_Data', callable=lambda: data, exposed=['add_prey', 'add_predator', 'get_prey', 'get_predator', 'get_grass', 'kill_prey', 'kill_predator', 'add_grass', 'eat_grass', 'eat_prey', 'active_prey', 'passive_prey', 'active_predator', 'passive_predator', 'kill_all'])
MyManager.register("get_lock_prey", callable=lambda: lock_prey)
MyManager.register("get_lock_predator", callable=lambda: lock_predator)
MyManager.register("get_lock_grass", callable=lambda: lock_grass)

### Fonction de création de storage manager à appeler en process
def shared_memory():

    manager = MyManager(address=("localhost", PORT_M), authkey=b"clef")
    print("manager started")

    manager.get_server().serve_forever()

def handler_signal(signum, frame) :
    drought_event.set()


### Process principale
def env():
    ### Connection au storage manager
    manager = MyManager(address=("localhost", PORT_M), authkey=b"clef")
    while True: # Cette boucle s'assure que la connection au lieu
        try:
            manager.connect()
            break
        except ConnectionRefusedError:
            sleep(0.1)

    ### Flag utiles pour le display et l'herbe
    flag_display = Value('b', True)
    flag_grass = Value('b', True)

    ### Création du signal pour la secheresse, SIGUSR1 ne fonctionne pas sur toutes les machines 
    if sys.platform != "win32":
        signal.signal(signal.SIGUSR1, handler_signal)
    else:
        print("SIGUSR1 non disponible")

    ### Création de la message queue vers le display
    #mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)

    ### Récupération dans le process des accès aux fonction et des locks de shared memory
    data = manager.get_Data() 
    lock_prey = manager.get_lock_prey()
    lock_predator = manager.get_lock_predator()
    lock_grass = manager.get_lock_grass()
    
    ### Initialisation du serveur pour la connection des process animaux
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.setblocking(False)

    ### Création des threads de gestion de différents éléments et evenement

    # Thread d'affichage
    #thread_display = threading.Thread(target=msg_display, args=(mq, data, lock_prey, lock_predator, lock_grass, flag_display,))      #ajouter les locks ...
    thread_display_no_mq = threading.Thread(target=msg_display_no_mq, args=(data, lock_prey, lock_predator, lock_grass, flag_display,))
    # Thread de gestion de la poussé de l'herbe
    thread_grass = threading.Thread(target=incGrass, args=(data, lock_grass, flag_display, flag_grass,))
    # Thread de gestion de secheresse avec son signal
    thread_drought = threading.Thread(target=secheresse, args=(drought_event, flag_grass, flag_display,))
    # Thread de gestion des arrivées de nouveaux animaux
    thread_connection = threading.Thread(target=gestion_connection, args=(data, server_socket, flag_display, lock_prey, lock_predator))

    thread_connection.start()
    #thread_display.start()
    thread_display_no_mq.start()
    thread_grass.start()
    thread_drought.start()

    
    sleep(10)

    ### Boucle qui s'assure de la présence d'animaux des deux types
    ### Permet de finir la simulation si non via flag_display
    while flag_display.value == True :
        sleep(3)
        lock_prey.acquire()
        if data.get_prey() == {} :
            flag_display.value = False
        lock_prey.release()
        lock_predator.acquire()
        if data.get_predator() == {} :
            flag_display.value = False
        lock_predator.release()
            
    print("flag = False")

    ### Tue tous les process animaux
    lock_predator.acquire()
    lock_prey.acquire()
    data.kill_all()
    lock_predator.release()
    lock_prey.release()

    ### Attend la fin de toutes les threads
    thread_connection.join()
    thread_grass.join()
    thread_drought.join()
    #thread_display.join()
    thread_display_no_mq.join()

    print("every thread stop")

    #stop_display(mq)



### Fonction de gestion client/serveur
def gestion_connection(data, server_socket, flag_display, lock_prey, lock_predator):
    """
    Fonciton qui accepte les connections de tous les nouveaux animaux et crée une thread qui gère la connection
    Paramètres :
        data: Permet l'accès à la shared memory et à ses fonctions
        server_socket: socket serveur à laquelle se connecte les nouveaux animaux
        flag_display: flag qui annonce la fin du programme
        lock_prey: lock d'accès pour lire et modifier pop_prey
        lock_predator: lock d'accès pour lire et modifier pop_predator
    """
    with server_socket:
        server_socket.listen(1)
        while flag_display.value :
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable:
                client_socket, address = server_socket.accept()
                thread_client = threading.Thread(target=gestion_clients, args=(data, client_socket, address, lock_prey, lock_predator))
                thread_client.start()
                thread_client.join()
                

# Fonciton de gestion de la connection qui reçoit un message du nouvel animal et l'ajoute à la liste
def gestion_clients(data, client_socket, address, lock_prey, lock_predator):
    msg = client_socket.recv(64).decode()
    print(msg)
    pid, type, event = msg.split(",")
    if event == "new" :
        if type == "prey" :
            lock_prey.acquire()
            data.add_prey(pid)
            lock_prey.release()
        elif type == "predator" :
            lock_predator.acquire()
            data.add_predator(pid)
            lock_predator.release()
        

### Fonction principale
if __name__ == "__main__":
    print("starting")
    
    # Création du process de storage manager
    p_memory = mp.Process(target=shared_memory)
    p_memory.start()
    
    sleep(2)

    # Création du process principal env
    p_env = mp.Process(target=env)
    p_env.start()

    sleep(2)

    # Création de proies et de prédateurs aussi ajoutable manuelement en lançant les programmes prey.py et predator.py
    prey.main()
    prey.main()
    prey.main()
    prey.main()
    prey.main()
    predator.main()
    predator.main()


