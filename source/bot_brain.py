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


uniChars = "àáảãạâầấẩẫậăằắẳẵặèéẻẽẹêềếểễệđìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵÀÁẢÃẠÂẦẤẨẪẬĂẰẮẲẴẶÈÉẺẼẸÊỀẾỂỄỆĐÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴÂĂĐÔƠƯ"
unsignChars = "aaaaaaaaaaaaaaaaaeeeeeeeeeeediiiiiooooooooooooooooouuuuuuuuuuuyyyyyAAAAAAAAAAAAAAAAAEEEEEEEEEEEDIIIOOOOOOOOOOOOOOOOOOOUUUUUUUUUUUYYYYYAADOOU"


def loaddicchar():
    dic = {}
    char1252 = 'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ'.split(
        '|')
    charutf8 = "à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ".split(
        '|')
    for i in range(len(char1252)):
        dic[char1252[i]] = charutf8[i]
    return dic


dicchar = loaddicchar()


def covert_unicode(txt):
    return re.sub(
        r'à|á|ả|ã|ạ|ầ|ấ|ẩ|ẫ|ậ|ằ|ắ|ẳ|ẵ|ặ|è|é|ẻ|ẽ|ẹ|ề|ế|ể|ễ|ệ|ì|í|ỉ|ĩ|ị|ò|ó|ỏ|õ|ọ|ồ|ố|ổ|ỗ|ộ|ờ|ớ|ở|ỡ|ợ|ù|ú|ủ|ũ|ụ|ừ|ứ|ử|ữ|ự|ỳ|ý|ỷ|ỹ|ỵ|À|Á|Ả|Ã|Ạ|Ầ|Ấ|Ẩ|Ẫ|Ậ|Ằ|Ắ|Ẳ|Ẵ|Ặ|È|É|Ẻ|Ẽ|Ẹ|Ề|Ế|Ể|Ễ|Ệ|Ì|Í|Ỉ|Ĩ|Ị|Ò|Ó|Ỏ|Õ|Ọ|Ồ|Ố|Ổ|Ỗ|Ộ|Ờ|Ớ|Ở|Ỡ|Ợ|Ù|Ú|Ủ|Ũ|Ụ|Ừ|Ứ|Ử|Ữ|Ự|Ỳ|Ý|Ỷ|Ỹ|Ỵ',
        lambda x: dicchar[x.group()], txt)


def preprocessing(text):
    text =covert_unicode(text)
    #stopwords 
    stopwords = ['thủ tục', 'giải quyết', 'cho hỏi', 'cho tôi hỏi', 'cho tôi hỏi về', 'tôi muốn hỏi', 'quy định', 'hỏi', 'thuộc']
    for word in stopwords:
        if word in text:
            text = text.replace(word, "")
    text = remove_tone_line(text)
    text = text.lower()
    text = re.sub(' +', ' ',text)
    return text.strip()

print(preprocessing('thủ tục tuyển chọn, giao trực tiếp đề tài thuộc lĩnh vực khxh&nv'))

def remove_dup(result_list):
    tmp_list = list(dict.fromkeys(result_list))
    # tmp_list = sorted(tmp_list, key=len)
    return tmp_list


def bot_understand(user_question: str):
    global BOT_MEMORY
    keyword_list = []
    action = []
    user_question_action = preprocessing(user_question)
    user_question_keyword = user_question_action
    # load keyword dictionary
    with open('../json_data/keyword.json', 'r', encoding='utf-8') as f1:
        keyword_dict = json.load(f1)
        
    with open('../json_data/action.json', 'r', encoding='utf-8') as f2:
        action_dict = json.load(f2)
    
    for key in action_dict.keys():
        for val in action_dict[key]:
            if (re.search(r'\b'+val+r'\b', user_question_action)):
                action.append(key)
                user_question_action = user_question_action.replace(val, '')
    
    print(user_question)
    for key in keyword_dict.keys():
        for val in keyword_dict[key]:
            if (re.search(r'\b'+val+r'\b', user_question_keyword)):
                keyword_list.append(key)
                user_question_keyword = user_question_keyword.replace(val, '')
                

    BOT_MEMORY.update({'keywords': keyword_list})
    BOT_MEMORY.update({'action': action})
    
    return BOT_MEMORY

# print(bot_understand('che do uu dai'))


def search_token_in_database(user_token):
    df = pd.read_csv('../data/new_procedure.csv', engine='python')
    # print(df.info())
    user_token = r'\b'+user_token+r'\b'
    procedures = df[df.procedure_name.str.contains(pat=user_token, na=False, regex=True)].id
    procedure_list = procedures.tolist()
    # print(procedures.tolist())
    # flatten 2d listresponse
    # procedure_list = list(chain.from_iterable(procedures.tolist()))
    # print(procedure_list)
    procedure_list = sorted(procedure_list, key=len)
    return procedure_list
# print(search_token_in_database('ket hon'))

def search_list_token_in_database(list_user_token: list):
    tmp_list = []
    for token in list_user_token:
        tmp_list += search_token_in_database(token)
    print(len(tmp_list))
    n = len(list_user_token)
    if n == 2 :
        df = pd.DataFrame({'procedure': tmp_list})

        df1 = pd.DataFrame(data=df['procedure'].value_counts())

        df1['Count'] = df1['procedure'].index

        mingg = list(df1[df1['procedure'] == n]['Count'])

        return mingg
    if n >= 3:
        df = pd.DataFrame({'procedure': tmp_list})

        df1 = pd.DataFrame(data=df['procedure'].value_counts())

        df1['Count'] = df1['procedure'].index

        mingg = list(df1[df1['procedure'] >= 2]['Count'])
        return mingg

print(search_list_token_in_database(['thuoc phien', 'nghien']))


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
                # print(result)
        print(keywords)
        if len(keywords) != 0:
            result += search_token_in_database(keywords[0])
        result = remove_dup(result)
        # Lấy K=5
        if result:
            tmp = result[:5]
            # tmp = sorted(tmp, key=len)
            response_json = []
            for item in tmp:
                response_json.append({'procedure': item, 'action': action})
            return response_json
        else:
            return "Tôi chưa được học thủ tục này :("
    else:
        # list_user_token = word_tokenize(user_question)
        # print(list_user_token)
        # tmp = []
        # for token in list_user_token:
        #     tmp += search_token_in_database(token)
        # df = pd.DataFrame({'procedure': tmp})
        # df1 = pd.DataFrame(data=df['procedure'].value_counts())
        # df1['Count'] = df1['procedure'].index
        # result = list(df1[df1['procedure'] >= df1.procedure.max()-2]['Count'])
        # if result:
        #     tmp = result[:5]
        #     response_json = []
        #     for item in tmp:
        #         response_json.append({'procedure': item, 'action': action})
        #     return response_json
        # else:
        return "Tôi chưa được học thủ tục này :("
# print(bot_searching('Thời hạn giải quyết thủ tục cấp lại giấy đăng ký tham gia trợ giúp pháp lý?'))

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

# print(mingg('tôi muốn cưới chồng người nước ngoài'))
    