
import websocket
import json, threading


system_state = {"P": 0, "I": 0, "D": 0, "running": 0, "realtemp": 0, "tarTemp": 0, "pidOut": 0}
ws = None

def on_message(ws, message):
    global system_state
    system_state = json.loads(message)
    print(system_state)

def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")

def init():
    global ws
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("ws://localhost:1337/",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    websocket_thread = threading.Thread(target=ws.run_forever)
    websocket_thread.start()


def main():



    init()  # Init interrupts, GPIO, ...

    try:
        while True:

            ws.send(json.dumps([input('Which value do you want to change? '), eval(input('To what value? '))]))
    except KeyboardInterrupt:
        print('interrupted with keyboard')
    except:
        print('unspecified error')

if __name__ == '__main__':
    main()