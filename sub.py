from LLM import LLM, get_json_response, refine_answer
from API import API
from prompt import TABLE_PROMPT, TABLE_PLAN_PROMPT, QUESTION_CLASS
from tools import get_tools_response, prase_json_from_response
from execute_plan import execute_plan
import json



Table_solution=[]

table_plan_map = {'company_info': 1,'company_register': 1,'sub_company_info': 2,'legal_document': 3}

with open('question(1).json', 'r', encoding='utf-8') as f:
    lines = f.readlines()
data = [json.loads(line.strip()) for line in lines]

for q in data:
    try:
        ans = q['answer']
        continue
    except:
        question = q['question']
        print(q['id'],question)
        try:
            ### 问题分类：直接作答、需要检索
            prompt = QUESTION_CLASS.format(question=question)
            response = prase_json_from_response(LLM(prompt))
            if response["category_name"] == "direct_answer":
                answer = LLM(query=question)
            else:
                ### 表-方案分类：
                response = LLM(TABLE_PROMPT.format(question=q['question']))
                plan_id = table_plan_map[prase_json_from_response(response)["名称"]]
                answer = execute_plan(question, plan_id)
                answer = refine_answer(q['question'], answer)
        except:
            answer = q['question']
        q['answer'] = answer
        print(q['answer'])


with open("submission.json", "w", encoding="utf-8") as f:
    for item in data:
        f.write(json.dumps(item, ensure_ascii=False) + "\n")
