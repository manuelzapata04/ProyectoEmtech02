# -*- coding: utf-8 -*-
"""
Created on Fri Sep 25 21:16:09 2020

@author: zaju9001
"""
#coloca la ruta de trabajo
import os
os.chdir(r'C:\Users\zaju9001\Documents\Programas Python')

#Se usa la paquetería pandas para realizar los análisis
import pandas as pd

#Lee el archivo csv donde está la base de datos a analizar
base_de_datos  = pd.read_csv('synergy_logistics_database.csv')

##### En esta primera sección se obtienen los análisis solicitados por la compañía #####

#crea una nueva variable para conocer la ruta (origen-destino)
base_de_datos['route'] = base_de_datos['origin'] + '_' + base_de_datos['destination']

#crea una tabla que agrupa el total de exportaciones por ruta
exportaciones_rutas = base_de_datos[base_de_datos.direction == 'Exports'].groupby(
'route').agg(total = ('total_value', 'sum'), count = ('route', 'count')).sort_values(
    'total', ascending=False)

#crea una tabla que agrupa el total de importaciones por ruta
importaciones_ruta = base_de_datos[base_de_datos.direction == 'Imports'].groupby(
'route').agg(total = ('total_value', 'sum'), count = ('route', 'count')).sort_values(
    'total', ascending=False)

#crea una tabla que agrupa el total de exportaciones e importaciones por medio de transporte
transportes = base_de_datos.groupby('transport_mode').agg(
    total = ('total_value', 'sum'), count = ('transport_mode', 'count')).sort_values(
    'total', ascending=False)

#crea una tabla que agrupa el total de exportaciones por país
exportaciones_paises = base_de_datos[base_de_datos.direction == 'Exports'].groupby(
'origin').agg(total = ('total_value', 'sum'), count = ('route', 'count')).sort_values(
    'total', ascending=False)

#crea una tabla que agrupa el total de importaciones por país
importaciones_paises = base_de_datos[base_de_datos.direction == 'Imports'].groupby(
'destination').agg(total = ('total_value', 'sum'), count = ('route', 'count')).sort_values(
    'total', ascending=False)
    
##### En esta sección se repiten los mismos análisis, pero ahora también se considera el año, para saber si con el paso del tiempo los resultados son iguales#####


#crea una tabla que agrupa el total de exportaciones por ruta y año
exportaciones_rutas_año = base_de_datos[base_de_datos.direction == 'Exports'].pivot_table(
    index = 'route', columns = 'year', values = 'total_value', aggfunc = 'sum').sort_values(
    2020, ascending=False).fillna(0)
    
#crea una tabla que agrupa el total de importaciones por ruta y año
importaciones_ruta_año = base_de_datos[base_de_datos.direction == 'Imports'].pivot_table(
    index = 'route', columns = 'year', values = 'total_value', aggfunc = 'sum').sort_values(
    2020, ascending=False).fillna(0)

#crea una tabla que agrupa el total de exportaciones e importaciones por medio de transporte y año
transportes_año = base_de_datos.pivot_table(
    index = 'transport_mode', columns = 'year',values = 'total_value', aggfunc = 'sum' ).sort_values(
    2020, ascending=False).fillna(0)

#crea una tabla que agrupa el total de exportaciones por país
exportaciones_paises_año = base_de_datos[base_de_datos.direction == 'Exports'].pivot_table(
    index = 'origin', columns = 'year', values = 'total_value', aggfunc = 'sum').sort_values(
    2020, ascending=False).fillna(0)

#crea una tabla que agrupa el total de importaciones por país
importaciones_paises_año = base_de_datos[base_de_datos.direction == 'Imports'].pivot_table(
    index = 'destination', columns = 'year', values = 'total_value', aggfunc = 'sum').sort_values(
    2020, ascending=False).fillna(0)
        

"""
Con base en las tablas por año, se nota que algunos países dejan de importar y otros de exportar en el 2020
lo que afecta también a las rutas en las que participan. De igual forma algunos paises comienzan a tener movimientos.
Algunos otros no tuvieron movimientos algunos años.

Por todo lo anterior y con el objeto de enfocarse en las rutas más rentables actualmente y 
hacer un análisis más objetivo y homogéneo, se decide analizar la base de datos sólo con la 
información del 2020.

"""


