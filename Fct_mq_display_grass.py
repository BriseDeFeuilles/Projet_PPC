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
        sleep(2)
        flag_grass.value = True
        print("fin sécheresse")



### Fonctions pour les threads :
def incGrass(grass, flag_display, flag_grass) :
    while flag_display.value :
        if flag_grass.value :
            # with lock_grass :
            sleep(0.5)
            grass.value += 10


def msg_display(mq, pop_prey, pop_predator, grass, flag_display) :
    """
    Envoie périodiquement un message "herbe,prey,predator"
    """
    msg_pid = str(os.getpid()).encode()
    mq.send(msg_pid, type = 3)
    while flag_display.value :
        # with lock_prey and lock_predator :
        msg = str(grass.value) + "," + str(len(pop_prey)) + "," + str(len(pop_predator))
        msg_send = msg.encode()
        mq.send(msg_send, type = 3)
        sleep(0.5)