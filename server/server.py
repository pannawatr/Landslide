import os
import datetime
import requests
import numpy as np
import pandas as pd
from flask import Flask, jsonify
from flask_cors import CORS

# ANN
from keras.models import load_model
from sklearn.preprocessing import LabelEncoder
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import StandardScaler

app = Flask(__name__)
CORS(app)
@app.route('/api/home')
def home():
    rain_total = pd.read_csv('static/rain_total.csv')
    area_name = rain_total['area_name'].tolist()
    rain_1d = rain_total['rain_1d'].tolist()
    rain_5d = rain_total['rain_5d'].tolist()
    return jsonify({'datetime': datetime.datetime.now().strftime('%d/%m/%Y'), 'rain_1d': [f"{num:.1f}" for num in rain_1d], 'rain_5d': [f"{num:.1f}" for num in rain_5d], 'area_name': area_name})

if __name__ == '__main__':
    app.run(debug=True)
"""


# Task function
def request_rain():
    url = "http://ews1.dwr.go.th/website/webservice/rain_daily.php?uid=landslide2022cm&upass=cicecmu2020&dmode=2&dtype=2&ondate=dd/mm/yyyy"
    req = requests.get(url).json()

    # Request rain from ews
    rain_station_csv = pd.read_csv('static/rain_station.csv')
    rain_total: list = [0.0 for i in range(5)]
    rain_station: list = [0.0 for i in range(len(rain_station_csv))]
    
    for i in req['station']:
        for j in range(len(rain_station_csv)):
            if i['id'] == rain_station_csv['station_id'][j]:
                rain_total[int(rain_station_csv['area_id'][j] - 1)] += float(i['rain07h'])
                rain_station[j] = (str(i['rain07h'])) 
    len_area = rain_station_csv.groupby('area_id').count()
    for i in range(len(rain_total)):
        rain_total[i] /= int(len_area['station_id'].iloc[i])
    
    # Save rain station
    rain_station_csv['rain_1d'] = rain_station
    rain_station_csv.to_csv('static/rain_station.csv', index=False)

    # Save rain
    rain_total_csv = pd.read_csv('static/rain_total.csv')
    rain_total_csv['rain_1d'] = rain_total
    rain_total_csv.to_csv('static/rain_total.csv', index=False)
    return rain_total


def predict_ls(area_type: str):
    filepath: str = 'static/model/0' + area_type +'.csv'
    LSmodel = load_model('static/model/model.h5')
    dataset = pd.read_csv(filepath)
    rain_station_csv = pd.read_csv('static/rain_station.csv')
    rain_station = rain_station_csv[rain_station_csv['area_id'] == int(area_type)]['rain_1d'].tolist()
    newRain = []
    for i in range(len(dataset)):
        x: float = 0
        y: float = 0
        for j in range(len(rain_station)):
            x += (rain_station[j]/dataset.iloc[i][j+8])
            y += (1/dataset.iloc[i][j+8])
        newRain.append(x/y)
    print(len(newRain), len(dataset))
    dataset['IDW-5d'] = pd.DataFrame(newRain)
    dataset.to_csv(filepath, index=False, mode= 'w')
    dataset.isnull().sum()
    X = dataset.iloc[:,1:5].values
    sl = dataset.iloc[:,3].values
    le = LabelEncoder()
    X[:, 1] = le.fit_transform(X[:, 1])
    ct = ColumnTransformer(transformers=[('encoder', OneHotEncoder(), [0])], remainder='passthrough')
    X = np.array(ct.fit_transform(X))
    sc = StandardScaler()
    X_test  = sc.fit_transform(X)
    meanSt1 = 26.9769               
    sdSt1 = 20.7869
    rainSt1 = X[:,7]
    stardScaleSt1 = (rainSt1 - meanSt1)/sdSt1
    X_test[:,7] = stardScaleSt1
    meanSt2 = 12.8612               
    sdSt2 = 5.185
    rainSt2 = X[:,6]
    stardScaleSt2 = (rainSt2 - meanSt2)/sdSt2
    X_test[:,6] = stardScaleSt2
    y_pred = LSmodel.predict(X_test)
    normalized = (sl-min(sl))/(max(sl)-min(sl))
    for i in range(len(y_pred)):
        if sl[i] >= 5:
            y_pred[i] = normalized[i]*y_pred[i]
        else:
            y_pred[i] = 0
    df = pd.DataFrame(y_pred)
    df_csv = pd.read_csv(filepath)
    df_csv['ls_prob'] = df
    df_csv.to_csv(filepath, index=False, mode= 'w')


# Everday at 7:00
def update_rain_cumulative(rain_total: list):
    rain_cumulative_csv = pd.read_csv('static/rain_cumulative.csv')
    rain_cumulative_csv['d5'] = rain_cumulative_csv['d4'] + rain_cumulative_csv['d3'] + rain_cumulative_csv['d2'] + rain_cumulative_csv['d1']
    rain_cumulative_csv['d4'] = rain_cumulative_csv['d3'] + rain_cumulative_csv['d2'] + rain_cumulative_csv['d1']
    rain_cumulative_csv['d3'] = rain_cumulative_csv['d2'] + rain_cumulative_csv['d1']
    rain_cumulative_csv['d2'] = rain_cumulative_csv['d1']
    rain_cumulative_csv['d1'] = rain_total
    rain_cumulative_csv.to_csv('static/rain_cumulative.csv', index=False)

    # Save rain 5 day to rain_total.csv
    rain_total_csv = pd.read_csv('static/rain_total.csv')
    rain_total_csv['rain_5d'] = rain_cumulative_csv['d5']
    rain_total_csv.to_csv('static/rain_total.csv', index=False)
"""

"""
rain_total = request_rain()
update_rain_cumulative(rain_total)
predict_ls(area_type='1')
predict_ls(area_type='2')
predict_ls(area_type='3')
predict_ls(area_type='4')
predict_ls(area_type='5')
"""