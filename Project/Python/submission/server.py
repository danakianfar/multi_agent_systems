from flask import Flask
from flask import request
from dummy_controller import *
from main_bus import MainBus
import pickle
import time

app = Flask('NetLogo_API')
# with open('m_support.pkl', 'rb') as f:
#     M_init_dist = pickle.load(f)
# with open('adj_distance_matrix.pkl', 'rb') as f:
#     adj_matrix = pickle.load(f)
controller = Controller(MainBus) #, M_init_dist, adj_matrix)

@app.route("/tick", methods = ['POST'])
def hello():
    # print('Call Made from %s' % request.form['bus_id'])
    # start_time = time.monotonic()

    commands = controller.tick(request.form)

    response = NetLogoAction.ACT_TYPE_CMD_DELIM.join([str(cmd) for cmd in commands])

    # print('Elapsed time for response %.4f' % (time.monotonic() - start_time))
    # print('Response sent to %s' % request.form['bus_id'])
    return response

if __name__ == "__main__":
    app.run(debug=False)