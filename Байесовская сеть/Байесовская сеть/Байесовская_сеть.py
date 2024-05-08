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

print(df.head(3))
col_name_B = input("Enter parameter, please, only string ")

def ret_uniq_mean_col(col_name_B, df):
    b = df[col_name_B]
    sheet_val = b.unique ()   
    sheet_val = np.sort(sheet_val)
    print(sheet_val)
    return sheet_val

def P_A_B(col_name_B, df, sheet_val,col_name_A):
    b = df[col_name_B]
    a = df[col_name_A]
    df_res = pd.DataFrame()
#    df_ind = pd.DataFrame(index=['S0','S3','S2','S1'])
    for i in range(0,len(sheet_val)):
        ser1 = df.loc[b == sheet_val[i], col_name_A].value_counts(normalize=True)
        ser2 = df.loc[:,col_name_A].value_counts(normalize=True)
        fin_ser = pd.Series()
        uniq = a.unique ()
        ser3 = (ser1 * ser2)
        P_B = ser3.sum()
#        print(P_B, end='\n\n')
        for i in range(0,len(uniq)):
            res = pd.Series(ser3.iloc[i]/P_B)
            fin_ser = pd.concat([fin_ser, res], axis=0)
        df_res = pd.concat([df_res,fin_ser.to_frame().T], axis=0)
    print(ser3/P_B)
    df_res = df_res.T
    df_res.dropna(how='all')
    print(df_res)
        
sheet_val = ret_uniq_mean_col(col_name_B, df)

P_A_B(col_name_B, df, sheet_val,'Severity')