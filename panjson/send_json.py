import json
import socket
import logging
#########################################
l = logging.INFO
logging.basicConfig(
    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d in function %(funcName)s] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=l
)
logger = logging.getLogger(__name__)
logger.setLevel(level=l)
#########################################

import json

#
# String data without length (possibly terminated by \r\n?)
# JSON data is sent as strings
#
def send_string(sock: socket, data: str):
    # data is bytes()
    sock.sendall(data.encode("utf-8"))

#
# Receive string data, as byte by byte...
#
def recv_line(sock: socket) -> str:
    buffer = bytearray()
    chunk = sock.recv(1)
    # read chars until we hit a NL
    while chunk != b'\n':
        buffer += chunk
        try:
            chunk = sock.recv(1)
            if len(chunk) == 0:
                raise ConnectionError("Lost connection")
        except Exception as e:
            logger.error(e)
            raise e
            
    s = buffer.decode('utf-8')
    return s

# an alias since json was really a dict!
def send_json(sock: socket, d: dict):
    send_dict_json(sock, d)

def send_dict_json(sock: socket, d: dict):
    #convert dictionary to bytes
    message = json.dumps(d) + "\r\n"
    send_string(sock, message)



