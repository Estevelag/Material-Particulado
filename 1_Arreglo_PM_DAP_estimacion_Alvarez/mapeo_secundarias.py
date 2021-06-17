import math
import pandas as pd
import numpy as np


#Funcion para separar datos de diametro por individio, sin separar
#los valores varios que hay en una sola casilla, eso se hace despues
#Input:
#data - Datos crudos sobre el diametro
#Output:
#data - Datos crudos con su asignacion unica  
def diametrocrudo(data):
    data.drop_duplicates(subset=['Número del Individuo','Nombre común','Diametro Nuevo'],inplace=True)
    data = data[data.loc[:,"Diametro Nuevo"]!= np.nan]
    data.reset_index(inplace=True)
    
    print("--------------------------------------------")
    print("Datos con diametro",len(data), "datos")
    
    return data

#Funcion para mapear datos de diametro por individuo a datos por individuo 
#en una base resumida "data_res"
#Input:
#data - datos donde estan los diametros por individuo 
#data_res - datos donde se mapearan los diametros por individuo, esto si 
#            es asi porque en esta base ya estan los datos de materian particulado
#            mapeados correctamente
#Output:
#data_res - datos de diametro ya mapeados 

def mapeo_Diametro(data,data_res):
    data_res["Diametro"]=np.nan
    data_res.reset_index(inplace=True,drop=True)
    for i in range(len(data_res.index)):
        
        bool_mask = ((data.loc[:,'Nombre común'] == data_res.loc[i,'Nombre común']) & 
                   (data.loc[:,'Número del Individuo'] == data_res.loc[i,'Número del Individuo']))



        
        data_no_nans=data[bool_mask].dropna(subset=['Diametro Nuevo'])
        #print("START--:\n",data.loc[bool_mask,'Nombre común'],"\n---\n",
        #data.loc[bool_mask,'Número del Individuo'],"\n\n",
        #data.loc[bool_mask,'Diametro Nuevo'],"\n\n",
        #len(data_no_nans),"\n-----------\n")

        #El indice de la fila en la base de datos "data" es unico y tiene indice
        #0
        if len(data_no_nans) == 1:
            index_Data=data_no_nans.index[0]
        elif len(data_no_nans) == 0:
            index_Data = data[bool_mask].index[0]

        data_res.loc[i,"Diametro"] = data.loc[index_Data,"Diametro Nuevo"]
    
    print("--------------------------------------------")
    print("Individuos con diametro:",len(data_res)-len(data_res[data_res["Diametro"].isnull()]))
    print("Individuos sin diametro:",len(data_res[data_res["Diametro"].isnull()]))

    return data_res

#Fucion que separa los diametros de las casillas donde hay mas de un diametro
#para el mismo individuo
#Input:
#data - datos mapeados pero no separados de diametro
#Output:
#data_res - datos de diametro separados por individuo, listos para aplicar un modelo
#de biomasa sobre ellos

def separacion_Diametro(data):
    #Se crea un dataframe copia pero sin datos
    data_res=pd.DataFrame(columns = data.columns)

    #La columna de diametros se trata como cadena
    data=data.astype({'Diametro': 'str'})

    for i in range(len(data.index)):
        #Se hacen las divisiones para casillas con mas de 1 diametro o no
        #separadas o con un slash o con un "-"
        #print(data.loc[i,"Diametro"],data.loc[i,"Nombre común"],data.loc[i,"Número del Individuo"])
        slashsplit = data.loc[i,"Diametro"].split("/")
        lineasplit = data.loc[i,"Diametro"].split("-")
        slashcount = len(slashsplit)
        lineacount = len(lineasplit)

        if slashcount > 1:

            for x in slashsplit:
                data_res = data_res.append(data.loc[i,:],ignore_index=True)#Se adiciona una fila al dataframe
                
                discrete = x.replace(",",".")
                discrete = floatconversion(discrete)
                data_res.loc[data_res.index[-1],"Diametro"] = discrete
                #print(data_res.loc[data_res.index[-1],"Diametro"], " y ", x)

        elif lineacount > 1:

            for x in lineasplit:
                data_res = data_res.append(data.loc[i,:],ignore_index=True)
                
                discrete = x.replace(",",".")
                discrete = floatconversion(discrete)
                data_res.loc[data_res.index[-1],"Diametro"] = discrete
                #print(data_res.loc[data_res.index[-1],"Diametro"], " y ", x)  
                   
        else:
            data_res = data_res.append(data.loc[i,:],ignore_index=True)
            
            discrete = data.loc[i,"Diametro"].replace(",",".")
            discrete = floatconversion(discrete)
            data_res.loc[data_res.index[-1],"Diametro"] = discrete
            #print(data_res.loc[data_res.index[-1],"Diametro"], "nada")

    return data_res

