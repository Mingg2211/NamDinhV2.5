from bot_brain import *
import pandas as pd

df = pd.read_csv('../data/ND_procedure.csv')
procedure_list = df.id.tolist()

not_cover = []
for procedure in procedure_list:
    list_relevant = []
    relevant = bot_searching(procedure)
    if relevant == 'Tôi chưa được học thủ tục này :(' :
        not_cover.append(procedure)
    else:
        for item in relevant :
            list_relevant.append(item['procedure'])
        if procedure not in list_relevant:
            not_cover.append(procedure)

with open('exceptions.txt','w') as f:
    for item in sorted(not_cover, key=len):
        if len(item.split(" ")) < 22 :
            f.write(item)
            f.write('\n')