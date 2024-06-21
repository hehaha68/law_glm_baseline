from LLM import *
from tools import *
from API import API

# 针对四个复杂问题，可以参考以下代码逻辑思考plan的逻辑以及所需要的具体操作。
# 改进使得LLM可以生成正确的任务规划。

def plan_4(question):
    PROMPT = f"""
根据例子，获取公司名称。
----
例子：
问题："熊猫乳品集团股份有限公司的全资控股子公司有几家？"
{{
    "公司名称": "熊猫乳品集团股份有限公司"
}}
----
问题："{question}"
直接输出json，可以被Python json.loads函数解析。不作解释，不作答：
```json
{{
    "公司名称": ""
}}
```
"""
    api_response = []
    response = LLM(PROMPT)
    company_name = prase_json_from_response(response)['公司名称']

    api_response.append(API(api_name='search_company_name_by_sub_info',  args={'key':'关联上市公司全称', 'value':company_name}))
    if len(api_response[-1]) == 0:
        new_company_name = company_name_check(company_name)
        api_response.append(API(api_name='search_company_name_by_sub_info',  args={'key':'关联上市公司全称', 'value':new_company_name}))
    
    sub_com=[]
    for res in api_response[-1]:
        api_response.append(API(api_name='get_sub_company_info',  args={'company_name':res['公司名称']}))
        if api_response[-1]['上市公司参股比例'] is not None and float(api_response[-1]['上市公司参股比例']) == 100:
            sub_com.append(res['公司名称'])

    answer = refine_answer(question, f"满足条件的子公司数量为{len(sub_com)}")
    return answer

def plan_2(question):
    PROMPT = f"""
根据数据表和列表，提取问题中的公司名称和属性名称。
----
数据表属性：关联上市公司股票代码, 关联上市公司股票简称, 关联上市公司全称, 上市公司关系, 上市公司参股比例, 上市公司投资金额, 公司名称
----
例子：
问题："深圳市大族瑞利泰德精密涂层有限公司归属于哪家母公司？这家母公司控股它的股权比例是多少？包括这家在内，他们有多少家子公司？"
[
    {{
        "公司名称": "深圳市大族瑞利泰德精密涂层有限公司"
    }},
    {{
        "属性名称": "上市公司参股比例"
    }}
]
----
问题："{question}"
直接输出json，可以被Python json.loads函数解析。不作解释，不作答。属性名称只有一个。
```json
[
    {{
        "公司名称": ""
    }},
    {{
        "属性名称": ""
    }}
]
```
"""
    api_response = []
    answer = []
    response = LLM(PROMPT)
    question_list = prase_json_from_response(response)

    api_response.append(API(api_name='get_sub_company_info', args={'company_name': question_list[0]['公司名称']}))
    answer.append(f"上市公司全称:{api_response[-1]['关联上市公司全称']}, {question_list[1]['属性名称']}:{api_response[-1][question_list[1]['属性名称']]}")
    
    api_response.append(API(api_name='search_company_name_by_sub_info', args={'key': '关联上市公司全称', 'value': api_response[-1]['关联上市公司全称']}))
    answer.append(refine_answer(question,answer[0]+f"子公司数为{len(api_response[-1])}"))
    return answer[-1]

def plan_3(question):
    PROMPT = f"""
根据例子，提取公司名称。
----
例子：
问题："我想确认下福龙马集团股份有限公司公司控股比例最高的子公司与自身的具体关系，并说明该项投资的具体金额及该公司子公司总数"
{{
    "公司名称": "福龙马集团股份有限公司"
}}
----
问题："{question}"
直接输出json，可以被Python json.loads函数解析。不作解释，不作答：
```json
{{
    "公司名称": ""
}}
```
"""
    import heapq
    def top_k_elements_with_indices(lst, k):
        indexed_lst = [(val, idx) for idx, val in enumerate(lst)]
        top_k = heapq.nlargest(k, indexed_lst)
        top_k_values, top_k_indices = zip(*top_k)
        return list(top_k_indices), list(top_k_values)
    
    api_response = []
    answer = []
    response = LLM(PROMPT)
    company_name = prase_json_from_response(response)['公司名称']

    api_response = API(api_name='search_company_name_by_sub_info', args={'key':"关联上市公司全称", 'value':company_name})

    if isinstance(api_response, list):
        sub_name = []
        sub_rate = []
        for res in api_response:
            sub = API(api_name='get_sub_company_info', args={'company_name': res['公司名称']})
            sub_name.append(sub['公司名称'])
            sub_rate.append(sub['上市公司参股比例'])
        idx, _ = top_k_elements_with_indices(sub_rate, 1)
        sub = API(api_name='get_sub_company_info', args={'company_name': sub_name[idx[0]]})
        answer = f"关系为“{sub['上市公司关系']}”， 金额为{sub['上市公司投资金额']}，子公司总数为{len(api_response)}"
    else:
        sub = API(api_name='get_sub_company_info', args={'company_name':api_response['公司名称']})
        answer = f"关系为“{sub['上市公司关系']}”， 金额为{sub['上市公司投资金额']}，子公司总数为1"

    answer = refine_answer(question, answer)

    return answer

def plan_1(question):
    PROMPT = f"""
根据例子，提取公司名称。
----
例子：
问题："贵人鸟股份有限公司的主要投资对象是哪一家企业？"
{{
    "公司名称": "贵人鸟股份有限公司"
}}
----
问题："{question}"
直接输出json，可以被Python json.loads函数解析。不作解释，不作答：
```json
{{
    "公司名称": ""
}}
```
"""
    import heapq
    def top_k_elements_with_indices(lst, k):
        indexed_lst = [(val, idx) for idx, val in enumerate(lst)]
        top_k = heapq.nlargest(k, indexed_lst)
        top_k_values, top_k_indices = zip(*top_k)
        return list(top_k_indices), list(top_k_values)
    
    api_response = []
    answer = []
    response = LLM(PROMPT)
    question_list = prase_json_from_response(response)

    api_response.append(API(api_name='search_company_name_by_sub_info',args={'key':'关联上市公司全称','value':question_list['公司名称']}))
    name_list=[]
    value_list=[]
    for res in api_response[0]:
        sub = API(api_name='get_sub_company_info',args={'company_name':res['公司名称']})
        name_list.append(res['公司名称'])
        value = sub['上市公司投资金额']
        if value is None:
            value = 0
        elif '万' in value:
            value = float(value[:-1])
        elif '亿' in value:
            value = float(value[:-1]) * 10000
        elif len(value) <= 2:
            value = 10000
        else:
            value = float(value)
        value_list.append(value)

    idx, _ =top_k_elements_with_indices(value_list,1)
    
    answer.append(refine_answer(question,f'答案是{name_list[idx[0]]}'))
    return answer[-1]
