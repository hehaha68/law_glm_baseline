from action import *
from LLM import *
from tools import *
from complex import *
from prompt import COMPLEX_QUESTION, TABLE_PLAN_PROMPT


def execute_plan(question, plan_id):
    if plan_id == 2:
        # 处理几个复杂问题
        response = LLM(COMPLEX_QUESTION.format(question=question))
        print(prase_json_from_response(response)['类别序号'])
        category = int(prase_json_from_response(response)['类别序号'])
        plan_map = {6: plan_1, 7: plan_2, 8: plan_3, 9: plan_4}
        if category >= 6:
            answer = plan_map[category](question)
            return answer
        else:
            question = refine_question(question)
    
    response = LLM(TABLE_PLAN_PROMPT[plan_id-1].format(question=question))
    plan = prase_json_from_response(response)

    # 执行plan
    plan_map = {"查询": retrieve, "统计": stat, "排序": order, "总结": summary, "多次查询": multi_retrieve, "条件筛选": filter_list, "总金额计算": calculate_cash}
    answer=[]
    data=None
    sub_answer=''
    for sub_plan in plan:
        try:
            if sub_plan["是否需要前序结果"] == 'False':
                question = sub_plan['问题']
            else:
                question = sub_answer+'\n'+sub_plan['问题']
            sub_answer, data = plan_map[sub_plan['操作']](question, data)
            answer.append(sub_answer)
        except:
            pass
    return answer