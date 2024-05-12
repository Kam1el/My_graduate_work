from enum import unique
import pandas as pd
import openpyxl
import numpy as np
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.utils import get_example_model
from pgmpy.inference import VariableElimination
from pgmpy.metrics import correlation_score, log_likelihood_score, BayesianModelProbability
import time

start = time.perf_counter()
#Необходимые нам переменные, чтобы всё заработало
df = pd.read_excel(r"C:\Users\PC\Documents\Diplom\Bayes_start_table_1.xlsx", engine='openpyxl', header = 0)
test_date = {
    'abcd': ['S0', 'S1','S2', 'S3'],
    'proportion': [0.0,0.0,0.0,0.0]
    }
test_date1 = {
    'Num_Acc': [0],
    'catv':[0],
    'manv':[0],
    'lum':[0],
    'int':[0],
    'atm':[0],
    'col':[0],
    'circ':[0],
    'prof':[0],
    'surf':[0],
    'infra':[0],
    'situ':[0],
    'catr':[0],
    'Severity':[0],
    }
#Оставил только 10000 записей, чтобы работало быстрее
df = df[df.catv.index < 50000]
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
df = df[(df.catv.isin(values1) == True)]
df = df[(df.grav.isin(values2) == True)]
#Удалили некоторые строки, необходимо сбросить индексы строк
df.reset_index(drop=True, inplace=True)

df.to_pickle (" my_data.pkl ")
df = pd.read_pickle (" my_data.pkl ")

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

#Фильтруем полученную по параметрам пользователя базу сценариев
def check_scen(df, sheet_val, sheet_par):
    for i in range(0,len(sheet_val)):
        a = df[sheet_par[i]]
        df = df.loc[a == sheet_val[i]]
    return df

#Тут мы опишем статистический вывод и сценарии
def stat_for_param(col_name, df, par_val, df_scenario, sheet_val, sheet_par):
    a = df[col_name]
    df2 = df.loc[a == par_val]
    df_scenario = pd.concat([df_scenario, df2], axis=0)
    df_scenario = df_scenario[(df_scenario.int.isin([0]) != True)]
    df_scenario = df_scenario.drop_duplicates()
    df_scenario = check_scen(df_scenario, sheet_val, sheet_par)
    df_scenario.reset_index(drop=True, inplace=True)
    df1 = df_scenario.loc[:,'Severity'].value_counts(normalize=True)
    df1 = df1.to_frame()
    df1.reset_index(inplace=True)
    return df1, df_scenario

#Тут мы опишем вывод сценариев и тяжести
def inp_scen_sev(df, variab = pd.DataFrame(test_date), scen_df = pd.DataFrame(test_date1), Response = "Yes", sheet_par = [], sheet_val = [], par_count = 0.0):
    #Собираем список параметров и значений для данных параметров
    while (Response != "No"):
        par_count += 1.0
        parameter = input("Enter parameter, please, only string ")
        sheet_par.append(parameter)
        print(sheet_par)
        param_val = int(input("Enter parameter value, please, only int "))
        sheet_val.append(param_val)
        print(sheet_val)
        #Обращаемся к функции, которая нам выдаёт список сценариев, среднюю степень тяжести
        df_fr_stat, scen_df = stat_for_param(parameter,df, param_val,scen_df, sheet_val, sheet_par)
        df_fr_stat['proportion'] = df_fr_stat['proportion'] + variab['proportion']
        variab = df_fr_stat
        #Добавить параметры или нет
        Response = input("Do you want to add other parameters. Only Yes/No ")
    #Если сценариев под введённые параметры нет
    if len(scen_df) == 0:
        #Спрашиваем, запустить ли ещё раз программу
        ti = input('No such scenarios, try again? Only Yes/No ', )
        if ti == 'Yes':
            sheet_par = []
            sheet_val = []
            inp_scen_sev(df, variab = pd.DataFrame(test_date), scen_df = pd.DataFrame(test_date1), Response = "Yes", sheet_par = [], sheet_val = [], par_count = 0.0)
        else:
            return 0
    #Если сценарии таки есть
    else:                       
        variab['proportion'] = variab['proportion']/par_count
        df_fr_stat['proportion'] = variab['proportion'].transform(lambda x: '{:,.2%}'.format(x))
        #Записываем данные в файл
        with pd.ExcelWriter(r'C:\\Users\\PC\\Documents\\Diplom\\Scenarios.xlsx') as writer:
            scen_df.to_excel (writer,index= False, sheet_name='Scen')
            df_fr_stat.to_excel (writer,index= False, sheet_name='Sev')
        return sheet_par, sheet_val


