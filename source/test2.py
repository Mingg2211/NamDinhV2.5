from bot_brain import *
import pandas as pd

df = pd.read_csv('../data/new_procedure.csv')
procedure_list = df.id.tolist()

n_key = []
for procedure in procedure_list:
    memory = bot_understand(procedure)
    if len(memory['keywords']) > 3 :
        n_key.append(procedure)
with open('n_key.txt', 'w') as f:
    for i in n_key:
        f.write(str(i))
        f.write('\n')
    