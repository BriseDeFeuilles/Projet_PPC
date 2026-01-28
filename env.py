#!/usr/bin/env python3

#import
import sys 
import time
import sysv_ipc
import multiprocessing as mp
import socket
import select
import signal
import threading
import prey
from multiprocessing import Process, Value
from multiprocessing.managers import BaseManager
import random
from class_data import Data
from Fct_mq_display_grass import stop_display, secheresse, incGrass, msg_display

#constantes
HOST = "localhost"
PORT = 6666

PORT_M = 50000


key = 777
drought_event = threading.Event()




data = Data()
lock_prey = mp.Lock()
lock_predator = mp.Lock()
lock_grass = mp.Lock()

class MyManager(BaseManager):
    pass

MyManager.register('get_Data', callable=lambda: data, exposed=['add_prey', 'get_prey', 'get_predator', 'get_grass', 'kill_prey', 'kill_predator', 'add_grass', 'eat_grass', 'active_prey', 'passive_prey'])
MyManager.register("get_lock_prey", callable=lambda: lock_prey)
MyManager.register("get_lock_predator", callable=lambda: lock_predator)
MyManager.register("get_lock_grass", callable=lambda: lock_grass)

#fonction de création de storage manager
def shared_memory():

    manager = MyManager(address=("localhost", PORT_M), authkey=b"clef")
    print("manager started")

    manager.get_server().serve_forever()

def handler_signal(signum, frame) :
    drought_event.set()


#process principale
def env():
    manager = MyManager(address=("localhost", PORT_M), authkey=b"clef")
    print(MyManager._registry['get_Data'])
    while True:
        try:
            manager.connect()
            break
        except ConnectionRefusedError:
            time.sleep(0.1)
    print("connect manager", flush=True)

    ### Flag utiles pour le display et l'herbe
    flag_display = Value('b', True)
    flag_grass = Value('b', True)
    signal.signal(signal.SIGUSR1, handler_signal)

    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)

    data = manager.get_Data() 
    lock_prey = manager.get_lock_prey()
    lock_predator = manager.get_lock_predator()
    lock_grass = manager.get_lock_grass()
    

    print("serveur init", flush=True)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.setblocking(False)

    thread_display = threading.Thread(target=msg_display, args=(mq, pop_prey, pop_predator, grass, flag_display,))      #ajouter les locks ...
    thread_grass = threading.Thread(target=incGrass, args=(grass, flag_display, flag_grass,))
    thread_drought = threading.Thread(target=secheresse, args=(drought_event, flag_grass, flag_display,))
    thread_connection = threading.Thread(target=gestion_connection, args=(data, server_socket, True))

    thread_connection.start()
    thread_display.start()
    thread_grass.start()
    thread_drought.start()

    print("serveur start", flush=True)
    for i in range(15):
        time.sleep(1)
        print("env : ", data.get_prey(), i, flush=True)
    
    thread_connection.join()
    # Ces deux lignes sont à enlever, il faudra mettre une condition quelque part pour mettre ce flag à False
    sleep(10) 
    flag_display.value = False
    
    thread_grass.join()
    thread_drought.join()
    thread_display.join()

    stop_display(mq)



#fonction de client/serveur
def gestion_connection(data, server_socket, on, number=0):
    with server_socket:
        server_socket.listen(1)
        while on == True :
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable:
                client_socket, address = server_socket.accept()
                thread_client = threading.Thread(target=gestion_clients, args=(data, client_socket, address))
                thread_client.start()
                thread_client.join()
                print("connection : ", data.get_prey(), flush = True)
                


def gestion_clients(data, client_socket, address):
    msg = client_socket.recv(64).decode()
    print(msg)
    pid, type, event = msg.split(",")
    if event == "new" :
        if type == "prey" :
            print(pid)
            data.add_prey(pid)
            print("gestion", data.get_prey())
        elif type == "predator" :
            data.add_predator(pid)
        

#fonction principale
if __name__ == "__main__":
    print("starting")
    
    p_memory = mp.Process(target=shared_memory)
    p_memory.start()
    
    print("starting manager process")
    
    time.sleep(5)

    print("starting env process")
    p_env = mp.Process(target=env)
    p_env.start()
    #fin = input()
    time.sleep(5)
    prey.main()
"""    prey.main()
    prey.main()
    time.sleep(1)
    prey.main()
    prey.main()"""

