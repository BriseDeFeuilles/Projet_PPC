from time import sleep
import os

### Fonctions annexes :

### Fonction d'arrêts de l'affichage
def stop_display(mq) :
    m_stop = "0,0,0"
    stop = m_stop.encode()
    mq.send(stop, type=3)


    
### Fonction de gestion de la sécheresse lancée en thread.
# Lorsque le bouton de l'affichage est pressé, la fonction reçoit un signal et change flag_grass à False pendant 5 secondes.
def secheresse(event, flag_grass, flag_display) :
    while flag_display.value :
        event.wait()
        event.clear()
        print("sécheresse")
        flag_grass.value = False
        sleep(5)
        flag_grass.value = True
        print("fin sécheresse")



### Fonction lancée en thread qui gère la croissance de l'herbe, augmente la quantité d'herbe de 1 toutes les 2 secondes
# sauf s'il y a une sécheresse annoncée par le flag_grass.
def incGrass(data, lock_grass, flag_display, flag_grass) :
    while flag_display.value :
        if flag_grass.value :
            lock_grass.acquire()
            data.add_grass()
            lock_grass.release()
        sleep(2)


### Fonction lancée en thread qui envoie périodiquement un message "herbe,prey,predator" au display pour l'affichage via une message queue.
def msg_display(mq, data, lock_prey, lock_predator, lock_grass, flag_display, ) :
    """
    Envoie périodiquement un message "herbe,prey,predator"
    """
    msg_pid = str(os.getpid()).encode()
    mq.send(msg_pid, type = 3)
    while flag_display.value :
        lock_predator.acquire()
        lock_prey.acquire()
        lock_grass.acquire()
        msg = str(data.get_grass()) + "," + str(len(data.get_prey())) + "," + str(len(data.get_predator()))
        lock_grass.release()
        lock_prey.release()
        lock_predator.release()
        msg_send = msg.encode()
        mq.send(msg_send, type = 3)
        sleep(0.5)




