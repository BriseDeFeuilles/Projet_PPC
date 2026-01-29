from time import sleep
import os

### Fonctions annexes :
def stop_display(mq) :
    m_stop = "0,0,0"
    stop = m_stop.encode()
    mq.send(stop, type=3)


    

def secheresse(event, flag_grass, flag_display) :
    while flag_display.value :
        event.wait()
        event.clear()
        print("sécheresse")
        flag_grass.value = False
        sleep(5)
        flag_grass.value = True
        print("fin sécheresse")



### Fonctions pour les threads :
def incGrass(data, lock_grass, flag_display, flag_grass) :
    while flag_display.value :
        if flag_grass.value :
            lock_grass.acquire()
            data.add_grass()
            lock_grass.release()
        sleep(2)


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

