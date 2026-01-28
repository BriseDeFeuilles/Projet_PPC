#!/usr/bin/env python3

#import
import sys 
import time
#import sysv_ipc
import multiprocessing as mp
import socket
import select
import threading
import os
import signal
from multiprocessing.managers import BaseManager



H = 10
R = 15
PORT_M = 50000

class MyManager(BaseManager):
    pass

MyManager.register('get_Data')
MyManager.register("get_lock_prey")
MyManager.register("get_lock_predator")
MyManager.register("get_lock_grass")


def main():

    p = mp.Process(target=prey, args=())
    p.start()



def prey():
    manager = MyManager(address=("localhost", PORT_M), authkey=b"clef")
    manager.connect()

    data = manager.get_Data()
    lock_prey = manager.get_lock_prey()
    lock_predator = manager.get_lock_predator()
    lock_grass = manager.get_lock_grass()

    pid = os.getpid()
    born(pid)
    energy = [10] 
    while energy[0] > 0 :
        time.sleep(2)
        if energy[0] < H :
            energy[0] += eat(data, pid, lock_prey, lock_grass, energy)
            print("want to eat")
        if energy[0] > R :
            have_kid()
            energy[0] -= 10
        energy[0] -= 1
    print(data.get_prey())
    time.sleep(1)
    die(pid, data)


def born(pid) :
    HOST = "localhost"
    PORT = 6666
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((HOST, PORT))
        msg = str(pid) + ",prey,new"
        print(msg)
        client_socket.send(msg.encode())


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


def have_kid():
    main()



def die(pid,data):
    # close things if necessary 
    # supress self from prey list
    # kill process with own pid 
    print("die")
    data.kill_prey(str(pid))
    time.sleep(2)
    os.kill(pid, signal.SIGTERM)
    quit()


if __name__ == "__main__":
    main()



"""
connect_to_serveur()
lock() #for energy
thread(timer(energy))
thread(live(energy, "prey"))

send_message_die()
"""