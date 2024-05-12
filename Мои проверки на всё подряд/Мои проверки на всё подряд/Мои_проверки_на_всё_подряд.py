from enum import unique
import numpy as np
import pandas as pd
import openpyxl
from pgmpy.models import BayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator, BayesianEstimator
from pgmpy.utils import get_example_model
from pgmpy.inference import VariableElimination
from pgmpy.metrics import correlation_score, log_likelihood_score, BayesianModelProbability

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
df.drop('Num_Acc', axis= 1 , inplace= True)
print(list(df))
print(df.head(1))
model = BayesianNetwork([('atm', 'surf'), ('infra', 'surf'), ('infra', 'catr'), ('atm', 'lum'), ('infra', 'lum'),('infra','prof'), ('infra','situ'), ('catr','int'),('int','circ'),
                       ('int','col'),('circ','manv'),('col','manv'),('catv','Severity'), ('surf','Severity'), ('situ','Severity'), ('lum','Severity'), ('manv','Severity'), 
                       ('prof','Severity')])
#estimator = MaximumLikelihoodEstimator(model, df)
#print(estimator.get_parameters())


model.fit(df, estimator=MaximumLikelihoodEstimator)

#print(model.get_cpds())
print(model.check_model())
#print(model.get_cpds('Severity'))
#cpd = model.get_cpds('Severity')
#cpd.to_csv(filename='sao2_cpd.csv')
infer = VariableElimination(model)
print(infer.map_query(['Severity'], evidence={'atm': 1, 'manv': 3}))
prob_var = infer.query(['Severity'], evidence={'atm': 1, 'manv': 1})
print(prob_var)

print(BayesianModelProbability(model))
#for cpd in model.get_cpds():
# print("CPD of {variable}:".format(variable=cpd.variable))
# print(cpd)
 


# Splitting the data into train and test sets 
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.15, random_state = 42) 
  
# Creating and training the Complement Naive Bayes Classifier 
#classifier = ComplementNB() 
#classifier.fit(X_train, y_train) 
  
# Evaluating the classifier 
#prediction = classifier.predict(X_test) 
#prediction_train = classifier.predict(X_train) 
  
#print(f"Training Set Accuracy : {accuracy_score(y_train, prediction_train) * 100} %\n") 
#print(f"Test Set Accuracy : {accuracy_score(y_test, prediction) * 100} % \n\n") 
#print(f"Classifier Report : \n\n {classification_report(y_test, prediction)}")