import sys
from datetime import datetime
import socket
TIME_FORMAT = "%d-%m-%Y-%H-%M-%S"
def get_date_as_str(the_date):
    """ this function return date string from datestring object """
    return the_date.strftime(TIME_FORMAT)
def get_date_from_str(the_date_str):
    """ this function return datetime object from string) """
    return datetime.strptime(the_date_str, TIME_FORMAT)
def parse_entery(ent):
    """ this function parse entery to known format """
    separator = ','
    ents = ent.split(separator)
    if len(ents) < 4:
        ents.append(datetime.max)
    else:
        ents[3] = get_date_from_str(ents[3])
    return ents
def write_to_file(file_path, ents_dict):
    """ write enterys dict to file """
    with open(file_path, 'w') as f:
        for i in ents_dict:
            ent = [i, ents_dict[i]["ip"], ents_dict[i]["ttl"]]
            if ents_dict[i]["last_modf"] is not datetime.max:
                ent.append(get_date_as_str(ents_dict[i]["last_modf"]))
            f.write(",".join(ent) + "\n")

def read_init_file(path):
    """ this function read a file that contain in every line entery: name, ip,
    TTL
    and return dictionary (key = name, value = dictionary of IP and TTL) """
    with open(path) as f:
        content = f.read().splitlines()
    enterys = {}
    for i in content:
        name, ip, ttl, last_modf = parse_entery(i)
        entery = {
                "ip" : ip,
                "ttl" : ttl,
                "last_modf" : last_modf
                }
        enterys[name] = entery
    return enterys
## read from file
parent_ip = sys.argv[2]
parent_port = int(sys.argv[3])
names = read_init_file(sys.argv[4])

## open a sockets for clients and parent
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.bind(('', int(sys.argv[1])))
# creat diffrent socket to connect parent for avoiding cases of
# wating for parent answaer while new requsting from client
parent_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

## get msg from client and handle 
while True:
    data, addr = client_socket.recvfrom(1024)
    data = data.decode()
    if data not in names or ((datetime.now() -
        names[data]["last_modf"]).total_seconds() > float(names[data]["ttl"])):
        parent_socket.sendto(data.encode(), (parent_ip, parent_port))
        new_data, _ = parent_socket.recvfrom(1024)
        new_data = new_data.decode()
        new_name, new_ip, new_ttl = new_data.split(',')
        new_entery = {"ip" : new_ip, "ttl" : new_ttl, "last_modf" :
                datetime.now()}
        if data in names: del names[data] # in a case of update
        names[new_name] = new_entery
        write_to_file(sys.argv[4], names)
    ans = ",".join([data, names[data]["ip"], names[data]["ttl"]])
    client_socket.sendto(ans.encode(), addr)

## close connection
client_socket.close()
parent_socket.close()
