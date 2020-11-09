import sys
from datetime import datetime
import socket

TIME_FORMAT = "%d-%m-%Y-%H-%M-%S"
def get_date_as_str(date):
    """ this function return date string from datetime object """
    return date.strftime(TIME_FORMAT)

def get_date_from_str(date_str):
    """ this function return datetime object from string """
    return datetime.strptime(date_str, TIME_FORMAT)

def parse_entery(ent):
    """ this function parse entery to known format """
    separator = ','
    ents = ent.split(separator)
    if len(ents) < 4: # in a case of static entery
        ents.append(datetime.max)
    else: # dynemic entery
        ents[3] = get_date_from_str(ents[3])
    return ents

def write_to_file(file_path, enterys_dict):
    """ write enterys dict to file """
    with open(file_path, 'w') as f:
        for i in enterys_dict:
            entery = [i, enterys_dict[i]["ip"], enterys_dict[i]["ttl"]]
            # check if the entery is dymanic 
            if enterys_dict[i]["last_modf"] is not datetime.max:
                entery.append(get_date_as_str(enterys_dict[i]["last_modf"]))
            f.write(",".join(entery) + "\n")

def read_init_file(path):
    """ this function read a file that contain entery in every line:
    name, ip, TTL
    and return dictionary (key = name, value = dictionary of IP and TTL) """
    with open(path) as f:
        content = f.read().splitlines()
    enterys = {}
    for line in content:
        name, ip, ttl, last_modf = parse_entery(line)
        entery = {
                "ip" : ip,
                "ttl" : ttl,
                "last_modf" : last_modf
                }
        enterys[name] = entery
    return enterys

def time_to_update(entery):
    """ this function check if we need to update the entery, return boolean """
    diff = (datetime.now() - entery["last_modf"]).total_seconds()
    return diff > float(entery["ttl"])


parent_ip = sys.argv[2]
parent_port = int(sys.argv[3])
## read from file
names = read_init_file(sys.argv[4])

## open a sockets for clients and parent
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', int(sys.argv[1]))) # bind to requsted port
# creat diffrent socket to connect parent for avoiding cases of
# wating for parent answaer while new requsting from client
parent_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

## get msg from client and handle 
while True:
    data, addr = client_socket.recvfrom(1024)
    data = data.decode()
    # check if need to ask parent server
    # it will happen when we don't have the info, or it is'nt up to date
    if data not in names or time_to_update(names[data]):
        parent_socket.sendto(data.encode(), (parent_ip, parent_port))
        new_data, _ = parent_socket.recvfrom(1024)
        new_data = new_data.decode()
        new_name, new_ip, new_ttl = new_data.split(',')
        new_entery = {"ip" : new_ip, "ttl" : new_ttl, "last_modf" :
                datetime.now()} # create the new entery
        if data in names: del names[data] # in a case of update
        names[new_name] = new_entery # save the new entery to dictionary
        write_to_file(sys.argv[4], names)
    ans = ",".join([data, names[data]["ip"], names[data]["ttl"]])
    client_socket.sendto(ans.encode(), addr) # send answer to client

## close connection
client_socket.close()
parent_socket.close()
