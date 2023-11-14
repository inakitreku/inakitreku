import subprocess
import sys

def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


install_and_import('requests')
install_and_import('bs4')
install_and_import('pandas')
install_and_import('selenium')

import re   #para hacer regex match y extraer los valores
from bs4 import BeautifulSoup
import pandas as pd
import os   #para leer el directorio actual

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"')
driver = webdriver.Chrome(options=chrome_options)
driver.get('https://www.omie.es/')
element = WebDriverWait(driver, 20).until(
EC.element_to_be_clickable((By.XPATH, '//*[@id="block-marketresults"]/div/div[1]/a')))
element.click();
driver.get('https://www.omie.es/es/market-results/daily/daily-market/hourly-power-technologies?')
driver.get('https://www.omie.es/es/market-results/monthly/daily-market/daily-market-price?scope=monthly&year=2023&month=1')
beautifulsouplink = driver.current_url
driver.quit()

def getweb(m):
    web=beautifulsouplink
	#'https://www.omie.es/es/market-results/monthly/daily-market/daily-power?scope=monthly&year=2022&month={}'.format(m)
    page=requests.get(web)   #descargamos la página
    soup=BeautifulSoup(page.content,'html.parser')   #parseamos la página
    return soup

#definimos las energias y la fecha, y las combinamos para definir nuestras variables
energias=['CARBON','NUCLEAR','HIDRAULICA','CICLOCOMBINADO','EOLICA','SOLARTERMICA', 'SOLARFOTO','COGENERACION','IMPORTACION']
fecha=['AÑO','MES','DIA']
variables=fecha+energias

#Definimos los meses y el año
meses=['ENERO','FEBRERO','MARZO','ABRIL','MAYO','JUNIO','JULIO','AGOSTO','SEPTIEMBRE','OCTUBRE','NOVIEMBRE','DICIEMBRE']
ano=2022

#Create a dict with the variables as they are in variables
myvars={}
for l in range(0,len(variables)):
    myvars[variables[l]]=list()

DIA=[]
MES=[]
ANO=[]

#Iteramos por los meses para sacar la informacion de cada uno
for m in range(1,13):
    #Descargamos la web
    soup=getweb(m)
    
    #extraemos la etiqueda que contiene los datos del gráfico que queremos obtener. Como no tiene ID, usamos la clase
    data = soup.find(class_='charts-highchart chart')   

    #transormamos tipo etiqueta a texto
    datastring=str(data)

    #obtenemos los días de ese mes y los añadimos a la lista DIA
    days=re.search(r'categories":\[(.+)],"crosshair',datastring) #Cogemos todos los días
    mydays=re.findall(r'(?=(\d\d))',days.group(1))  #Extraemos los días uno a uno ya que son una string. Podría hacerse split por ,
    for d in range(0,len(mydays)):
        DIA.append(mydays[d])
        #Aprovechamos para ir añadiendo el mes y año a esas variables
        MES.append(meses[m-1])
        ANO.append(ano)
   
    #Añadimos ANO, MES y DIA al diccionario
    myvars['AÑO']=ANO
    myvars['MES']=MES
    myvars['DIA']=DIA
   
    #Extraemos todos los valores de las energias
    losdatos=re.findall('"name":".+?","data":\[(.+?)],"color',datastring)
   
    #Iteramos por cada energía para añadirla secuencialmente al diccionario
    for d in range(0,len(energias)):
        datis=str(','+losdatos[d]+',')
        valores=re.findall(r'\d+\.*\d*',datis) #se puede hacer con slipt
           
        for x in range(0,len(valores)):
            myvars[str(variables[d+3])].append(valores[x])      
           

df = pd.DataFrame()

for keys,values in myvars.items():
      df[keys] = values

print(df)

directorio=os.getcwd()
nombrefile="EnergiaTecnoDiaria_peninsula_2022.csv"
df.to_csv(directorio+"\\"+nombrefile, index=False)