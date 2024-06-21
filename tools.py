from zhipuai import ZhipuAI
import json, re
from LLM import get_json_response
from API import API

API_KEY = <YOUR_API_KEY>

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_company_info",
            "description": "根据提供的公司名称，查询该公司的基本信息。参数为中文。",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "公司名称",
                    }
                },
                "required": ["company_name"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_name_by_info",
            "description": "根据公司基本信息某个字段是某个值来查询具体的公司名称。参数为中文。基本信息有：公司名称, 公司简称, 英文名称, 关联证券, 公司代码, 曾用简称, 所属市场, 所属行业, 上市日期, 法人代表, 总经理 ,董秘, 邮政编码, 注册地址, 办公地址, 联系电话, 传真, 官方网址, 电子邮箱, 入选指数, 主营业务, 经营范围, 机构简介, 每股面值, 首发价, 首发募资净额, 首发主承销商。",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "基本信息的字段",
                    },
                    "value": {
                        "type": "string",
                        "description": "基本信息的字段对应的值",
                    }
                },
                "required": ["key", "value"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_company_register",
            "description": "根据公司名称，获得该公司的注册信息。参数为中文。",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "公司名称",
                    }
                },
                "required": ["company_name"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_name_by_register",
            "description": "根据公司注册信息某个字段是某个值，来查询具体的公司名称。参数为中文。注册信息有：公司名称, 登记状态, 统一社会信用代码, 注册资本, 成立日期, 省份, 城市, 区县, 注册号, 组织机构代码, 参保人数, 企业类型, 曾用名。",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "注册信息的字段",
                    },
                    "value": {
                        "type": "string",
                        "description": "注册信息的字段对应的值",
                    }
                },
                "required": ["key", "value"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sub_company_info",
            "description": "根据公司名称，获得该公司的关联子公司信息。参数为中文。",
            "parameters": {
                "type": "object",
                "properties": {
                    "company_name": {
                        "type": "string",
                        "description": "公司名称",
                    }
                },
                "required": ["company_name"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_company_name_by_sub_info",
            "description": "根据关联子公司信息某个字段是某个值，来查询具体的公司名称。参数为中文。信息有：关联上市公司股票代码, 关联上市公司股票简称, 关联上市公司全称, 上市公司关系, 上市公司参股比例, 上市公司投资金额, 公司名称。",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "关联子公司信息的字段",
                    },
                    "value": {
                        "type": "string",
                        "description": "关联子公司信息的字段对应的值",
                    }
                },
                "required": ["key", "value"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_legal_document",
            "description": "根据案号获得该案的基本信息。参数为中文。",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_num": {
                        "type": "string",
                        "description": "案号",
                    }
                },
                "required": ["case_num"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_case_num_by_legal_document",
            "description": "根据法律文书某个字段是某个值，来查询具体的案号。参数为中文。信息有：标题, 案号, 文书类型, 原告, 被告, 原告律师, 被告律师, 案由, 审理法条依据, 涉案金额, 判决结果, 胜诉方, 文件名。",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "法律文书信息的字段",
                    },
                    "value": {
                        "type": "string",
                        "description": "法律文书信息的字段对应的值",
                    }
                },
                "required": ["key","value"],
            },
        }
    }
]

def get_tools_response(query):
    messages = [
        {
            "role": "user",
            "content": query
        }
    ]

    client = ZhipuAI(api_key=API_KEY)
    response = client.chat.completions.create(
        model="glm-4",
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    function = response.choices[0].message.tool_calls[0].function
    print(function)
    func_args = function.arguments
    func_name = function.name
    return func_name, json.loads(func_args)

# 解析LLM生成的json
def prase_json_from_response(rsp: str):
    pattern = r"```json(.*?)```"
    rsp_json = None
    try:
      match = re.search(pattern, rsp, re.DOTALL)
      if match is not None:
        try:
          rsp_json =  json.loads(match.group(1).strip())
        except:
          pass
      else:
        rsp_json  = json.loads(rsp)
      return rsp_json
    except json.JSONDecodeError as e:
      raise("Json Decode Error: {error}".format(error = e))
# 公司名称检查    
def company_name_check(company_name):
    PROMPT = """已知【公司名称】是数据表中的主键，需要用公司的全称才能够查询到公司的信息。
名称：{company_name} 不存在于数据表中，思考该名称是【公司简称】还是【英文名称】。

----
例子1：
名称：劲拓股份
{{
    "判断": "劲拓股份是【公司简称】。"
}}

例子2：
名称：Shanghai Construction Group Co., Ltd.
{{
    "判断": "Shanghai Construction Group Co., Ltd.是【英文名称】。"
}}

----
直接输出json，可以被Python json.loads函数解析。只给出判断，不作解释，不作答：
{{ 
        "判断": ""
}}
    """
    prompt = PROMPT.format(company_name=company_name)
    response = get_json_response(query=prompt)
    if '公司简称' in response["判断"]:
       new_company_name = API(api_name='search_company_name_by_info', args={"key":"公司简称","value":company_name})['公司名称']
    elif '英文名称' in response["判断"]:
       new_company_name = API(api_name='search_company_name_by_info', args={"key":"英文名称","value":company_name})['公司名称']
    print(f"公司名称为: “{new_company_name}”")
    return new_company_name, f"公司名称为: “{new_company_name}”"