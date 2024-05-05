
import numpy as np
import pandas as pd

df = pd.read_excel(r"C:\Users\PC\Documents\Diplom\Bayes_start_table_1.xlsx", engine='openpyxl', header = 0)
#������� ������ 10000 �������, ����� �������� �������
df = df[df.catv.index < 10000].reset_index()
#������� ����������� �� ���������� ��������� ��������, �����
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
# print(df.columns)
#������� �������, ���� ������ ������ �� ������� �����������
df.insert(15,"Severity", 0)
df["grav"] = df["grav"].astype('int64')
df["Severity"] = df["Severity"].astype('object')
print(df.index)
print(df.last_valid_index())

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

values = [0,1,2,33,10,13,14,15,99,37,3,35,36,39,40]
df = df[(df.catv.isin(values) == True)]

print(df.head(n=10))
print(df.last_valid_index())