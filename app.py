import simplejson as json
import requests
import pandas as pd
from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure
from bokeh.embed import components

###
#Constants

API_KEY = "AQxy1jwjCgs9_xDvJ8bY"
QUANDL_URL = "https://www.quandl.com/api/v3/datasets/WIKI/"

#Keys
keys = ['Open',  'Adj. Open', 'Close', 'Adj. Close']
colors = {'Open': 'navy', 'Adj. Open': 'firebrick', 'Close': 'olive', 'Adj. Close': 'green'}
###

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def main():
  return redirect('/index')

@app.route('/index', methods=['POST','GET'])
def index():

  if request.method == 'POST':
    
    df, L = downloadStockForKey(request.form.get('ticker'))
    return plot_data(df, L)
  return render_template('index.html')

def downloadStockForKey(key):
  """
  Download stock data from Quandl.com for.
  """
  

  key = key.upper()
  r = requests.get(QUANDL_URL + key + ".json", params = {"api_key": API_KEY}, auth=('user', 'pass'))
  column_names = r.json()['dataset']['column_names']
  data = r.json()['dataset']['data']
  print column_names

  #Identify selected columns
  L = [key for key in keys if request.form.get(key) in keys]
  L.insert(0, 'Date')
  
  df = pd.DataFrame(data, columns = column_names)
  df = df[L]
  df['Date'] = pd.to_datetime(df['Date'], format='%Y-%m-%d')

  print df
  return df, L

def plot_data(df, L):
  
  
  plot = figure(title='Data from Quandle WIKI set',
              x_axis_label='date',
              x_axis_type='datetime')

  for column in L:

    if column == 'Date':
      continue
    print "adding column " + column
    plot.line(df['Date'], df[column], color=colors[column], legend = column)
    print(df['Date'])
    print(df[column])

  #plot = figure(plot_width=400, plot_height=400)
  #plot.patches([[1, 3, 2], [3, 4, 6, 6]], [[2, 1, 4], [4, 7, 8, 5]],color=["firebrick", "navy"], alpha=[0.8, 0.3], line_width=2)
  #plot = figure()
  #plot.circle([1,2], [3,4])

  script, div = components(plot)

  return render_template('plot.html', script=script, div=div)

if __name__ == '__main__':
  app.run(port=33507)