#crea tabla con el total de importaciones/exportaciones por medio de transporte del 2020
transportes_2020 = base_de_datos[base_de_datos.year == 2020].groupby('transport_mode').agg(
    total = ('total_value', 'sum'), count = ('transport_mode', 'count')).sort_values(
    'total', ascending=False)
        
transportes_2020['porcentaje']  = (transportes_2020['total'] / 
                  transportes_2020['total'].sum()) * 100

#se observa que sea, rail & air hacen más del 90% del total, con lo que pareciera que
#road no es rentable

#Crea una tabla con info del 2020
base = base_de_datos[base_de_datos.year == 2020]

#crea tablas de la nueva base para importaciones y exportaciones por ruta y medio de transporte
base_exp = base[base.direction == 'Exports'].groupby(['route','transport_mode']).agg(
    total_exp = ('total_value', 'sum'), count_exp = ('route', 'count'))
        
base_imp = base[base.direction == 'Imports'].groupby(['route','transport_mode']).agg(
    total_imp = ('total_value', 'sum'), count_imp = ('route', 'count'))

#cruza las dos bases anteriores
base_fin = base_exp.merge(base_imp, how = 'outer', on = ['route', 'transport_mode']).fillna(0)

#crea una nueva columna con el total de import. y exp. por ruta
base_fin['total'] = base_fin.total_exp + base_fin.total_imp
base_fin['count'] = base_fin.count_exp + base_fin.count_imp

#ordena por total
base_fin = base_fin.sort_values('total', ascending=False)

#calcula procentajes del total y su acumulado, crea un listado para saber la posición de la ruta
base_fin['porc_total'] = (base_fin['total'] /  base_fin['total'].sum()) * 100
base_fin['porc_acumulado'] = base_fin['porc_total'].cumsum()
base_fin['pos_total'] = range(1,75)

'''
Hasta este punto se recomienda enfocar la estrtegia del 2021 en las primeras 28 rutas
de la tabla base_fin, pues aportan más de 1% al total de impor/export y en conjunto logran el 88%
del total.

A continuación, se busca profundizar más el análisis, con datos que no provienen de la base
proporcionada por el cliente.
Se harán estimaciones del costo de cada ruta, para ello se utiliza la base Country Centroids de la
Universidad de Harvard (contiene las coordenadas del punto central de cada país), así como la paquetería
haversine  que calcula la distancia entre dos puntos del planeta tierra (tomando en cuenta la esfericidad)
y finalmente las estimaciones realizadas por la universidad de Noruega sobre los costos de transporte.
La documentación de la información extra se encuentra en los siguientes links:
    1: Country Centroids by Harvard University:
        https://worldmap.harvard.edu/data/geonode:country_centroids_az8
    2: Haversine Distance:
        https://towardsdatascience.com/calculating-distance-between-two-geolocations-in-python-26ad3afe287b
    3: The relationship between travel distance and fares, time costs and generalized costs in passenger transport by Nord University:
        https://www.researchgate.net/publication/241164152_The_relationship_between_travel_distance_and_fares_time_costs_and_generalized_costs_in_passenger_transport

Observación: Las distancias son medidas del punto medio de un país a otro, quizás no es la mejor 
aproximación, pero dado que ninguna ruta es el línea recta, parece funcionar adecuadamente para estimar los costos
'''

#Lee el archivo csv donde está la base Country Centroids 
#NOTA: La base se limpió en otro programa
country_cent = pd.read_csv('country_centroids_az8.csv')

#crea tablas con los origenes y destinos del 2020 y sus coordenadas
origenes = pd.DataFrame(base_de_datos[base_de_datos.year == 2020]['origin'].drop_duplicates())
origenes = origenes.merge(country_cent, how = 'left', left_on = 'origin', right_on = 'sovereignt')
origenes = origenes[['origin', 'Latitude', 'Longitude']].rename(columns={'Latitude': 'or_lat', 'Longitude': 'or_lon'})

