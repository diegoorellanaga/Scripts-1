%pyspark
# -*- coding: utf-8 -*-
"""
Created on Wed May 31 15:51:03 2017

@author: diego.orellana
"""
import pprint
from luminol import exceptions, utils
from luminol.modules.time_series import TimeSeries
import csv
import luminol
import luminol.anomaly_detector
import datetime
from datetime import timedelta
import time
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from influxdb import InfluxDBClient
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
from luminol.correlator import Correlator

def encuentra_correlaciones(arrayts,arraynames,threshold2,threshold3):
    correlations={}
    length=len(arrayts)
    for i in range(length):
        ts1=arrayts[i]
        name1=arraynames[i]
        for j in range(length):
            ts2=arrayts[j]
            name2=arraynames[j]
            if name2==name1:
                continue
            correlations["{0} y {1}".format(name1,name2)]=get_correlations_of_anomalies(ts1,ts2,name1,name2,threshold2,threshold3)
            
    return correlations      

def plot_serie_anomalia(ts,x,y,threshold,ubicacion,title,ylabel,numgraph):
    detector = luminol.anomaly_detector.AnomalyDetector(ts,score_threshold=threshold)
    anomalies = detector.get_anomalies()
    ax=plt.subplot(numgraph,1,ubicacion)
    plt.xlabel("Periodo {0} a {1}".format(datetime.datetime.fromtimestamp(int(ts.keys()[0])).strftime('%Y-%m-%d'),datetime.datetime.fromtimestamp(int(ts.keys()[-1])).strftime('%Y-%m-%d'))) # datetime.datetime.fromtimestamp(int(ts.keys()[0])).strftime('%Y-%m-%d')
    plt.ylabel("{0}".format(ylabel))
    plt.title("{0}. Umbral de anomalia: {1}/9".format(title,threshold))
    plt.grid(True)
    plt.plot(x,y, lw=2)
    ax.set_xticks(x[0::10])
    ax.set_xticklabels( xlabels[0::10], rotation=90 )

    for anomaly in anomalies:
        anomaly_y1 = ts[anomaly.start_timestamp]
        anomaly_y2 = ts[anomaly.end_timestamp]
        anomaly_y = [anomaly_y1,anomaly_y2]
        x1 = datetime.datetime.fromtimestamp(int(anomaly.start_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        x2 = datetime.datetime.fromtimestamp(int(anomaly.end_timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        x1 = datetime.datetime.strptime(x1, "%Y-%m-%d %H:%M:%S")
        x2 = datetime.datetime.strptime(x2, "%Y-%m-%d %H:%M:%S")
        anomaly_x = [x1, x2]
        plt.plot(anomaly_x, anomaly_y, 'ro')

def get_ts_from_influxdb(client,query,gen_name,value,time_value,numelements,acepta_fechas,fechas=None):
    ts={}
    x=[]
    y=[]
    xlabels=[]
    if not acepta_fechas:
        fechas=[]
    kk=0
    result = client.query(query)
    Falla=True
    for n in result[gen_name]:
        d = datetime.datetime.strptime(n[time_value], '%Y-%m-%dT%H:%M:%S%fZ')  #'%Y-%m-%dT%H:%M:%S.%fZ' #el punto hace los segundos float
        fecha = time.mktime(d.timetuple())     
        if acepta_fechas:
            if kk==len(fechas):
                break
            ts[fechas[kk]]=n[value]
        else:
            fechas.append(fecha)
            ts[fecha]=n[value]
        tiempo = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute,0)
        #tiempo = datetime.datetime(d.year, d.month,d.day, d.hour, d.minute)
        xlabels.append("{0}:{1}".format(d.hour,d.minute))
        x.append(tiempo)
        y.append(n[value])
        kk=kk+1
        if kk==numelements:
            print("numero de elementos de {1} es: {0}".format(numelements,gen_name))
            Falla=False
            break
        
    if Falla:
        print("numero de elementos de {1} es {2}, menor que maximo fijado: {0}".format(numelements,gen_name,len(ts)))
    return [x,y,ts,fechas,xlabels]

def get_correlations_of_anomalies(ts1,ts2,ts1name,ts2name,threshold,threshold2):

    period_coef={}
    key=0
    detector = luminol.anomaly_detector.AnomalyDetector(ts1,score_threshold=3)
    anomalies = detector.get_anomalies()
    for a in anomalies:
      time_period = a.get_time_window()
      if (time_period[0]-time_period[1])!=0: 
          #print(len(ts1),len(ts2),ts1name,ts2name, time_period)
          my_correlator = Correlator(ts1, ts2, time_period)      
          if my_correlator.is_correlated(threshold=threshold2):
              period_coef[key]={'factor':round(my_correlator.get_correlation_result().coefficient,threshold),'start_time':datetime.datetime.fromtimestamp(int(time_period[0])).strftime('%H:%M:%S'),'end_time':datetime.datetime.fromtimestamp(int(time_period[1])).strftime('%H:%M:%S')}
              print(" ")
              print "{3} se correlaciona con {4} en el periodo anomalo {0} - {1} con un coeficiente {2}".format(datetime.datetime.fromtimestamp(int(time_period[0])).strftime('%H:%M:%S'),datetime.datetime.fromtimestamp(int(time_period[1])).strftime('%H:%M:%S'),round(my_correlator.get_correlation_result().coefficient,3),ts1name,ts2name)   
              print("")
              key=key+1
                                           
    if key==0:
        print(" ")
        print("No se encontro correlacion durante los tiempo anomalos para: {0} y {1}".format(ts1name,ts2name))
        print(" ")
    
    return period_coef

def get_times(hour,minute, aproximar):
    
    startHourDateTimeUTC = datetime.datetime.utcnow()
    endHourDateTimeUTC = datetime.datetime.utcnow() - timedelta(hours = hour) - timedelta(minutes = minute)
    
    startHourDateTime = datetime.datetime.now()
    endHourDateTime = datetime.datetime.now() - timedelta(hours = hour) - timedelta(minutes = minute)
    
    if aproximar:
        startHourDateTimeUTC=startHourDateTimeUTC.replace(second=0, microsecond=0)
        endHourDateTimeUTC=endHourDateTimeUTC.replace(second=0, microsecond=0)

        startHourDateTime=startHourDateTime.replace(second=0, microsecond=0)
        endHourDateTime=endHourDateTime.replace(second=0, microsecond=0)

    start_timeUTC ="'{0}'".format(startHourDateTimeUTC.strftime('%Y-%m-%dT%H:%M:%SZ'))
    end_timeUTC ="'{0}'".format(endHourDateTimeUTC.strftime('%Y-%m-%dT%H:%M:%SZ'))
    


    start_time ="'{0}'".format(startHourDateTime.strftime('%Y-%m-%d'))
    end_time ="'{0}'".format(endHourDateTime.strftime('%Y-%m-%d'))
    
    return [start_timeUTC,end_timeUTC,start_time,end_time]

    

aproximar=True
times=get_times(12,0,aproximar)

start_time=times[1]
end_time=times[0]
start_time_z=times[3]
end_time_z=times[2]

time_period="AND  time >= {0} AND time <= {1}".format(start_time,end_time)
numelements=1300

client = InfluxDBClient(host='192.168.xx.xx', port=9086, username='root', password='password', database='database_name')
query="SELECT CargaCPU FROM UsoCPU WHERE hostname = 'xxxx.pentasec.local' {0} limit 1000;".format(time_period)
gen_name='UsoCPU'
value='CargaCPU'
time_value='time'
acepta_fechas=False

query2="SELECT StorageUsed*100/TotalSize FROM Storage WHERE hostname = 'xxxx.pentasec.local' AND Dispositivo = 'Physical Memory' {0} limit 1000; ".format(time_period) 
gen_name2='Storage'
value2='StorageUsed_TotalSize'
time_value2='time'
acepta_fechas2=False

query3="SELECT non_negative_derivative(last(TraficoEntrante), 8s) FROM Network WHERE hostname = 'xxxx.pentasec.local' AND NombreInterfaz =~ /.*Broadcom BCM943228HMB 802.11abgn 2x2 Wi-Fi Adapter\S$/ {0} GROUP BY time(1s) limit 1000;".format(time_period)  
gen_name3='Network'
value3='non_negative_derivative'
time_value3='time'
acepta_fechas3=False

query4="SELECT non_negative_derivative(last(TraficoSaliente), 8s) FROM Network WHERE hostname = 'xxxx.pentasec.local' AND NombreInterfaz =~ /.*Broadcom BCM943228HMB 802.11abgn 2x2 Wi-Fi Adapter\S$/ {0} GROUP BY time(1s) limit 1000;".format(time_period) 
gen_name4='Network'
value4='non_negative_derivative'
time_value4='time'
acepta_fechas4=False


#> SELECT non_negative_derivative(last("TraficoEntrante"), 8s) FROM "Network" WHERE "hostname" = 'xxxx.pentasec.local' AND "NombreInterfaz" =~ /.*Broadcom BCM943228HMB 802.11abgn 2x2 Wi-Fi Adapter\S$/ AND time > now() - 12h GROUP BY time(60s);
#SELECT non_negative_derivative(last("TraficoEntrante"), 1s) FROM "Network" WHERE "hostname" = 'xxxx.pentasec.local' AND "NombreInterfaz" =~ /.*Broadcom BCM943228HMB 802.11abgn 2x2 Wi-Fi Adapter\S$/ AND time > now() - 12h GROUP BY time(60s) limit 1000;


x,y,ts,fechas,xlabels = get_ts_from_influxdb(client,query,gen_name,value,time_value,numelements,acepta_fechas)
x2,y2,ts2,fechas2,xlabel2=get_ts_from_influxdb(client,query2,gen_name2,value2,time_value2,numelements,acepta_fechas2)
x3,y3,ts3,fechas3,xlabel3=get_ts_from_influxdb(client,query3,gen_name3,value3,time_value3,numelements,acepta_fechas3)
x4,y4,ts4,fechas4,xlabel4=get_ts_from_influxdb(client,query4,gen_name4,value4,time_value4,numelements,acepta_fechas4)


plt.figure(figsize=(10,15))
numgraph=4 #Numero de graficos

threshold=3
ubicacion=1
title='Carga CPU entre {0} y {1}'.format(start_time_z,end_time_z)
ylabel='Carga CPU'

plot_serie_anomalia(ts,x,y,threshold,ubicacion,title,ylabel,numgraph)

threshold=3
ubicacion=2
title='StorageUsed entre {0} y {1}'.format(start_time_z,end_time_z)
ylabel='StorageUsed'

plot_serie_anomalia(ts2,x,y2,threshold,ubicacion,title,ylabel,numgraph)

threshold=3
ubicacion=3
title='Ancho de banda entrante entre {0} y {1}'.format(start_time_z,end_time_z)
ylabel='Derivada'

plot_serie_anomalia(ts3,x3,y3,threshold,ubicacion,title,ylabel,numgraph)

threshold=3
ubicacion=4
title='Ancho de banda saliente entre {0} y {1}'.format(start_time_z,end_time_z)
ylabel='Derivada'

plot_serie_anomalia(ts4,x4,y4,threshold,ubicacion,title,ylabel,numgraph)


plt.show()




  
arrayts=[ts,ts2,ts3,ts4]
arraynames=["uso CPU","StorageUsed","A.B. Entrante","A.B. Saliente"]
threshold2=3
threshold3=0.8
        
get_correlations_of_anomalies(ts2,ts4,"uso CPU","StorageUsed",threshold,threshold2)
kk=encuentra_correlaciones(arrayts,arraynames,threshold2,threshold3)
print(" ")
print(" ")
pprint.pprint(kk)


