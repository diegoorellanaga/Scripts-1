Title:    Scripts-1  
Author:    Diego Orellana  
Base Header Level:    2  

# Introduction #

These are one of the latest scripts I made that were actually used by a company.

## Email filter: unmanaged.py ##

This script was written in Python. The purpose of this script was to filter Information from certain emails. These emails were identified by their title, and all of them contained a table with a certain format and information. What this script does is to connect to the email server find the right emails then read the information from the table which is a list of IPs and macs. Then we connect to the API of a web page that gives us the vendor given the mac, with this information we create a third list of vendors. Once we obtain these 3 lists we proceed to filter information from this table. We know what information to filter by checking some files that will be stored in a given path, these files are one for Macs, one for IPs, and one for vendors. Each client will have its own set of filter files, therefore, for each client, we will have 3 filter files.

![diagram]

Once we get the filtered information we proceed to send it by email to a given destination. We used a cron job to execute this script periodically.


You need to set the credential of the server and the email addresses inside the script. The paths to the filter files and the filtered information are given as parameters.

Then in the crontab, you need to set your script in a way that you may register the exceptions and logs (all the prints commands).

Below we can find a example that tells us how to execute this script:

          python unmanage.py -i /root/unmanaged_filtro -m /root/unmanaged_filtro -v /root/unmanaged_filtro -d /root/unmanaged"


