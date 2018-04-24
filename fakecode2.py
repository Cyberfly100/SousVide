from time import time, sleep
import ws_broadcast as ws
import random
import json

x=time()

myws=ws.broadcast(8082)
try:
    while True:
        myws.send(json.dumps({'x':time()-x,'y1':random.randint(1,1000),'y2':random.randint(1,1000)}))
        sleep(2)
except KeyboardInterrupt:
        myws.server_close()
        print('server shut down')