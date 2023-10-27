#文心一言调用 ERNIE-Bot
import requests
import json

def get_access_token(API_KEY,Secret_Key):
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
        
    url = f"https://aip.baidubce.com/oauth/2.0/token?client_id={API_KEY}&client_secret={Secret_Key}&grant_type=client_credentials"

    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def main(API_KEY,Secret_Key,messgaes):
    #ERNIE-Bot
    # url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token=" + get_access_token(API_KEY,Secret_Key)
    #ERNIE-Bot-turbo
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/eb-instant?access_token=" + get_access_token(API_KEY,Secret_Key)
    payload = json.dumps({
        "messages": messgaes
    })
    # payload = json.dumps({
    #     "messages": content})
    headers = {
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    print(response.text)

if __name__ == "__main__":
    AK = '' #填写控制台中获取的 	API Key 信息
    SK = '' #填写控制台中获取的 	Secret Key 信息
    messages =  [  
    {'role':'system', 'content':'You are an assistant that speaks like Shakespeare.'},    
    {'role':'user', 'content':'tell me a joke'},   
    {'role':'assistant', 'content':'Why did the chicken cross the road'},   
    {'role':'user', 'content':'I don\'t know'}  ]
    main(AK,SK,messages)