#Esta funcion ejecuta el modelo de biomasa por dato, la funcion no es muy rara
#Recordar que su R2 era de 0.4 mas o menos
#Inputs:
#x - El DAP(en centimetros), dentro de la funcion se corrige a metros dividiendo
#   entre 100 en la formula
#b0 - parametro de modelo
#b1 - parametro de modelo
#Output:
#biomas - biomasa estimada por el modelo

def modeloBiomasa(x,b0,b1):
    biomas=math.log( b0 + b1 * (x/100))
    return biomas

#Funcion para convertir strings complicadas a float
#Input:
#string - string a convertir
#Output:
#conver - string convertida a float

def floatconversion(string):
    conver=''
    for i in string:
        if string =='nan':
            break
        if i == ' ':
            pass
        elif i == '.' or type(int(i)) == int:
            conver += i
    if len(conver) == 0 or conver == '':
        conver = 'nan'
    conver=float(conver)
    return conver

#Funcion para separar datos de angulo y distancia por individio y luego hace
#la operacion correspondiente para sacar la altura
#tambien entraga un reporte de los datos malos

#Input:
#data - Datos crudos sobre angulo y distancia
#Output:
#data - Datos crudos con su asignacion unica  

def altura_crudo(data):
    data.drop_duplicates(subset=['Número del Individuo','Nombre común','Angulo inferior.1',
                                 'Angulo superior.1','Distancia.1'],inplace=True)
    

    #data = data[data.loc[:,"Angulo inferior.1"]!= np.nan]
    data = data.dropna(subset=['Angulo inferior.1'])
    data.reset_index(inplace=True)
    
    #reporte=data[data.loc[:,"Distancia.1"]== np.nan]
    #data = data[data.loc[:,"Distancia.1"]!= np.nan]
    data = data.dropna(subset=['Distancia.1'])
    #data = data.loc[~data.loc[:,"Distancia.1"].isnull(),:]
    reporte=data.copy()
    print("--------------------------------------------")
    print("Datos con altura calculable:",len(data))
    
    #Aqui se hacen las operaciones
    distancia=data.loc[:,"Distancia.1"].astype('float')
    arriba=data.loc[:,"Angulo superior.1"].apply(lambda x: x*math.pi/180).apply(math.tan)
    abajo=data.loc[:,"Angulo inferior.1"].apply(lambda x: x*math.pi/180).apply(math.tan)
    altura=distancia*(arriba+abajo)
    data['Altura']=altura

    return data, reporte

#Funcion para mapear datos de altura por individuo a datos por individuo 
#en una base resumida "data_res"
#Input:
#data - datos donde esta la altura por individuo 
#data_res - datos donde se mapeara la altura por individuo, esto si 
#            es asi porque en esta base ya estan los datos de materian particulado
#            mapeados correctamente
#Output:
#data_res - datos de altura ya mapeados 

def mapeo_Altura(data,data_res):
    data_res["Altura"]=np.nan
    data_res.reset_index(inplace=True,drop=True)
    for i in range(len(data_res.index)):
        
        bool_mask = ((data.loc[:,'Nombre común'] == data_res.loc[i,'Nombre común']) & 
                   (data.loc[:,'Número del Individuo'] == data_res.loc[i,'Número del Individuo']))

        data_no_nans=data[bool_mask].dropna(subset=['Altura'])

        #El indice de la fila en la base de datos "data" es unico y tiene indice
        #0
        if len(data_no_nans) == 1:
            index_Data=data_no_nans.index[0]
            data_res.loc[i,"Altura"] = data.loc[index_Data,"Altura"]
        elif len(data_no_nans) == 0:
            try:
                index_Data = data[bool_mask].index[0]
                data_res.loc[i,"Altura"] = data.loc[index_Data,"Altura"]
            except IndexError:
                pass
       
    
        
    print("--------------------------------------------")
    print("Individuos con altura",len(data_res)-len(data_res[data_res["Altura"].isnull()]))
    print("Individuos sin altura",len(data_res[data_res["Altura"].isnull()]))
    return data_res