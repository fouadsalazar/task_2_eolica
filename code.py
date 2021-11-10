import pandas as pd
import numpy as np
import datetime
from datetime import datetime
import plotly.graph_objects as go
import math
import statistics

def leer(año):
    datos = pd.read_csv('{}.txt'.format(año), sep=",")
    
    # Se arregla el formato de las fechas para poder trabajarlo
    datos["DATE (MM/DD/YYYY)"]= pd.to_datetime(datos["DATE (MM/DD/YYYY)"])
    datos['Año'] = datos["DATE (MM/DD/YYYY)"].dt.year
    datos['Mes'] = datos["DATE (MM/DD/YYYY)"].dt.month
    datos['Dia'] = datos["DATE (MM/DD/YYYY)"].dt.day
    
    # Se arregla el formato de las horas 
    hora=[]
    for i in range(len(datos)):
        hora.append(datetime.strptime(datos["MST"][i],"%H:%M"))
    datos['Hora'] = hora
    datos['Hora'] = datos["Hora"].dt.hour
    
    return(datos)

    # Limpieza de datos
def corregir_datos(datos):
    columna=["Station Pressure [mBar]","Avg Wind Speed @ 2m [m/s]","Avg Wind Speed @ 5m [m/s]",
             "Avg Wind Speed @ 10m [m/s]","Avg Wind Speed @ 20m [m/s]","Avg Wind Speed @ 50m [m/s]",
             "Avg Wind Speed @ 80m [m/s]"]

    datos.fillna(0,inplace=True)
    
    for i in range(len(datos)):
        for j in range(len(columna)):
            if i > 0  and i < (len(datos)-1):
                if datos[columna[j]][i] < 0:
                    datos[columna[j]][i] = (datos[columna[j]][i-1] + datos[columna[j]][i+1])/2
    return (datos)

    # Obtener coeficiente de Hellman
def datos_x_mes(datos,año):
    datos_por_mes=datos.groupby(["Mes"],as_index=False).mean()
    v_v=[2,5,20,50,80]
    z = np.log(v_v)
    z0 = []
    vT = []
    alpha=[]
    for i in range (0,12):
        v_10 =  [datos_por_mes.iloc[i]['Avg Wind Speed @ 10m [m/s]']]
        v_w =[datos_por_mes.iloc[i]['Avg Wind Speed @ 2m [m/s]'],datos_por_mes.iloc[i]['Avg Wind Speed @ 5m [m/s]'],
              datos_por_mes.iloc[i]['Avg Wind Speed @ 20m [m/s]'],datos_por_mes.iloc[i]['Avg Wind Speed @ 50m [m/s]'],
              datos_por_mes.iloc[i]['Avg Wind Speed @ 80m [m/s]']]
        x = np.log(v_w)
        ajuste = np.polyfit(z,x,1)
        alpha.append(ajuste[0])
    return(alpha)
    
Mes = [1,2,3,4,5,6,7,8,9,10,11,12]
Mes1 = ["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
fig1 = go.Figure()
fig2 = go.Figure()
media_z0 = []
media_vT = []
prueba = pd.DataFrame(index=Mes1)

#Altura de rugosidad y velocidad de fricción
for año in [2017,2018,2019]:
    datos = corregir_datos(leer(año))
    variables = datos_x_mes(datos,año)
    fig1.add_trace(go.Scatter(name="z0 Año {}".format(año),x=Mes, y=variables[0]))
    fig1.update_layout(title = 'Valores mensuales de Altura de Rugosidad para los años 2017,2018 y 2019',
                       title_x=0.5, xaxis_title='Mes',xaxis = dict(tick0 = 1,dtick = 1),yaxis_title='z0 [m]')
    fig1.update_layout(yaxis_range=[0,0.05])
    
    fig2.add_trace(go.Scatter(name="Vt Año {}".format(año),x=Mes, y=variables[1]))
    fig2.update_layout(title = 'Valores mensuales de Velocidad de Fricción para los años 2017,2018 y 2019',
                       title_x=0.5, xaxis_title='Mes',xaxis = dict(tick0 = 1,dtick = 1),yaxis_title='Vt [m/s]')
    fig2.update_layout(yaxis_range=[0,0.35])
    media_z0.append(statistics.mean(variables[0]))
    media_vT.append(statistics.mean(variables[1]))
    prueba["z_0 [m] {}".format(año)] = np.transpose(variables)[:,0]
    prueba["v_T [m/s] {}".format(año)] = np.transpose(variables)[:,1]
fig1.show()
fig2.show()


fig1 = go.Figure()
fig2 = go.Figure()
media_z0 = []
media_vT = []
alpha=[]
prueba1 = pd.DataFrame(index=Mes1)

# Obtener coeficiente de Hellman
for año in [2017,2018,2019]:
    datos = corregir_datos(leer(año))
    variables = datos_x_mes(datos,año)
    fig1.add_trace(go.Scatter(name="Alpha del año {}".format(año),x=Mes, y=variables))
    fig1.update_layout(title = 'Valores del Exponente de Hellman Mensual',
                       title_x=0.5, xaxis_title='Mes',xaxis = dict(tick0 = 1,dtick = 1),yaxis_title='Alpha')
    fig1.update_layout(yaxis_range=[0,0.20])
    prueba1["Alpha {}".format(año)] = np.transpose(variables)

print(prueba1)    
fig1.show() 
