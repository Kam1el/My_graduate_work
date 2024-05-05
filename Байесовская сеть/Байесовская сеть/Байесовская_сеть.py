
import numpy as np
import pandas as pd
from IPython.display import display

df = pd.read_excel(r"C:\Users\PC\Documents\Diplom\Bayes_start_table_1.xlsx", engine='openpyxl', header = 0)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(df.columns)
values = [0,1,2,33,10,13,14,15,99,37,3,35,36,39,40]
df = df[(df.catv.isin(values) == True)]
print(df.head(n=10))
