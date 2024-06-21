import requests

def API(api_name, args):
    domain = "comm.chatglm.cn"
    url = f"https://{domain}/law_api/{api_name}"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer <YOUR_TEAM_ID>'
    }
    rsp = requests.post(url, json=args, headers=headers)
    return rsp.json()

