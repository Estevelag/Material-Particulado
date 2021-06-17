import pandas as pd

#Esta funcion adiciona los factores de conversion correspondiente a los datos
#de peso de los filtros 2.5, los nombres de las columnas se conocen de antemano

#Input: 
#data - base de datos con los pesos de los filtros
#H25 - Factor de correcion de papeles filtro "Horno" 2.5
#NH25 - Factor de correcion de papeles filtro "No Horno" 2.5

#Output:
#data- Datos modificados con la condicion dada

def restarfila25(data,H25,NH25):
    #print(data.loc[data.loc[:,"No_horno_2.5"] == 1,"Peso filtro PM 2,5 (g)"])
    data.loc[data.loc[:,"No_horno_2.5"] == 1,"Peso filtro PM 2,5 (g)"] = data.loc[data.loc[:,"No_horno_2.5"] == 1,"Peso filtro PM 2,5 (g)"]+NH25
    data.loc[data.loc[:,"No_horno_2.5"] == 0,"Peso filtro PM 2,5 (g)"] = data.loc[data.loc[:,"No_horno_2.5"] == 0,"Peso filtro PM 2,5 (g)"]+H25
    return data

#Esta funcion adiciona los factores de conversion correspondiente a los datos
#de peso de los filtros 10, los nombres de las columnas se conocen de antemano

#Input: 
#data - base de datos con los pesos de los filtros
#H10 - Factor de correcion de papeles filtro "Horno" 10
#NH10 - Factor de correcion de papeles filtro "No Horno" 10

#Output:
#data- Datos modificados con la condicion dada

def restarfila10(data,H10,NH10):
    data.loc[data.loc[:,"No_horno_10"] == 1,"Peso filtro PM 10 (g)"] = data.loc[data.loc[:,"No_horno_10"] == 1,"Peso filtro PM 10 (g)"]+NH10
    data.loc[data.loc[:,"No_horno_10"] == 0,"Peso filtro PM 10 (g)"] = data.loc[data.loc[:,"No_horno_10"] == 0,"Peso filtro PM 10 (g)"]+H10
    return data