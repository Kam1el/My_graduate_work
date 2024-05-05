from enum import unique
from os import name
import pandas as pd

#create DataFrame
df = pd.DataFrame({'team': ['Mavs', 'Lakers', 'Spurs', 'Cavs'],
 'name': ['Dirk', 'Kobe', 'Tim', 'Lebron'],
 'rebounds': [11, 7, 14, 7],
 'points': [26, 31, 22, 29]})

#view DataFrame
print(df)

df.insert(4, "Family", "Johns")

for row in range(0,len(df.index)):
    if df.iloc [row]['points'] == 31:
        df.at[row,"name"] = "S0"

#Тут мы опишем статистический вывод
def Unique_column(col_name, df):
    
    a = df[col_name]
    name = col_name
    print("This is a name of that column -", name)
    return a.unique()
Response = "Yes"
#Тут мы опишем ввод параметров
while (Response != "No"):
    parameter = input("Enter parameter, please, only string ")
    print(Unique_column(parameter,df))
    Response = input("Do you want to add other parameters. Only Yes/No ")


#print(df)
