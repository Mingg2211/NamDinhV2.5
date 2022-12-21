import pandas as pd
import json
from itertools import chain
from underthesea import word_tokenize
import re

BOT_MEMORY = {'keywords': [], 'action': []}

def remove_tone_line(utf8_str):
    intab_l = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđ"
    intab_u = "ẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸĐ"
    intab = list(intab_l+intab_u)

    outtab_l = "a"*17 + "o"*17 + "e"*11 + "u"*11 + "i"*5 + "y"*5 + "d"
    outtab_u = "A"*17 + "O"*17 + "E"*11 + "U"*11 + "I"*5 + "Y"*5 + "D"
    outtab = outtab_l + outtab_u

    r = re.compile("|".join(intab))
    replaces_dict = dict(zip(intab, outtab))
    return r.sub(lambda m: replaces_dict[m.group(0)], utf8_str)


def preprocessing(text):
    text = remove_tone_line(text)
    text = text.lower().replace('thu tuc','')
    text = re.sub(' +', ' ',text)
    text = re.sub(r'[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ_\.\,]',' ',text)
    return text

def remove_dup(result_list):
    tmp_list = list(dict.fromkeys(result_list))
    # tmp_list = sorted(tmp_list, key=len)
    return tmp_list


def bot_understand(user_question: str):
    global BOT_MEMORY
    keyword_list = []
    action = []
    # load keyword dictionary
    with open('../json_data/keyword.json', 'r', encoding='utf-8') as f1:
        keyword_dict = json.load(f1)
        
    with open('../json_data/action.json', 'r', encoding='utf-8') as f2:
        action_dict = json.load(f2)
        
    for key in keyword_dict.keys():
        for val in keyword_dict[key]:
            if val in user_question:
                keyword_list.append(key)
                user_question = user_question.replace(val, '')

    for key in action_dict.keys():
        for val in action_dict[key]:
            if val in user_question:
                action.append(key)
                user_question = user_question.replace(val, '')
    
    BOT_MEMORY.update({'keywords': keyword_list})
    BOT_MEMORY.update({'action': action})
    
    return BOT_MEMORY

# print(bot_understand('Tối muốn đăng ký kết hôn với người nước ngoài thì cần phải chuẩn bị giấy tờ gì lệ phí'))


def search_token_in_database(user_token):
    df = pd.read_csv('../data/new_procedure.csv', engine='python')
    # print(df.info())
    procedures = df[df.procedure_name.str.contains(user_token, na=False)].id
    procedure_list = procedures.tolist()
    # print(procedures.tolist())
    # flatten 2d listresponse
    # procedure_list = list(chain.from_iterable(procedures.tolist()))
    # print(procedure_list)
    procedure_list = sorted(procedure_list, key=len)
    return procedure_list

# print(search_token_in_database('kết hôn'))

def search_list_token_in_database(list_user_token: list):
    tmp_list = []
    for token in list_user_token:
        tmp_list += search_token_in_database(token)
    if len(list_user_token) == 2:
        df = pd.DataFrame({'procedure': tmp_list})

        df1 = pd.DataFrame(data=df['procedure'].value_counts())

        df1['Count'] = df1['procedure'].index

        mingg = list(df1[df1['procedure'] == 2]['Count'])

        return mingg
    elif len(list_user_token) == 3:
        df = pd.DataFrame({'procedure': tmp_list})

        df1 = pd.DataFrame(data=df['procedure'].value_counts())

        df1['Count'] = df1['procedure'].index

        mingg = list(df1[df1['procedure'] == 3]['Count'])

        return mingg


def bot_searching(user_question: str):
    user_question = preprocessing(user_question)
    BOT_MEMORY = bot_understand(user_question)
    result = []
    keywords = BOT_MEMORY['keywords']
    action = BOT_MEMORY['action']
    
    if keywords:
        keywords = remove_dup(keywords)

        # Trả cụm động từ : VP = V1 + V2
        VP = ' '.join(key for key in keywords)
        # print(VP)
        VP_procedure_list = search_token_in_database(VP)
        if VP_procedure_list:
            result += VP_procedure_list
        # Lấy duplicate
        if len(keywords) >= 2:
            DUP_procedure_list = search_list_token_in_database(keywords)
            if DUP_procedure_list:
                result += DUP_procedure_list
        print(keywords)
        if len(keywords) != 0:
            result += search_token_in_database(keywords[0])
        result = remove_dup(result)
        # Lấy K=5
        if result:
            tmp = result[:5]
            response_json = []
            for item in tmp:
                response_json.append({'procedure': item, 'action': action})
            return response_json
        else:
            return "Tôi chưa được học thủ tục này :("
    else:
        list_user_token = word_tokenize(user_question)
        tmp = []
        for token in list_user_token:
            tmp += search_token_in_database(token)
        df = pd.DataFrame({'procedure': tmp})
        df1 = pd.DataFrame(data=df['procedure'].value_counts())
        df1['Count'] = df1['procedure'].index
        result = list(df1[df1['procedure'] >= df1.procedure.max()-3]['Count'])
        if result:
            tmp = result[:5]
            response_json = []
            for item in tmp:
                response_json.append({'procedure': item, 'action': action})
            return response_json
        else:
            return "Tôi chưa được học thủ tục này :("
print(bot_searching('Tối muốn đăng ký kết hôn'))

def bot_answer(procedure_name, action):
    df = pd.read_csv('../data/new_procedure.csv', engine='python')
    df = df.fillna('')
    procedure_name = remove_tone_line(procedure_name)
    index = df.index[df['procedure_name'] == procedure_name].tolist()
    if action:
        answer = df.at[index[0], action[0]]
    else:
        answer = df.iloc[index[0]]
        answer = answer.drop(labels=['procedure_name'])
    return answer
# print(bot_answer('thủ tục đăng ký kết hôn có yếu tố nước ngoài', []))

def mingg(user_question:str):
    user_question = user_question.strip()
    list_relevant = bot_searching(user_question)
    best_matching = list_relevant[0]
    print(best_matching)
    final_answer = bot_answer(best_matching['procedure'], best_matching['action'])
    return final_answer

print(mingg('tôi muốn cưới chồng người nước ngoài'))
    