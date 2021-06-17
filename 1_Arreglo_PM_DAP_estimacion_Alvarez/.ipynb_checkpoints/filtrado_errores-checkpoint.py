import filtrado_secundarias as fs
import pandas as pd
import numpy as np

#Esta funcion filtra posibles datos que sean cadenas y que puedan generar
#problemas en los subsequentes analisis
#Inputs:
#data - Los datos de material particulado crudos
#Output:
#data - Datos filtrados
#reporte - Registro de los datos eliminados, para tenerlos en cuenta 

def filtroInicial(data):

    #Se hace una mascara booleana de los valores que son strings
    filtro25=data.loc[:,"Peso filtro PM 2,5 (g)"].apply(lambda x: isinstance(x, str))
    filtro_con25=data.loc[:,"Peso de filtro con PM 2.5 (g)"].apply(lambda x: isinstance(x, str))
    filtro10=data.loc[:,"Peso filtro PM 10 (g)"].apply(lambda x: isinstance(x, str))
    filtro_con10=data.loc[:,"Peso de filtro con PM 10 (g)"].apply(lambda x: isinstance(x, str))

    #se filtra con las mascaras anteriores los valores que son strings
    reporte = data[filtro25 | filtro_con25 | filtro10 | filtro_con10]
    data = data[~(filtro25 | filtro_con25 | filtro10 | filtro_con10)]
    
    print("--------------------------------------------")
    print("Se eliminan",len(reporte),"datos con problemas: tienen cadenas en los pesos de material particulado")
    print("Se preservan",len(data), "datos")

    return data, reporte

#Le suma el factor de correccion a cada dato de peso de papel filtro dado la 
#condicion de ser Horno o no horno(de si fueron secados de una forma u otra)
#Inputs:
#data - Los datos de material particulado, reducidos o no
#H25 - Factor de correcion de papeles filtro "Horno" 2.5
#H10 - Factor de correcion de papeles filtro "Horno" 2.5
#NH25 - Factor de correcion de papeles filtro "Horno" 2.5
#NH10 - Factor de correcion de papeles filtro "Horno" 2.5
#Output:
#data- Datos modificados con la condicion dada

def correccion_Horno(data, H25, H10, NH25, NH10):
    data=data.astype({'Peso filtro PM 2,5 (g)': 'float', 'Peso filtro PM 10 (g)': 'float'})
    data=fs.restarfila25(data, H25, NH25)
    data=fs.restarfila10(data, H10, NH10)
    return data

#Esta funcion clasifica varios errores que nos podriamos encontrar en los datos 
#y los marca para poder filtrarlos despues
#La clasificacion se hace usando codigos numericos de la siguiente manera:
# Material PM 10 negativo = "1"
# Material PM 2.5 negativo = "2"
# Falta de datos = "3" 
#Inputs:
#data - Los datos de material particulado RESUMIDOS
#Output:
#data - Los datos de material particulado con sus errores clasificados
#       En una columna nueva "Errores"

def clasficacion_Errores(data):
    data["Errores"]=np.nan
    #Clasifica los errores en base a los codigos predefinidos
    #Hay que comprobar si el error de falta de datos es detectado efectivamente
    data.loc[data.loc[:,"Material_2.5"] < 0, "Errores"] = 2
    data.loc[data.loc[:,"Material_10"] < 0, "Errores"] = 1
    data.loc[(data.loc[:,"Material_2.5"] == 0) | (data.loc[:,"Material_2.5"] == np.nan), "Errores"] = 3
    data.loc[(data.loc[:,"Material_10"] == 0) | (data.loc[:,"Material_2.5"] == np.nan), "Errores"] = 3
    data.loc[(data.loc[:,"Material_10"] > 0) & (data.loc[:,"Material_2.5"] > 0), "Errores"] = 0
    
    print("--------------------------------------------")
    print("Se detecta la siguiente cantidad de errores:")
    print("Material PM 10 negativo =",len(data.loc[data.loc[:,"Errores"] == 1 ,:])) 
    print("Material PM 2.5 negativo =",len(data.loc[data.loc[:,"Errores"] == 2 ,:])) 
    print("Falta de datos =",len(data.loc[data.loc[:,"Errores"] == 3 ,:]))

    return data 

#Funcion que filtra los errores ya clasificados con "clasificacion_Errores"
#Devuelve los datos filtrados y los datos que fueron excluido
#Input:
#data - Los datos de material particulado con errores clasificados
#Output:
#data - Datos filtrados
#reporte - Registro de los datos eliminados, para tenerlos en cuenta, es un dataframe

def eliminacion_Errores(data):
    reporte=data.loc[data.loc[:,"Errores"] != 0,:]
    data=data.loc[data.loc[:,"Errores"] == 0,:]
    
    print("--------------------------------------------")
    print("Se eliminan",len(reporte),"individuos con problemas: los clasificados anteriormente")
    print("Se preservan",len(data), "individuos")
    
    return data,reporte


#Funcion pa checkear el numero de datos de individuo por especie que se tienen
#por tipo de dato de interes: Diametro, altura y area. 


def data_checker(data):
    especies=data["Nombre común"].unique() 
    qc_frame=pd.DataFrame(especies,columns=["Nombre_comun"])
    qc_frame["n_Individuos"]=np.nan
    qc_frame["Datos_diametro"]=np.nan
    qc_frame["Datos_altura"]=np.nan
    qc_frame["Datos_area"]=np.nan

    for especie in especies:
        
        to_count=data.loc[data.loc[:,"Nombre común"]==especie,:]
        
        conteo_individuos=len(to_count)
        conteo_diametro=len(to_count.dropna(subset=['Diametro']))
        conteo_altura=len(to_count.dropna(subset=['Altura']))
        conteo_area=len(to_count.dropna(subset=['Area']))
        
        qc_frame.loc[qc_frame.loc[:,"Nombre_comun"]==especie,"n_Individuos"]=conteo_individuos
        qc_frame.loc[qc_frame.loc[:,"Nombre_comun"]==especie,"Datos_diametro"]=conteo_diametro
        qc_frame.loc[qc_frame.loc[:,"Nombre_comun"]==especie,"Datos_altura"]=conteo_altura
        qc_frame.loc[qc_frame.loc[:,"Nombre_comun"]==especie,"Datos_area"]=conteo_area
       
        
    print("--------------------------------------------")
    print("Se queda con ",len(especies),"especies")
    print("Dataframe especies con numeros variables de datos(deberia")
    print("haber el mismo numero de datos por individuo por especie)")
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        display(qc_frame[qc_frame.iloc[:,1:].var(axis=1) > 0])
    
    return qc_frame