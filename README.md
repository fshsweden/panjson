# Build using 

```
poetry version       # check version
poetry version 0.1.9 # set version
poetry build
# result is in dist folder
```


## Local install using pip install [path-to-whl-file] --force-reinstall

### Example server:

```
import logging
import panjson as pj
from panjson import JsonTCPServer
from panjson import JsonTCPClientConnection
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


def conn_handler(client:JsonTCPClientConnection, connected:Boolean):
    logging.info(f"Client is connected: {connected}")

def message_handler(client:JsonTCPClientConnection, obj):
    logging.info(f"Message: {obj}")

def error_handler(client:JsonTCPClientConnection, error):
    logging.info(f"Error: {error}")

server = JsonTCPServer(host="0.0.0.0", port=3456)
server.setupMessageHandler(conn_handler=conn_handler, message_handler=message_handler, error_handler=error_handler)
server.accept_clients()
```

### Example client

```
from time import sleep
from panjson import JsonTCPClient
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

# Loop and connect/disconnect 10 times!
for i in range(10):
    logger.info("connecting...")
    client = JsonTCPClient()
    client.connect(host="localhost",port=6667)
    sleep(2)
    logger.info("disconnecting...")
    client.disconnect()
    sleep(2)
```
