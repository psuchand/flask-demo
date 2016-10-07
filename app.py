
from flask import Flask, render_template
from ml_helper_functions import *

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

    pos = "(%s, %s)"%(longitude,latitude)
    simulate_naive_trajectory

    return render_template("simulation.html", simulation_results = pos)

 
if __name__ == "__main__":
  app.run(debug = True, host='0.0.0.0', port=8020, passthrough_errors=True)