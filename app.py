from flask import Flask, render_template
from ml_helper_functions import *

import sys
from cStringIO import StringIO

app = Flask(__name__)

@app.route('/')
def homepage():

    try:
        return render_template("index.html")
    except Exception, e:
        return str(e)

@app.route("/jackson-heights")
def jackson_heights():
  return render_template("jackson-heights.html")


@app.route('/simulation/<longitude>/<latitude>')
def show_simulation_results(longitude,latitude):
    print "show_simulation_results"

    starting_hour = 9
    max_trip_length_seconds = 60*60
    starting_pos = "(%s, %s)"%(longitude,latitude)

    backup = sys.stdout

    #Capture output
    sys.stdout = StringIO()
    simulate_naive_trajectory(rides, starting_pos, starting_hour, max_trip_length_seconds)
    result = sys.stdout.getvalue()
    sys.stdout.close()
    sys.stdout = backup

    return render_template("simulation.html", simulation_results = results)
 
if __name__ == "__main__":
  app.run(debug = True, host='0.0.0.0', port=8020, passthrough_errors=True)