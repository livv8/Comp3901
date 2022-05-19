import pandas as pd
import os

Directory_fol = pd.DataFrame()

for file in os.listdir(os.getcwd()):
    if file.endswith('.csv'):
        Directory_fol = Directory_fol.append(pd.read_csv(file))

Directory_fol.to_csv('Stores.csv', index=False)