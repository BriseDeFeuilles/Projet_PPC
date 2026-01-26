#!/usr/bin/env python3

from tkinter import *
from time import sleep
from multiprocessing import Process, Manager, Value
import threading
import sysv_ipc
import sys
import signal
import os

### Constantes :
key = 777
drought_event = threading.Event()

### Fonctions annexes :
def stop_display(mq) :
    m_stop = "0,0,0"
    stop = m_stop.encode()
    mq.send(stop, type=3)

def handler_signal(signum, frame) :
    drought_event.set()
    

def secheresse(event, flag_grass, flag_display) :
    while flag_display.value :
        event.wait()
        event.clear()
        print("sécheresse")
        flag_grass.value = False
        sleep(2)
        flag_grass.value = True
        print("fin sécheresse")



### Fonctions pour les threads :
def incGrass(grass, flag_display, flag_grass) :
    while flag_display.value :
        if flag_grass.value :
            sleep(0.5)
            grass.value += 1


def msg_display(mq, pop_prey, pop_predator, grass, flag) :
    """
    Envoie périodiquement un message "herbe,prey,predator"
    """
    msg_pid = str(os.getpid()).encode()
    mq.send(msg_pid, type = 3)
    while flag.value :
        # with lock_prey and lock_predator :
        msg = str(grass.value) + "," + str(len(pop_prey)) + "," + str(len(pop_predator))
        msg_send = msg.encode()
        mq.send(msg_send, type = 3)
        sleep(0.5)
        pop_prey.append(6)

### Process principal :
def env(key, pop_prey, pop_predator, grass) :
    ### Fonctions et variables associées au display : 
    # Ce flag sera modifié par une thread qui vérifie si les listes de populations ne sont pas vide, dans le cas contraire on arrête la simulation
    flag_display = Value('b', True)
    flag_grass = Value('b', True)
    signal.signal(signal.SIGUSR1, handler_signal)

    mq = sysv_ipc.MessageQueue(key, sysv_ipc.IPC_CREX)


    ### Threads display et herbe : 
    thread_display = threading.Thread(target=msg_display, args=(mq, pop_prey, pop_predator, grass, flag_display,))
    thread_grass = threading.Thread(target=incGrass, args=(grass, flag_display, flag_grass,))
    thread_drought = threading.Thread(target=secheresse, args=(drought_event, flag_grass, flag_display,))

    thread_display.start()
    thread_grass.start()
    thread_drought.start()


    sleep(10)

    flag_display.value = False
    thread_grass.join()
    thread_drought.join()
    thread_display.join()

    stop_display(mq)



if __name__ == "__main__" :
    with Manager() as manager:
        pop_predator = manager.list()
        pop_prey = manager.list()
        grass = manager.Value('i', 100)

        env = Process(target=env, args=(key, pop_prey, pop_predator, grass,))
        env.start()
        env.join()
    
