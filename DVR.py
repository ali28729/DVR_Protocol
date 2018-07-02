import time
import sys
import os
import threading
from socket import *
import math

timeout_interval = 10.0
live_interval = 5.0

neighbours_paths = dict()
rout_path = dict()

lock = threading.Lock()


ID = sys.argv[1]
port = int(sys.argv[2])
filename_config = sys.argv[3]

class Path:
    def __init__(self, distance, nxt_destination):
        self.distance = distance
        self.nxt_destination = nxt_destination

    def equals(self, alternate_path):
        return self.distance == alternate_path.distance and self.nxt_destination == alternate_path.nxt_destination


class Neighbour:
    def __init__(self, cost_path, port, lifetime_interval):
        self.cost_path = cost_path
        self.port = port
        self.lifetime_interval = lifetime_interval
        self.paths = dict()
        self.checkAlive = False

def menu():
    option = 0
    while(1):
        print('\nThis is router ' + ID + '\n')

        option = int(input('1: Costs.\n2: Edit link cost\n3: Quit: '))
        if option == 1:
            for id, route in sorted(rout_path.items()):
                if id != ID:
                    print('Shortest Path to ' + id + ': ' + route.nxt_destination + ' and distance ' + str("%.1f" % route.distance))
        elif option == 2:
            string = 'Neighbours:'
            for id in sorted(neighbours_paths.keys()):
                string += ' ' + id
            print(string)
            toEdit = input('Enter the id of router: ')
            new_dist = float(input('write distance for ' + toEdit + ': '))
            neighbours_paths[toEdit].cost_path = new_dist

            ss = socket(AF_INET, SOCK_DGRAM)
            lock.acquire()
            ss.sendto(new_packet(toEdit, True), ('localhost', neighbours_paths[toEdit].port))
            lock.release()
            ss.close()

            threading.Thread(target=bellManFord).start()

        elif option == 3:
            os._exit(-1)

def send_distance_vector(sendcost_path):
    ss = socket(AF_INET, SOCK_DGRAM)
    lock.acquire()
    for id, neighbour in neighbours_paths.items():
        ss.sendto(new_packet(id, sendcost_path), ('localhost', neighbour.port))
    lock.release()
    ss.close()

def make_ready():
    while 1:
        time.sleep(live_interval)
        send_distance_vector(False)

def check_alive():
    while 1:
        time.sleep(1)
        for id, neighbour in neighbours_paths.items():
            if time.time() > neighbour.lifetime_interval:
                if neighbours_paths[id].cost_path != math.inf:
                    lock.acquire()
                    rout_path[id].distance = math.inf
                    neighbour.cost_path = math.inf
                    neighbour.checkAlive = True
                    for key2, item2 in rout_path.items():
                        if item2.nxt_destination == id:
                            item2.distance = math.inf

                    lock.release()
                    send_distance_vector(False)
                    threading.Thread(target=bellManFord).start()


def new_packet(dest_id, sendcost_path):
    dist_vect = str(ID)

    if sendcost_path:
        dist_vect += ' ' + str(neighbours_paths[dest_id].cost_path)
    dist_vect += '\n'

    for id, path in rout_path.items():
        dist_vect += str(id) + " " + str(path.distance) + '\n'

    return bytes(dist_vect, 'utf-8')



def r_obj(name):
    global neighbours_paths
    p = Path(math.inf, ID)
    rout_path[name] = p
    for id, neighbour in neighbours_paths.items():
        neighbour.paths[name] = p


def bellManFord():
    global rout_path
    lock.acquire()
    for id, route in rout_path.items():
        m_list = list()
        if id == ID:
            continue
        if id in neighbours_paths:
            m_list.append(Path(neighbours_paths[id].cost_path, ID))

        for id2, neighbour in neighbours_paths.items():
            p = Path(neighbours_paths[id2].cost_path + neighbour.paths[id].distance, id2)
            m_list.append(p)
        m_list.append(p)
        m = min(m_list, key = lambda x: x.distance)
        rout_path[id] = Path(m.distance,m.nxt_destination)

    lock.release()

def rec_input():
    rec_inputSocket = socket(AF_INET, SOCK_DGRAM)
    rec_inputSocket.bind(('localhost', port))
    while 1:
        message, S_addr = rec_inputSocket.recvfrom(2048)

        lines = str(message)[2:len(str(message))-1].split('\\n')
        fline = lines[0].split()
        neighbor_dest = fline[0]

        neighbours_paths[neighbor_dest].lifetime_interval = time.time() + timeout_interval

        if len(fline) > 1:
            neighbours_paths[neighbor_dest].cost_path = float(fline[1])

        lock.acquire()

        isUpdated = False

        for i in range(1, len(lines)):
            if lines[i] == '':
                continue
            t_ID = lines[i].split()
            p_id = Path(float(t_ID[1]),ID)
            if t_ID[0] not in neighbours_paths[neighbor_dest].paths:
                r_obj(t_ID[0])
            if not neighbours_paths[neighbor_dest].paths[t_ID[0]].equals(p_id):
                neighbours_paths[neighbor_dest].paths[t_ID[0]] = p_id
                isUpdated = True
        if isUpdated:
            threading.Thread(target=bellManFord).start()
        lock.release()

file = open(filename_config)
lines = file.readlines()
for i in range(1, len(lines)):
    t_ID = lines[i].split()
    neighbours_paths[t_ID[0]] = Neighbour(float(t_ID[1]), int(t_ID[2]), time.time() + timeout_interval)
    rout_path[t_ID[0]] = Path(float(t_ID[1]), ID)
for id, neighbour in neighbours_paths.items():
    for id2, neighbour2 in neighbours_paths.items():
        neighbour.paths[id2] = Path(math.inf, ID)

threading.Thread(target=make_ready).start()
threading.Thread(target=rec_input).start()
threading.Thread(target=menu).start()
threading.Thread(target=check_alive).start()
