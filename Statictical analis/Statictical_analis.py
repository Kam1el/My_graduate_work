
from enum import unique
import os.path
from os import name
import pandas as pd
import openpyxl
import numpy as np

#����������� ��� ����������, ����� �� ����������
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
#������� ������ 10000 �������, ����� �������� �������
df = df[df.catv.index < 10000]
df.reset_index(drop=True, inplace=True)
#������� ����������� �� ���������� ��������� ��������, �����. ������� ��������� ������, ���������� �������� ������� �����
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
#������� �������, ���� ������ ������ �� ������� �����������
df.insert(14,"Severity", 0)
#�������� ������� � �������� ��� ��������� ����
df["grav"] = df["grav"].astype('int64')
df["Severity"] = df["Severity"].astype('object')
df["Num_Acc"] = df["Num_Acc"].astype('string')
#���������� ������� ������, �� ������������� � �������������� ������ ���������
values1 = [0,1,2,33,10,13,14,15,99,37,3,35,36,39,40]
values2 = [1,2,3,4]
df = df[(df.catv.isin(values1) == True)]
df = df[(df.grav.isin(values2) == True)]
#������� ��������� ������, ���������� �������� ������� �����
df.reset_index(drop=True, inplace=True)

#������������ ������� ������� ������������ �� ������ ������ � ������ ����� ������ 
#(� ����� ������, �.�. ������ ID ������ ����� ���� 2 � ����� �������, �.�. ������ ��������������� � ����� ������ ���� ���������� ������)
for row in range(0,len(df.index)):
    if df.iloc[row]['grav'] == 1:
        df.at[row,"Severity"] = "S0"
    elif df.iloc[row]['grav'] == 2:
        df.at[row,"Severity"] = "S1"
    elif df.iloc[row]['grav'] == 3:
        df.at[row,"Severity"] = "S2"
    elif df.iloc[row]['grav'] == 4:
        df.at[row,"Severity"] = "S3"

#������� � ����������� �� ���������� ����� �� �����, �������
df.drop('grav', axis= 1 , inplace= True)

#��������� ���������� �� ���������� ������������ ���� ���������
def check_scen(df, sheet_val, sheet_par):
    for i in range(0,len(sheet_val)):
        a = df[sheet_par[i]]
        df = df.loc[a == sheet_val[i]]
    return df

#��� �� ������ �������������� ����� � ��������
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

#��� �� ������ ����� ��������� � �������
def inp_scen_sev(df, variab = pd.DataFrame(test_date), scen_df = pd.DataFrame(test_date1), Response = "Yes", sheet_par = [], sheet_val = [], par_count = 0.0):
    #�������� ������ ���������� � �������� ��� ������ ����������
    while (Response != "No"):
        par_count += 1.0
        parameter = input("Enter parameter, please, only string ")
        sheet_par.append(parameter)
        print(sheet_par)
        param_val = int(input("Enter parameter value, please, only int "))
        sheet_val.append(param_val)
        print(sheet_val)
        #���������� � �������, ������� ��� ����� ������ ���������, ������� ������� �������
        df_fr_stat, scen_df = stat_for_param(parameter,df, param_val,scen_df, sheet_val, sheet_par)
        df_fr_stat['proportion'] = df_fr_stat['proportion'] + variab['proportion']
        variab = df_fr_stat
        #�������� ��������� ��� ���
        Response = input("Do you want to add other parameters. Only Yes/No ")
    #���� ��������� ��� �������� ��������� ���
    if len(scen_df) == 0:
        #����������, ��������� �� ��� ��� ���������
        ti = input('No such scenarios, try again? Only Yes/No ', )
        if ti == 'Yes':
            sheet_par = []
            sheet_val = []
            inp_scen_sev(df, variab = pd.DataFrame(test_date), scen_df = pd.DataFrame(test_date1), Response = "Yes", sheet_par = [], sheet_val = [], par_count = 0.0)
        else:
            return 0
    #���� �������� ���� ����
    else:                       
        variab['proportion'] = variab['proportion']/par_count
        df_fr_stat['proportion'] = variab['proportion'].transform(lambda x: '{:,.2%}'.format(x))
        #���������� ������ � ����
        with pd.ExcelWriter(r'C:\\Users\\PC\\Documents\\Diplom\\Scenarios.xlsx') as writer:
            scen_df.to_excel (writer,index= False, sheet_name='Scen')
            df_fr_stat.to_excel (writer,index= False, sheet_name='Sev')

inp_scen_sev(df, variab = pd.DataFrame(test_date), scen_df = pd.DataFrame(test_date1), Response = "Yes", sheet_par = [], sheet_val = [], par_count = 0.0)