destinos = pd.DataFrame(base_de_datos[base_de_datos.year == 2020]['destination'].drop_duplicates())
destinos = destinos.merge(country_cent, how = 'left', left_on = 'destination', right_on = 'sovereignt')
destinos = destinos[['destination', 'Latitude', 'Longitude']].rename(columns={'Latitude': 'dest_lat', 'Longitude': 'dest_lon'})

#crea una tabla con las rutas del 2020 y sus coordenadas
rutas = base_de_datos[base_de_datos.year == 2020][['route', 'transport_mode', 'origin', 'destination']].drop_duplicates()
rutas = rutas.merge(origenes, how = 'left', on = 'origin').merge(
    destinos, how = 'left', on = 'destination')


#calcula la distancia en metros de cada ruta
import haversine as hs
#rutas['distancia'] 

distancias = []
for ii in range(0, len(rutas)):
    loc1=(rutas.or_lat[ii],rutas.or_lon[ii])
    loc2=(rutas.dest_lat[ii],rutas.dest_lon[ii])
    dist = round(hs.haversine(loc1,loc2), 2)
    distancias.append(dist)
    
rutas['distancias'] = distancias

rutas_dist = rutas[['route', 'transport_mode', 'distancias']]

#cruza a base_fin las distancias
base_fin = base_fin.merge(rutas_dist, how = 'left', on = ['route', 'transport_mode'])

'''
Con base en el artículo de la Universidad de Noruega, el costo de cada transporte es:
    Air = 269 + 5.42D
    Ferry = 15 + 1.12D
    Rail = 153 + 0.91D
    Bus = 22 + 1.15D
Donde D es la distancia en Km

Con esta información se calcula el costo de cada ruta, considerando el medio de transporte.
Observación: el costo de las fórmulas arriba resulta en NOKs (coronas noruegas), 
vamos a multiplicarlo por 0.10 que es el tipo de cambio de NOKs - dolares Américanos,
el 27 de septiembre del 2020 según google
'''

def cost(row):
    if row['transport_mode'] == 'Air':
        val = 269 + 5.42 * row['distancias']
    elif row['transport_mode'] == 'Rail':
        val = 153 + 0.91*row['distancias']
    elif row['transport_mode'] == 'Sea' :
        val = 15 + 1.12*row['distancias']
    else : 
        val = 22 + 1.15*row['distancias']
    return val*0.10
        
base_fin['costo_unitario'] = base_fin.apply(cost, axis=1)
base_fin['costo_total'] = base_fin['count'] * base_fin['costo_unitario']


'''
Dado que se desconocen las unidades de total_value, voy a asumir que son dólares,
de tal forma que al dividir total_value / costo_total tengamos una métrica que nos indique cuántos dólares
se generan en importaciones o exportaciones por cada dólar gastado en transporte. A esto lo llamaré
rentabilidad
'''

base_fin['rentabilidad'] = base_fin['total'] / base_fin['costo_total']

#Ahora vamos a ordenar la base de la mejor rentabilidad a la peor y crear un listado para conocer
#la posición de cada ruta por rentabilidad y compararla con su posición por total_value
base_fin = base_fin.sort_values('rentabilidad', ascending=False)
base_fin['pos_rent'] = range(1,75)


#finalmente, vamos a calcular la ganancia estimada como total - costo_total y calcular los porcentajes 
#(simples y acumulados) de cada ruta. Así como el ranking de rutas por ganancias

base_fin['ganancia'] = base_fin['total'] - base_fin['costo_total']
base_fin = base_fin.sort_values('ganancia', ascending=False)
base_fin['pos_gana'] = range(1,75)
base_fin['porc_gana'] = (base_fin['ganancia'] /  base_fin['ganancia'].sum()) * 100
base_fin['porc_acum_gana'] = base_fin['porc_gana'].cumsum()


#finalmente, se exporta el archivo a excel para su graficación e interpretación final
base_fin.to_excel('base_fin.xlsx', index = False)