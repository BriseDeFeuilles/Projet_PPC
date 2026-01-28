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

class MyManager(BaseManager):
    pass

MyManager.register('get_Data')
MyManager.register("get_lock_prey")
MyManager.register("get_lock_predator")
MyManager.register("get_lock_grass")


def main():

    p = mp.Process(target=predator, args=())
    p.start()



def predator():
    manager = MyManager(address=("localhost", PORT_M), authkey=b"clef")
    manager.connect()

    data = manager.get_Data()
    lock_prey = manager.get_lock_prey()
    lock_predator = manager.get_lock_predator()
    lock_grass = manager.get_lock_grass()

    pid = os.getpid()
    born(pid)
    energy = [E] 
    while energy[0] > 0 :
        sleep(2)
        if energy[0] < H :
            energy[0] += eat(data, pid, lock_prey, lock_predator, energy)
        if energy[0] > R :
            have_kid(energy)
        energy[0] -= 1
    sleep(1)
    die(pid, data, lock_predator)


def born(pid) :
    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        msg = str(pid) + ",predator,new"
        client_socket.send(msg.encode())


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


def have_kid(energy):
    main()
    energy[0] = 20



def die(pid,data,lock_predator):
    # close things if necessary 
    # supress self from prey list
    # kill process with own pid 
    print(pid, "predator die")
    lock_predator.acquire()
    data.kill_predator(str(pid))
    lock_predator.release()
    sleep(2)
    os.kill(pid, signal.SIGTERM)
    quit()


if __name__ == "__main__":
    main()

