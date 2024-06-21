from zhipuai import ZhipuAI
import json
MAX_RETRY = 5
API_KEY = <YOUR_API_KEY>

def LLM(query):
    client = ZhipuAI(api_key=API_KEY)
    response = client.chat.completions.create(
    model="glm-4",
        messages=[
            {"role": "user", "content": query},
        ],
        stream=False,
        )
    return response.choices[0].message.content

def get_json_response(query, max_retries=MAX_RETRY):
    response = LLM(query)
    for retry in range(max_retries):
        try:
            response = LLM(query)
            # print(response)
            response = json.loads(response)
            return response
        except Exception as e:
            print(f"解析失败，正在进行第{retry+1}次重试，错误信息：{e}")
            if retry == max_retries - 1:
                print(f"解析失败，已达到最大重试次数{max_retries}。")
                return None
            
def refine_answer(question, answer):
    prompt=f"""
    问题：{question}
    信息：{answer}
    请整合答案，直接给出简洁、完整且清晰的回答。回答格式忠于提问方式。不要回答问题之外的内容。
    回答：
    """
    final_answer = LLM(query=prompt)
    return final_answer

def refine_question(question):
    prompt=f"""根据例子，完善问题
例子：劲拓股份拥有哪些子公司
完善：关联上市公司全称是劲拓股份的公司拥有哪些子公司

例子：华仁药业股份有限公司控股的子公司中，持股比例超过50%的有几家？
完善：关联上市公司全称是华仁药业股份有限公司控股的子公司中，持股比例超过50%的有几家？

例子：北京华清瑞达科技有限公司、博晖生物制药（内蒙古）有限公司、浙江迪安健检医疗管理有限公司分别属于哪几家公司的子公司
完善：北京华清瑞达科技有限公司、博晖生物制药（内蒙古）有限公司、浙江迪安健检医疗管理有限公司分别属于哪几家公司的子公司

例子：Shanghai Construction Group Co., Ltd.拥有哪些子公司？
完善：关联上市公司全称是Shanghai Construction Group Co., Ltd.拥有哪些子公司？
----
问题：{question}
完善：(不要回答问题)"""
    return LLM(prompt)