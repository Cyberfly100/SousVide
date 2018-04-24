import random
from time import sleep, time
from tornado import gen
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Thread
 
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.document import without_document_lock
from bokeh.plotting import figure, curdoc


from bokeh.server.server import Server
 
t0=time()
 
executor = ThreadPoolExecutor(max_workers=2)
doc = curdoc()

print('HELLO')
def update_data(x,y1,y2):
    new_data=dict(t = [x], tarTemp = [y1], temp = [y2])
    data.stream(new_data, 10000)
 
 
def main():
    while True:
        doc.add_next_tick_callback(partial(update_data, x=time()-t0, y1=random.randint(0,100), y2=random.randint(0,100)))
        sleep(1)
 
 
data=ColumnDataSource(dict(t=[], tarTemp=[], temp=[]))
fig=figure(logo=None)
fig.xaxis.axis_label = 'Time (s)'
fig.line(source=data, x='t', y='tarTemp', line_width=2, alpha=.85, color='pink')
fig.line(source=data, x='t', y='temp', line_width=2, alpha=.85, color='purple')
 
 
doc.add_root(fig)

thread = Thread(target=main)
thread.start()

server = Server(
    bokeh_applications,  # list of Bokeh applications
    io_loop=loop,        # Tornado IOLoop
    **server_kwargs      # port, num_procs, etc.
)

# start timers and services and immediately return
server.start()