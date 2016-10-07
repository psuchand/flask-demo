
from flask import Flask, render_template
 
app = Flask(__name__)

@app.route('/')
def homepage():

    title = "Epic Tutorials"
    paragraph = ["wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!","wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!wow I am learning so much great stuff!"]

    try:
        return render_template("index.html", title = title, paragraph=paragraph)
    except Exception, e:
        return str(e)

@app.route("/jackson-heights")
def jackson_heights():
  return render_template("jackson-heights.html")

@app.route('/about')
def aboutpage():

    title = "About this site"
    paragraph = ["blah blah blah memememememmeme blah blah memememe"]

    pageType = 'about'

    return render_template("index.html", title=title, paragraph=paragraph, pageType=pageType)


@app.route('/about/contact')
def contactPage():

    title = "About this site"
    paragraph = ["blah blah blah memememememmeme blah blah memememe"]

    pageType = 'about'

    return render_template("index.html", title=title, paragraph=paragraph, pageType=pageType)

@app.route('/simulation/<float:longitude>/<float:latitude>')
def aboutpage():

    pos = "(%.2f, %.2f)"%(longitude,latitude)
    print "pos = " + pos

    return render_template("simulation.html", simulation_results = pos)

 
if __name__ == "__main__":
  app.run(debug = True, host='0.0.0.0', port=8020, passthrough_errors=True)