sheet_par, sheet_val =  inp_scen_sev(df, variab = pd.DataFrame(test_date), scen_df = pd.DataFrame(test_date1), Response = "Yes", sheet_par = [], sheet_val = [], par_count = 0.0)
print(sheet_par, sheet_val)

#Инициализируем байесовскую сеть и наполняем её данными, узлами и рёбрами
model = BayesianNetwork([('atm', 'surf'), ('infra', 'surf'), ('infra', 'catr'), ('atm', 'lum'), ('infra', 'lum'),('infra','prof'), ('infra','situ'), ('catr','int'),('int','circ'),
                       ('int','col'),('circ','manv'),('col','manv'),('catv','Severity'), ('surf','Severity'), ('situ','Severity'), ('lum','Severity'), ('manv','Severity'), 
                       ('prof','Severity')])
model.fit(df, estimator=MaximumLikelihoodEstimator)
#Проверяем корректность получившейся модели
print(model.check_model())
#Заводим переменную для расчёта предикта сценариев по параметрам пользователя
infer = VariableElimination(model)
#Да, калично, но динамического создания условия для байесовской сети пока не найдено/разработано
if len(sheet_par) == 1:
#Рассчитываем конечный результат в виде итоговой тяжести
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0]}))
#Тоже самое, но в виде таблицы вероятностей от наибольшей к наименьшей
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0]})
    print(prob_var)
#Повторяем это условие много-много раз, чтобы точно попасть в любое количество введённых пользователем параметров, для которых есть сценарии
elif len(sheet_par) == 2:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1]})
    print(prob_var)
elif len(sheet_par) == 3:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2]})
    print(prob_var)
elif len(sheet_par) == 4:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3]})
    print(prob_var)
elif len(sheet_par) == 5:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4]})
    print(prob_var)
elif len(sheet_par) == 6:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5]})
    print(prob_var)
elif len(sheet_par) == 7:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6]})
    print(prob_var)
elif len(sheet_par) == 8:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7]})
    print(prob_var)
elif len(sheet_par) == 9:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                  sheet_par[8]: sheet_val[8]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                   sheet_par[8]: sheet_val[8]})
    print(prob_var)
elif len(sheet_par) == 10:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                  sheet_par[8]: sheet_val[8], sheet_par[9]: sheet_val[9]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                   sheet_par[8]: sheet_val[8], sheet_par[9]: sheet_val[9]})
    print(prob_var)
elif len(sheet_par) == 11:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                  sheet_par[8]: sheet_val[8], sheet_par[9]: sheet_val[9], sheet_par[10]: sheet_val[10]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                   sheet_par[8]: sheet_val[8], sheet_par[9]: sheet_val[9], sheet_par[10]: sheet_val[10]})
    print(prob_var)
elif len(sheet_par) == 12:
    print(infer.map_query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                  sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                  sheet_par[8]: sheet_val[8], sheet_par[9]: sheet_val[9], sheet_par[10]: sheet_val[10], sheet_par[11]: sheet_val[11]}))
    prob_var = infer.query(['Severity'], evidence={sheet_par[0]: sheet_val[0], sheet_par[1]: sheet_val[1],sheet_par[2]: sheet_val[2], sheet_par[3]: sheet_val[3],
                                                   sheet_par[4]: sheet_val[4], sheet_par[5]: sheet_val[5], sheet_par[6]: sheet_val[6], sheet_par[7]: sheet_val[7],
                                                   sheet_par[8]: sheet_val[8], sheet_par[9]: sheet_val[9], sheet_par[10]: sheet_val[10], sheet_par[11]: sheet_val[11]})
    print(prob_var)
#По идее эта функция должна оценивать корректность самой байесовской сети, но ещё не доработана...ожидаем
#print(BayesianModelProbability(model))

finish = time.perf_counter()
print(str(finish - start))
