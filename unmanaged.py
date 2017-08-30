#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu May 25 09:20:13 2017

@author: diego.orellana
"""

import sys, getopt, json
from collections import namedtuple
import imaplib
import email
import re
import urllib2
import codecs
import pandas as pd
import numpy as np
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import csv


#ejemplo #example
#destino='d:\Users\d.orellana\Desktop'
#filedeleteip='d:\Users\d.orellana\Desktop\Diego_akainix_files\Mail\ips.txt'
#filedeletemac='d:\Users\d.orellana\Desktop\mac\mac.txt'
#filedeleteven="d:\\Users\\d.orellana\\Desktop\\ven\\ven.txt"
files = open("workfile","w")
files.write("Hello World")
files.close()
def main(argv):
    def filterByIp2(ips,macs,vends,listofip):

        length=len(listofip)
        for k in range(length):
            indices = [i for i, x in enumerate(ips) if x == listofip[k]]
            length2=len(indices)
            p=0
            for j in range(length2):
                p=p-1
                ips.pop(indices[p])
                macs.pop(indices[p])
                vends.pop(indices[p])
                print("{2} Borrando ip {0} con indice {1}".format(listofip[k],indices[p],str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        return [ips,macs,vends]

    def filterByMac2(ips,macs,vends,listofmac):

        length=len(listofmac)
        for k in range(length):
            indices = [i for i, x in enumerate(macs) if x == listofmac[k]]
            length2=len(indices)
            p=0
            for j in range(length2):
                p=p-1
                ips.pop(indices[p])
                macs.pop(indices[p])
                vends.pop(indices[p])
                print("{2} Borrando mac {0} con indice {1}".format(listofmac[k],indices[p],str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        return [ips,macs,vends]

    def filterByVen2(ips,macs,vends,listofven):

        length=len(listofven)
       # print("largo lista vendors: {0} ".format(length))
       # print("largo ips: {0} ".format(len(ips)))
        for k in range(length):
            indices = [i for i, x in enumerate(vends) if x == listofven[k]]
            length2=len(indices)
           # print("largo indices: {0} ".format(length2))
            p=0
            for j in range(length2):
                p=p-1
               # print("largo ips: {0} ".format(len(ips)))
               # print("value of p {0}".format(p))
               # print("indice a sacar {0}".format(indices[p]))
                ips.pop(indices[p])
                macs.pop(indices[p])
                vends.pop(indices[p])
                print("{2} Borrando vendor {0} con indice {1}".format(listofven[k],indices[p],str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        return [ips,macs,vends]
    filedeleteip= ''
    filedeletemac= ''
    filedeleteven= ''
    destino=''
    try:
        opts, args = getopt.getopt(argv,"hi:m:v:d:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -i <pathtofolder> -m <pathtofolder> -v <pathtofolder> -d <full_destinofinal>')
        print("example: python unmanage.py -i /root/unmanaged_filtro -m /root/unmanaged_filtro -v /root/unmanaged_filtro -d /root/unmanaged")
        print("En el ejemplo suponemos que dentro de la carpeta unmanaged_filtro")
        print("se encuentran las carpetas con el nombre de los dominios")
        print("por ejemplo: euromaerica conchaytoro etc.")
        print("y dentro de estas carpetas encontramos 3 archivos")
        print("ven.txt ip.txt y mac.txt")
        print("estos archivos contienen los vendor, mac e ip que queremos filtrar")
        print("la forma de escribirlos es uno en cada linea")
        print("sin comillas ni doble comillas y de la misma manera en que estan")
        print("escritos en el email original")
        print("")
        print("De la misma manera la carpeta unmanaged contiene carpetas con nombre de los dominios")
        print("En estas carpetas se guardara el resultado final como archivo csv")
        print("Estas carpetas hay que crearlas de antemano")
        print("")
        sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
           print( 'test.py -i <pathtofolder> -m <pathtofolder> -v <pathtofolder> -d <full_destinofinal>')
           print("example: python unmanage.py -i /root/unmanaged_filtro -m /root/unmanaged_filtro -v /root/unmanaged_filtro -d /root/unmanaged")
           print("En el ejemplo suponemos que dentro de la carpeta unmanaged_filtro")
           print("se encuentran las carpetas con el nombre de los dominios")
           print("por ejemplo: euromaerica conchaytoro etc.")
           print("y dentro de estas carpetas encontramos 3 archivos")
           print("ven.txt ip.txt y mac.txt")
           print("estos archivos contienen los vendor, mac e ip que queremos filtrar")
           print("la forma de escribirlos es uno en cada linea")
           print("sin comillas ni doble comillas y de la misma manera en que estan")
           print("escritos en el email original")
           print("")
           print("De la misma manera la carpeta unmanaged contiene carpetas con nombre de los dominios")
           print("En estas carpetas se guardara el resultado final como archivo csv")
           print("Estas carpetas hay que crearlas de antemano")
           print("")
           sys.exit()
       elif opt in ("-i","--ip"):
          filedeleteip = str(arg)
          #print(filedeleteip)
       elif opt in ("-m", "--mac"):
          filedeletemac = str(arg)
          #print(filedeletemac)
       elif opt in ("-v", "--vendor"):
          filedeleteven = str(arg)
          #print(filedeleteven)
       elif opt in ("-d", "--dest"):
          destino = str(arg)
          #print(filedeletemac)
       else:
          sys.exit(1)
    if len(sys.argv) < 2:
         print( 'test.py -i <pathtofolder> -m <pathtofolder> -v <pathtofolder> -d <full_destinofinal>')
         print("example: python unmanage.py -i /root/unmanaged_filtro -m /root/unmanaged_filtro -v /root/unmanaged_filtro -d /root/unmanaged")
         print("En el ejemplo suponemos que dentro de la carpeta unmanaged_filtro")
         print("se encuentran las carpetas con el nombre de los dominios")
         print("por ejemplo: euromaerica conchaytoro etc.")
         print("y dentro de estas carpetas encontramos 3 archivos")
         print("ven.txt ip.txt y mac.txt")
         print("estos archivos contienen los vendor, mac e ip que queremos filtrar")
         print("la forma de escribirlos es uno en cada linea")
         print("sin comillas ni doble comillas y de la misma manera en que estan")
         print("escritos en el email original")
         print("")
         print("De la misma manera la carpeta unmanaged contiene carpetas con nombre de los dominios")
         print("En estas carpetas se guardara el resultado final como archivo csv")
         print("Estas carpetas hay que crearlas de antemano")
         print("")

    print("{0} Empezando script unmanage".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))


    try:
        mail=imaplib.IMAP4("192.168.xx.x", ###)
    except:
        print("{0} problema al hacer la coneccion al host 1992.168.xx.x".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        sys.exit(1)


    try:
        mail.login("username","password")
    except:
        print("{0} Logon failure: unknown user name or bad password.".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        sys.exit(1)
#parsing/ Inbox conection
    mail.select('INBOX')
    result, data = mail.uid('search', None, '(UNSEEN)','(HEADER Subject "Computer Detected without Symantec Client Software")') # search and return uids instead

    mailidlist=data[0].split()
    print(data)
    if len(mailidlist)==0:
        print("{0} Terminando script unmanage. No hay nuevos email".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))

#    mailidlist=['123']

#mailidlist=['15']

    mailidlistlength=len(mailidlist)

    for i in range(mailidlistlength):
        email_uid = mailidlist[i]
        result, data = mail.uid('fetch',email_uid,'(RFC822)')
        raw_email = data[0][1] #obtengo el email raw
        email_message=email.message_from_string(raw_email) #formateo el email
        frominfo=email.utils.parseaddr(email_message['From'])[1] #obtengo el email
        domainwitha=re.findall("@[\w]+",frominfo)[0] #primer filtro
        onlydomain=domainwitha.replace('@','') #obtengo el dominio limpio
        filedeleteip= "{0}/{1}/ip.txt".format(filedeleteip,onlydomain)
        filedeletemac= "{0}/{1}/mac.txt".format(filedeletemac,onlydomain)
        filedeleteven= "{0}/{1}/ven.txt".format(filedeleteven,onlydomain)
      #  body = get_first_text_block(email_message) #obtengo el cuerpo del email
      #  decoded_body=base64.b64decode(body) #lo decodifico
        raw_email2=raw_email.replace('\r\n','')
        raw_email3=raw_email2.replace('=','')
        macip=re.findall('(width3D"10%">[0-9]+(?:\.[0-9]+){3})<\/td><td (width3D"20%">[0-9a-f]{2}(?:-[0-9a-f]{2}){5})',raw_email3) #juntos
        lengthmacip=len(macip)
        ipfix=[]
        macfix=[]
        for gg in range(lengthmacip):
            ipfix.append(macip[gg][0])
            macfix.append(macip[gg][1])
        ip_cleaned=[s.replace('width3D"10%">', '') for s in ipfix] #juntos
        mac_cleaned=[s.replace('width3D"20%">', '') for s in macfix] #juntos

        length=len(mac_cleaned) #obtengo largo de la lista
        ven_cleaned=[] #inicio lista
        url = "http://macvendors.co/api/" #url del api
        for j in range(length): #obtengo el vendor de cada mac

            mac_address=mac_cleaned[j]
            request = urllib2.Request(url+mac_address, headers={'User-Agent' : "API Browser"})
            response = urllib2.urlopen( request )
            reader = codecs.getreader("utf-8")
            obj = json.load(reader(response))
            try:
                company=obj['result']['company']
                ven_cleaned.append(company)
            except KeyError:
                print("{1} exception ocurred, no se obtuvo la informacion del mac: {0} ".format(mac_cleaned[j],str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
                ven_cleaned.append('No encontrado')

        print(onlydomain)
        try:
            f1 = open(filedeleteip, 'r')
            print("{0} abrio ip")
            filtro = f1.readlines()
            filtro_cleaned=[s.replace('\n', '') for s in filtro]
            lll=filterByIp2(ip_cleaned,mac_cleaned,ven_cleaned,filtro_cleaned)
        except IOError:
            lll=[ip_cleaned,mac_cleaned,ven_cleaned]
            print("{0} archivo de ip a borrar vacio/no encontrado o ningun ip de este archivo esta en la lista".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        try:
            f2 = open(filedeletemac, 'r')
            print("{0} abrio mac")
            filtro = f2.readlines()
            filtro_cleaned=[s.replace('\n', '') for s in filtro]
            lll1=filterByMac2(lll[0],lll[1],lll[2],filtro_cleaned)
        except IOError:
            lll1=lll
            print("{0} archivo de mac a borrar vacio/no encontrado o ningun mac de este archivo esta en la lista".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        try:
            f3 = open(filedeleteven, 'r')
            print("{0} Se abrio el archivo con el filtro de vendors".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
            filtro = f3.readlines()
            filtro_cleaned=[s.replace('\n', '') for s in filtro]
            lll2=filterByVen2(lll1[0],lll1[1],lll1[2],filtro_cleaned)
        except IOError:
            lll2=lll1
            print("{0} archivo de vendor a borrar vacio/no encontrado o ningun vendor de este archivo esta en la lista".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
        lpp=np.array(lll2).T
        df = pd.DataFrame(lpp,columns = ["IP", "MAC", "VENDOR"])
        try:
            address="{2}/{0}/{0}_{1}.csv".format(onlydomain,str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")).replace(':','.'),destino)
            df.to_csv(address, header=True,quoting=csv.QUOTE_NONNUMERIC)
            with open(address) as fp:
            # Create a text/plain message
                msg = MIMEText(fp.read())
            msg['Subject'] = "Computer Detected without Symantec Client Software: {0} ".format(onlydomain)
            msg['From'] = 'diego.orellana@akainix.com'
            msg['To'] = 'diego.orellana@akainix.com'
            s = smtplib.SMTP('godzuki.penta-sec.com')
            #godzuki.penta-sec.com
            s.sendmail('diego.orellana@akainix.com','alertas@akainix.com',msg.as_string())
            s.sendmail('diego.orellana@akainix.com','diego.orellana@akainix.com',msg.as_string())
            #s.send_message(msg)
            s.quit()

            mail.uid('store', email_uid, '+FLAGS', '(\\Seen)') #Lo marco como visto
            print("{0} Finalizando script unmanage".format(str(datetime.now().strftime("%Y-%m-%d-%H:%M:%S")).replace(':','.')))
        except IOError:
            print("{0} Directorio no creado o el path al los directorios unmanaged no es correcto".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")).replace(':','.')))
            mail.uid('store', email_uid, '-FLAGS', '(\\Seen)') #Si hay error lo dejo como no visto



if __name__ == "__main__":
   main(sys.argv[1:])
