#!/usr/bin/env python3

#import
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

MyManager.register('get_Data', callable=lambda: data, exposed=['add_prey', 'add_predator', 'get_prey', 'get_predator', 'get_grass', 'kill_prey', 'kill_predator', 'add_grass', 'eat_grass', 'eat_prey', 'active_prey', 'passive_prey', 'active_predator', 'passive_predator', 'kill_all'])
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
    while True:
        try:
            manager.connect()
            break
        except ConnectionRefusedError:
            sleep(0.1)

    ### Flag utiles pour le display et l'herbe
    flag_display = Value('b', True)
    flag_grass = Value('b', True)
    if sys.platform != "win32":
        signal.signal(signal.SIGUSR1, handler_signal)
    else:
        print("SIGUSR1 non disponible")

    #mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)

    data = manager.get_Data() 
    lock_prey = manager.get_lock_prey()
    lock_predator = manager.get_lock_predator()
    lock_grass = manager.get_lock_grass()
    

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.setblocking(False)

    #thread_display = threading.Thread(target=msg_display, args=(mq, data, lock_prey, lock_predator, lock_grass, flag_display,))      #ajouter les locks ...
    thread_display_no_mq = threading.Thread(target=msg_display_no_mq, args=(data, lock_prey, lock_predator, lock_grass, flag_display,))
    thread_grass = threading.Thread(target=incGrass, args=(data, lock_grass, flag_display, flag_grass,))
    thread_drought = threading.Thread(target=secheresse, args=(drought_event, flag_grass, flag_display,))
    thread_connection = threading.Thread(target=gestion_connection, args=(data, server_socket, flag_display, lock_prey, lock_predator))

    thread_connection.start()
    #thread_display.start()
    thread_display_no_mq.start()
    thread_grass.start()
    thread_drought.start()

    
    sleep(10)

    ### makes sure that there are animals of both types, 
    ### prepare to finish the simulation otherwise via flag_display
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

    ### kill all animal process
    lock_predator.acquire()
    lock_prey.acquire()
    data.kill_all()
    lock_predator.release()
    lock_prey.release()

    ### wait for all thread to finish
    thread_connection.join()
    thread_grass.join()
    thread_drought.join()
    #thread_display.join()
    thread_display_no_mq.join()

    print("every thread stop")

    #stop_display(mq)



#fonction de client/serveur
def gestion_connection(data, server_socket, flag_display, lock_prey, lock_predator):
    with server_socket:
        server_socket.listen(1)
        while flag_display.value :
            readable, writable, error = select.select([server_socket], [], [], 1)
            if server_socket in readable:
                client_socket, address = server_socket.accept()
                thread_client = threading.Thread(target=gestion_clients, args=(data, client_socket, address, lock_prey, lock_predator))
                thread_client.start()
                thread_client.join()
                


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
        

#fonction principale
if __name__ == "__main__":
    print("starting")
    
    p_memory = mp.Process(target=shared_memory)
    p_memory.start()
    
    sleep(2)

    p_env = mp.Process(target=env)
    p_env.start()

    sleep(2)
    prey.main()
    prey.main()
    prey.main()
    prey.main()
    prey.main()
    predator.main()
    predator.main()


