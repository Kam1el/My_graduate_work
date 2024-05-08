
from locale import normalize
import numpy as np
import pandas as pd
from IPython.display import display

df = pd.read_excel(r"C:\Users\PC\Documents\Diplom\Bayes_start_table_1.xlsx", engine='openpyxl', header = 0)
#Оставил только 10000 записей, чтобы работало быстрее
df = df[df.catv.index < 10000]
df.reset_index(drop=True, inplace=True)
#Убираем ограничение по количеству выводимых столбцов, строк. Удалили некоторые строки, необходимо сбросить индексы строк
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
#Добавил столбец, куда пойдут данные по тяжести последствий
df.insert(14,"Severity", 0)
#Приводим столбцы к удобному для обработки виду
df["grav"] = df["grav"].astype('int64')
df["Severity"] = df["Severity"].astype('object')
df["Num_Acc"] = df["Num_Acc"].astype('string')
#Необходимо удалить данные, не вписывающиеся в подготовленный список сценариев
values1 = [0,1,2,33,10,13,14,15,99,37,3,35,36,39,40]
values2 = [1,2,3,4]
values3 = [-1]
df = df[(df.catv.isin(values1) == True)]
df = df[(df.grav.isin(values2) == True)]
df = df[(df.lum.isin(values3) != True)]
#Удалили некоторые строки, необходимо сбросить индексы строк
df.reset_index(drop=True, inplace=True)

#Распределяем степень тяжести происшествия по каждой аварии с каждой точки зрения 
#(у одной аварии, т.е. одного ID аварии может быть 2 и более записей, т.к. авария рассматривается с точки зрения всех участников аварии)
for row in range(0,len(df.index)):
    if df.iloc[row]['grav'] == 1:
        df.at[row,"Severity"] = "S0"
    elif df.iloc[row]['grav'] == 2:
        df.at[row,"Severity"] = "S1"
    elif df.iloc[row]['grav'] == 3:
        df.at[row,"Severity"] = "S2"
    elif df.iloc[row]['grav'] == 4:
        df.at[row,"Severity"] = "S3"

#Столбец с информацией по смертности более не нужен, удаляем
df.drop('grav', axis= 1 , inplace= True)

def P_B(col_name, df, par_val,col_name_ask):
    a = df[col_name]
    b = df[col_name_ask]
    ser1 = df.loc[a == par_val, 'Severity'].value_counts(normalize=True)
    ser2 = df.loc[:,'Severity'].value_counts(normalize=True)
    fin_ser = pd.Series()
    print(ser1)
    print(ser2)
    uniq = b.unique ()
    print(a.unique ())
    print(len(uniq))
    ser3 = (ser1 * ser2)
    print(ser3)
    P_B = ser3.sum()
    print(P_B, end='\n\n')
    for i in range(0,len(uniq)):
        print(ser3.iloc[i]/P_B)
        
        
P_B('lum', df, 5,'Severity')