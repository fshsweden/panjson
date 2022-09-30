import socket
from _thread import *
import queue
import uuid
import json

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

from .send_json import send_dict_json, recv_line, send_string

# ================================================================
#
# ================================================================
class JsonTCPClient:

    # ------------------------------------------------------------
    # Connect and start a reader loop.
    # ------------------------------------------------------------
    def connect(self, host, port):

        self.host = host
        self.port = port
        self.sock = None
        
        self.inq = queue.Queue(10000)
        self.outq = queue.Queue(10000)

        self.quit_write_thread = False
        self.quit_read_thread = False

        self.clientid = str(uuid.uuid1())

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            logger.info("Connecting to: {}:{}".format(host, port))
            self.sock.connect((host, port))
            logger.info("Connected! - Starting worker threads")
            logger.info(f"Socket is {self.sock}")
            self.handle_connection_status("connected")
            
            start_new_thread(self.write_thread, ())
            start_new_thread(self.read_thread, ())

        except Exception as e:
            logger.info("Got an exception {} trying to connect".format(str(e)))
            self.handle_connection_status("disconnected")

        logger.info("Exiting connect_to_service()")

    # ------------------------------------------------------------
    #
    # ------------------------------------------------------------
    def inq_size(self):
        return self.inq.qsize()

    # ------------------------------------------------------------
    #
    # ------------------------------------------------------------
    def outq_size(self):
        return self.outq.qsize()
            
    # ------------------------------------------------------------
    #
    # ------------------------------------------------------------
    def read_thread(self):
        logger.info("+++ ENTR +++ read_thread()")
        try:
            cont = True
            while cont and not self.quit_read_thread:
                try:
                    line = recv_line(self.sock)
                    msg = json.loads(line)
                    self.handle_message(msg)
                except Exception as e:
                    logger.info(f"Exception in read_thread... {e}")
                    logger.info(str(e))
                    self.handle_exception(e)
                    cont = False
        finally:
            logger.info("Closing socket from read_thread...")
            self.sock.close()
            logger.info("+++ EXIT +++ read_thread()")
            self.handle_connection_status("disconnected")

        logger.info(f"Exiting read-thread!!")

    # ------------------------------------------------------------
    #
    # ------------------------------------------------------------
    def write_thread(self):
        logger.info("+++ ENTR +++ write_thread()")
        while not self.quit_write_thread:

            out_msg = self.outq.get(block=True)

            try:
                if type(out_msg) is dict:
                    send_dict_json(self.sock, out_msg)
                else:
                    send_string(self.sock, out_msg)
            except Exception as e:
                self.handle_exception(e)
                logger.info(f"Exception: {e} - exiting write thread")

                self.quit_write_thread = True
                self.quit_read_thread = True
                return

        logger.info(f"Exiting write-thread since quit:_thread flag was set!!")

    # ------------------------------------------------------------
    #
    # ------------------------------------------------------------
    def handle_message(self, msg):
        self.inq.put(msg)


    # ------------------------------------------------------------
    #
    # ------------------------------------------------------------
    def handle_exception(self, e):
        msg = {
            "message": "exception",
            "exception": e
        }
        self.inq.put(msg)

    # ------------------------------------------------------------
    #
    # ------------------------------------------------------------
    def handle_connection_status(self, status):
        msg = {
            "message": "connection_status",
            "status": status
        }
        self.inq.put(msg)

    def send_msg(self, msg_json):
        self.outq.put(msg_json)

    def read_msg(self):
        m = self.inq.get(block=True)
        return m

    def disconnect(self):

        logger.info(f"Disconnecting socket {self.sock}!")
        try:
            self.quit_write_thread = True
            self.quit_read_thread = True
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except Exception as e:
            logger.info(f"Exception: {e}")

