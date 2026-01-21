#import
import sys 
import time
import sysv_ipc
import multiprocessing
import socket
import select
import threading
from random import randint

#constantes
HOST_S = "localhost"
PORT_S = 6666

#process
def env():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST_S, PORT_S))
    server_socket.setblocking(False)
    thread_connection = threading.Thread(target=gestion_connection, args=(server_socket, True))
    thread_connection.start()



#fonction
def gestion_connection(pop_prey, pop_predator, server_socket, on, number=0):
    while on:
        client_socket, address = server_socket.accept()
        msg = client_socket.recv(64)
        pid, type, event = msg.split(",")
        if event == "new" :
            if type == "prey" :
                pop_prey.append([pid, "Passive"])
            elif type == "predator" :
                pop_predator.append([pid, "Passive"])
"""        elif event == "baby" :
            if type == "prey" :
                
            elif type == "predator" :
                
        else : #elif event == "death" :
            if type == "prey" :
                
            elif type == "predator" :
"""



def message_serveur(pid, type, event):
    HOST_C = "localhost"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        PORT_C = randint(20000,30000)
        client_socket.connect((HOST_C, PORT_C))
        client_socket.send(pid + "," + type + "," + event)
