#!/usr/bin/env python

import http.server
import threading
import logging
from ws_broadcast import WebsocketServer
import json


class broadcast:
    def __init__(self, PORT=1337):
        self.system_state = {"P": 0, "I": 0, "D": 0, "running": 0, "realtemp": 0, "tarTemp": 0, "pidOut": 0}
        self.port = PORT

        def new_message(client, server, message):
            print("client " + str(client["address"]) + " asks " + message)
            command = json.loads(message)
            self.system_state[command[0]] = command[1]

            self.server.send_message_to_all(json.dumps(self.system_state))

        def new_client(client, server):
            print("New client " + str(client["address"]) +
                  " connected to port " + str(PORT) + ". ")

        self.server = WebsocketServer(
            PORT, host='0.0.0.0', loglevel=logging.INFO)
        self.server.set_fn_new_client(new_client)
        self.server.set_fn_message_received(new_message)

        thread_websocket = threading.Thread(target=self.server.run_forever)
        thread_websocket.daemon = True
        thread_websocket.start()

    def close(self):
        self.server.server_close()


bc = broadcast()
while True:
    input("Input to stop the program")