You must customize the following lines with your own information:

	mail=imaplib.IMAP4("192.168.xx.x", ###)
	mail.login("username","password")
	result, data = mail.uid('search', None, '(UNSEEN)','(HEADER Subject "Computer Detected without Symantec Client Software")')
	s.sendmail('diego.orellana@akainix.com','xxxxx@akainix.com',msg.as_string())
	s.sendmail('diego.orellana@akainix.com','diego.orellana@akainix.com',msg.as_string())

Also, the regex should be customized to fit your needs:

	macip=re.findall('(width3D"10%">[0-9]+(?:\.[0-9]+){3})<\/td><td (width3D"20%">[0-9a-f]{2}(?:-[0-9a-f]{2}){5})',raw_email3) #juntos

And any other line in order to fit your particular context.

## Luminol implementation: influxdbLuminol.py ##

The next script implements [luminol] for anomaly detection. We will be working with time series information like CPU usage, memory usage etc. After obtaining this information, by making queries to influx DB, we will analyze their possible anomalies by using [luminol]. 

Below we can find an explanation of the functions used:


## Function: encuentra_correlaciones(arrayts,arraynames,threshold2,threshold3)

### This function receives the following values as inputs:

  Parameter  | Value
  -----------| -------------
  arrayts    | Time series array
  arraynames | Time series names array
  treshold2  | Anomaly threshold
  treshold3  | Correlation threshold


### Returned Values

  Output      | Value
  -------------|-------------
  Correlations | Dictionary: Contains the correlations information given the anomalies.

### Code

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

    


## Function: plot_serie_anomalia(ts,x,y,threshold,ubicacion,title,ylabel,numgraph) 

#### This function plots the time series and their anomalies given a particular anomaly threshold.
### This function receives as input the following parameters:

  Parameter | Value
  ----------| -------------
  ts        | Dictionary: Time series
  x         | List: Time list from the time series
  y         | List: Value list from the time series
  threshold | Double: Anomaly threshold
  ubicacion | Int: Plot location in the figure
  title     | String:  Plot title
  ylabel    | String: y ax label
  numgraph  | Int: Number of plots in the figure
  

### This function doesn't return values

### Code

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
        #plt.show()

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



## Function: get_ts_from_influxdb(client,query,gen_name,value,time_value,numelements,acepta_fechas,fechas=None) 

#### This function returns a dictionary given a particular influxdb query, this dictionary contains a time series that has the right format for luminol.
### This function has the following parameters as inputs:

  Parameter         | Value
  ------------------|--------------------------------------
  client            | Client object: Influxdb client
  query             | String: influxdb query
  gen_name          | String: generator name, to know this value we must analyze the data returned by influxdb after making a query
  value             | String: value name of the time series
  time_value        | String: time name of the time series
  numelements       | Int: max amount of data that we want to obtain from the query
  acepta_fechas     | Bool: this parameter let us replace the time list from the time series for an external one (for debug).
  fechas            | List: External date list 
  
### Returned values
  
  Output | Value
  --------|---------
  x       | list: Contains the time values from the time series
  y       | list: Contains the values from the time series
  ts      | Dictionary: Contains the time values as keys and the values are the time series values 
  fechas  | list: Time values in unix time
  xlabel  | list: Contains the hours from the time series period in ISO 8601 format

### Code


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



%md

## Function: get_correlations_of_anomalies(ts1,ts2,ts1name,ts2name,threshold1,threshold2) 

#### Esta funcion encuentra las correlaciones en las anomalias dadas 2 series de tiempo.
### Esta funcion recibe como entrada los siguientes parametros:

  Parametro         | Valor
  ------------------|--------------------------------------
  ts1               | Dictionary: Serie de tiempo 1 a correlacionar
  ts2               | Dictionary: Serie de tiempo 2 a correlacionar
  ts1name           | String: nombre de la serie de tiempo 1
  ts2name           | String: nombre de la serie de tiempo 2
  threshold1        | Dobule: Umbral de la anomalia
  threshold2        | Double: Umbral de el coeficiente de correlacion

  
### Valores de retorno
  
  Retorno           | Valor
  ------------------|---------
  period_coef       | Dictionary: Contiene la informacion de las correlaciones


### Codigo


    def get_correlations_of_anomalies(ts1,ts2,ts1name,ts2name,threshold1,threshold2):

        period_coef={}
        key=0
        detector = luminol.anomaly_detector.AnomalyDetector(ts1,score_threshold=threshold1)
        anomalies = detector.get_anomalies()
        for a in anomalies:
            time_period = a.get_time_window()
            if (time_period[0]-time_period[1])!=0: 
                #print(len(ts1),len(ts2),ts1name,ts2name, time_period)
                my_correlator = Correlator(ts1, ts2, time_period)      
                if my_correlator.is_correlated(threshold=threshold2):
                    period_coef[key]={'factor':round(my_correlator.get_correlation_result().coefficient,3),'start_time':datetime.datetime.fromtimestamp(int(time_period[0])).strftime('%H:%M:%S'),'end_time':datetime.datetime.fromtimestamp(int(time_period[1])).strftime('%H:%M:%S')}
                    print(" ")
                    print "{3} se correlaciona con {4} en el periodo anomalo {0} - {1} con un coeficiente {2}".format(datetime.datetime.fromtimestamp(int(time_period[0])).strftime('%H:%M:%S'),datetime.datetime.fromtimestamp(int(time_period[1])).strftime('%H:%M:%S'),round(my_correlator.get_correlation_result().coefficient,3),ts1name,ts2name)   
                    print("")
                    key=key+1
                                           
        if key==0:
            print(" ")
            print("No se encontro correlacion durante los tiempo anomalos para: {0} y {1}".format(ts1name,ts2name))
            print(" ")
        return period_coef









%md

## Funcion: get_times(hour,minute, aproximar) 

#### Esta funcion fija el inicio y final de la series de tiempo.
### Esta funcion recibe como entrada los siguientes parametros:

  Parametro           | Valor
  --------------------|--------------------------------------
  hour                | Int: Cuantas horas a partir de ahora para atras queremos registrar las series de tiempo
  minute              | Minutos: Ademas de las horas podemos decir cuantos minutos hacia atras queremos. Horas y minutos se suman. 
  aproximar           | Boolean: True si queremos aproximar los segundos y microsegundos. Para usar luminol hay que aproximar los segundos.

  
### Valores de retorno
  
  Retorno             | Valor
  --------------------|---------
  start_timeUTC       | String: Valor del tiempo inicial de las series de tiempo (tiempo actual) UTC (influxdb entiende UTC)
  end_timeUTC         | String: Valor del final de las series de tiempo UTC
  start_time          | String: Valor del tiempo inicial de las series de tiempo (tiempo actual) 
  end_time            | String: Valor del final de las series de tiempo 


### Codigo


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



                










%md



# Ejemplo de uso

#### Se fijan los parametros del tiempo de la serie de tiempo y se guardan los valores

    aproximar=True
    times=get_times(12,0,aproximar)
    start_time=times[1]
    end_time=times[0]
    start_time_z=times[3]
    end_time_z=times[2]

### Se contruye la porcion del query de influxdb que pide el intervalo    

    :::python
    time_period="AND  time >= {0} AND time <= {1}".format(start_time,end_time)

### Se fijan los parametros para obtener la primera seria de tiempo

    numelements=1300
    client = InfluxDBClient(host='192.168.70.6', port=9086, username='root', password='P13Ak!ix', database='monstermometer')
    query="SELECT CargaCPU FROM UsoCPU WHERE hostname = 'Seeker.pentasec.local' {0} limit 1000;".format(time_period)
    gen_name='UsoCPU'
    value='CargaCPU'
    time_value='time'
    acepta_fechas=False
    
### Se fijan los parametros para obtener la segunda seria de tiempo    
    
    
    query2="SELECT StorageUsed*100/TotalSize FROM Storage WHERE hostname = 'Seeker.pentasec.local' AND Dispositivo = 'Physical Memory' {0} limit 1000; ".format(time_period) 
    gen_name2='Storage'
    value2='StorageUsed_TotalSize'
    time_value2='time'
    acepta_fechas2=False

### Se obtienen las series de tiempo (ts) y los valores asociados a estas.

    x,y,ts,fechas,xlabels = get_ts_from_influxdb(client,query,gen_name,value,time_value,numelements,acepta_fechas)
    x2,y2,ts2,fechas2,xlabel2=get_ts_from_influxdb(client,query2,gen_name2,value2,time_value2,numelements,acepta_fechas2)

### Para obtener las correlaciones. Se crean los parametros necesario: 

    arrayts=[ts,ts2]
    arraynames=["uso CPU","StorageUsed"]
    threshold2=3
    threshold3=0.8
    
### se ejecuta la funcion respectiva y se guarda el valor.

    correlaciones=encuentra_correlaciones(arrayts,arraynames,threshold2,threshold3)

### El diccionario de retorno tendra el siguiente formato:
### En el caso de abajo solo una combinacion presento correlaciones
### El ejemplo de abajo se hizo para 4 series de tiempo

    {'A.B. Entrante y A.B. Saliente': {},
     'A.B. Entrante y StorageUsed': {},
     'A.B. Entrante y uso CPU': {},
     'A.B. Saliente y A.B. Entrante': {},
     'A.B. Saliente y StorageUsed': {},
     'A.B. Saliente y uso CPU': {},
     'StorageUsed y A.B. Entrante': {},
     'StorageUsed y A.B. Saliente': {},
     'StorageUsed y uso CPU': {},
     'uso CPU y A.B. Entrante': {},
     'uso CPU y A.B. Saliente': {},
     'uso CPU y StorageUsed': {0: {'end_time': '13:36:05',
                                   'factor': 1.0,
                                   'start_time': '13:32:02'}}}




### Si se quiere graficar las series de tiempo con sus anomalias se reliza lo siguuiente:

### Se fijan variables de la figura como tamano y numeros de subfiguras
    
    plt.figure(figsize=(10,15))
    numgraph=4 #Numero de graficos

### Se fija el umbral de las anomalias y parametros del grafico

    threshold=3
    ubicacion=1 # Ubicacion de esta subfigura
    title='Carga CPU entre {0} y {1}'.format(start_time_z,end_time_z)
    ylabel='Carga CPU'

### Se grafica

    plot_serie_anomalia(ts,x,y,threshold,ubicacion,title,ylabel,numgraph)

### Se hacer lo mismo para n cantidades de subgraficos

    threshold=3
    ubicacion=2
    title='StorageUsed entre {0} y {1}'.format(start_time_z,end_time_z)
    ylabel='StorageUsed'

    plot_serie_anomalia(ts2,x,y2,threshold,ubicacion,title,ylabel,numgraph)


### Los graficos quedaran todos en una misma figura para efectos visuales.





### I hope you find this script useful. Let me know if you have any question. ###


[diagram]:	https://github.com/diegoorellanaga/Scripts-1/blob/master/Scriptdiagram.jpg

[luminol]:	https://github.com/linkedin/luminol


