import simplejson as json
import requests
from flask import Flask, render_template, request, redirect

###
#Constants

API_KEY = "AQxy1jwjCgs9_xDvJ8bY"
QUANDL_URL = "https://www.quandl.com/api/v3/datasets/WIKI/"
###

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

@app.route('/index')
def index():
  downloadStockForKey("FB")
  return render_template('index.html')

def downloadStockForKey(key):
  """
  Download stock data from Quandl.com for. 
  

  """
  r = requests.get(QUANDL_URL + key + ".json", params = {"api_key": API_KEY}, auth=('user', 'pass'))
  print(r.json())

if __name__ == '__main__':
  app.run(port=33507)
