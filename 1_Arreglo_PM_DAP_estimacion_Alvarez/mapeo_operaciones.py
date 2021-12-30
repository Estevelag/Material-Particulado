import mapeo_secundarias as ms
import pandas as pd
import numpy as np
import math as math

#Funcion que hace la suma de material particulado 2.5 y 10 sobre los datos
#corregidos y por individuo
#Inputs:
#data - Los datos de material particulado corregidos
#Output:
#data - Datos resumidos por individuo

def suma_individuo(data):
    #Se filtra las columnas de interes
    data_res=data.filter(items=['Número del Individuo','Nombre común'])
    
    #Se quitan los duplicados para luego caminar sobre esta lista de datos
    data_res.drop_duplicates(subset=['Número del Individuo','Nombre común'],inplace=True)
    data_res.reset_index(inplace=True, drop=True)
    
    #Se crean las columnas donde estaran los valores de material particulado
    data_res["Material_2.5"]=np.nan
    data_res["Material_10"]=np.nan
    
    for i in range(len(data_res.index)):
        
        #Se crea una mascara booleana filtrando los datos en base a los
        #indices sin duplicados

        bool_mask = ((data.loc[:,'Nombre común'] == data_res.loc[i,'Nombre común']) & 
                   (data.loc[:,'Número del Individuo'] == data_res.loc[i,'Número del Individuo']))
        
        #Se saca el valor del material particulado

        filtro25 = data.loc[bool_mask, "Peso filtro PM 2,5 (g)"]
        filtro10 = data.loc[bool_mask, "Peso filtro PM 10 (g)"]
        pm25 = data.loc[bool_mask, "Peso de filtro con PM 2.5 (g)"]-filtro25
        pm10 = data.loc[bool_mask, "Peso de filtro con PM 10 (g)"]-filtro10

        #print(pm25)

        #Se asigna el valor en el dataframe sin duplicados
        data_res.loc[i,"Material_2.5"] = pm25.sum()
        data_res.loc[i,"Material_10"] = pm10.sum()
    
    print("--------------------------------------------")
    print("Numero de individuos",len(data_res))
      
    return data_res



#Funcion que retorna la biomasa por individuo en base a los datos de diametro
#Input:
#Data = datos originales, con el DAP
#Data = datos organizados hasta el momento por material pm 10 y pm 25
#b0 = parametro ecuacion de estimacion de biomasa
#b1 = parametro ecuacion de estimacion de biomasa
#Output:
#data_res1 = Datos de biomasa por dato de individuo
#data_res = Datos de biomasa por individuo

def biomasa_individuo(data,data_res,b0,b1,metros=True):
    data=ms.diametrocrudo(data)
    data_res=ms.mapeo_Diametro(data,data_res)
    data_res1=ms.separacion_Diametro(data_res)
    
    #Al hacer cortes de dataframes es importante resetear su indice
    #a no se que sirva para su identificacion claro
    data_res1.reset_index(inplace=True, drop=True)
    data_res1=data_res1.astype({'Diametro': 'float'}) #Se confirma el tipo de datos


    #Metodo con lambda, se divide sobre cien para pasarlo a metros
    
    if metros == True:
        data_res1['BiomasaEstimada']=data_res1['Diametro'].apply(lambda x : math.log( b0 + b1 * x/100*(math.pi)))
    elif metros == False:
        data_res1['BiomasaEstimada']=data_res1['Diametro'].apply(lambda x : math.log( b0 + b1 * x/(math.pi) ))
    data_res["BiomasaEstimada"]=np.nan
    for i in range(len(data_res.index)):
    
        #Se crea una mascara booleana filtrando los datos en base a los
        #indices sin duplicados
        bool_mask = ((data_res1.loc[:,'Nombre común'] == data_res.loc[i,'Nombre común']) & 
                    (data_res1.loc[:,'Número del Individuo'] == data_res.loc[i,'Número del Individuo']))
        
        #se saca la lista de los valores por individuo a sumar

        subset = data_res1.loc[bool_mask, "BiomasaEstimada"]


        #Se asigna el valor en el dataframe sin duplicados
        data_res.loc[i,"BiomasaEstimada"] = subset.sum()
    
    return data_res, data_res1




#Funcion que retorna la altura por individuo en base a los datos de angulos
#y distancia
#Input:
#data1 = datos originales, con angulos y distancias al arbol
#Data = datos organizados hasta el momento por material pm 10 y pm 25  y/o 
#        por biomasa
#Output:
#data_res = Datos añadidos de altura por individuo
#reporte = datos ignorados por falta de datos

def altura_Individuo(data1, data_res):

    data1, reporte = ms.altura_crudo(data1)
    data_res = ms.mapeo_Altura(data1, data_res)
    
    data_res.reset_index(inplace=True, drop=True)
    return data_res, reporte



#Funcion que agrupa datos de area, biomasa y area sobre biomasa por 
#Especie

def datos_especie(data):
    data['n_Individuos']=np.nan
    data_res=pd.DataFrame(columns = data.columns)
    data_res.drop(columns=['Número del Individuo'],inplace=True)

    for i in data.loc[:,"Nombre común"].unique():

        bool_mask = (data.loc[:,'Nombre común'] == i) 

        pm25 = data.loc[bool_mask,"Material_2.5"].mean()
        pm10 = data.loc[bool_mask,'Material_10'].mean()
        biomasaestimada = data.loc[bool_mask,'BiomasaEstimada'].mean()
        altura= data.loc[bool_mask,'Altura'].mean()
        n = len(data.loc[bool_mask])
        
        serie= pd.DataFrame([[i,pm25,pm10,biomasaestimada,altura,n]],columns=['Nombre común',
                                                                        'Material_2.5',
                                                                        'Material_10',
                                                                        'BiomasaEstimada',
                                                                        'Altura',
                                                                        'n_Individuos'])
        data_res = data_res.append(serie,ignore_index=True)
    
    return data_res

#Funcion que mapea los datos del tipo de hoja por especie al 
#dataframe resumido de datos, requiere del dataframe y del 
#diccionario con datos "Especie":"tipo_hoja"


def mapeo_tipo_hoja(data,tipohojadict):
    data.insert(2, column="Tipo_Hoja", value=np.nan)
    data["Tipo_Hoja"] = data["Nombre común"].apply(lambda x: tipohojadict.get(x))
    print("--------------------------------------------")
    print("Individuos con tipo de hoja",len(data)-len(data[data["Tipo_Hoja"].isnull()]))
    print("Individuos sin tipo de hoja",len(data[data["Tipo_Hoja"].isnull()]))
    
    
    return data
    
    
    
#Funcion para unir datos de area y biomasa limpios con datos de area
#con estos datos es que se hacen los modelos de material particulado
#por area foliar

def union_mp_dap_areas(data, data_areas):
    data["Area"]=np.nan

   # dataEsp.loc[:,'Nombre común'].unique()
    for i in range(len(data_areas.index)):
        individuo = data_areas.loc[i,'Numero']
        especie = data_areas.loc[i,'Especie']
        for x in range(len(data)):
            if data.loc[x,'Nombre común'] == especie and data.loc[x,'Número del Individuo'] == individuo :
                #print(individuo, especie,data_areas.loc[i,'Areatot(cm2)'])
                data.loc[x,"Area"] = data_areas.loc[i,'Areatot(cm2)']
                data_areas.loc[i,'Usados']=1
                break
                
    print("--------------------------------------------")
    print("Individuos con Area foliar",len(data)-len(data[data["Area"].isnull()]))
    print("Individuos sin Area foliar",len(data[data["Area"].isnull()]))
    
    return data, data_areas