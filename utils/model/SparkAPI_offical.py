import _thread as thread
import base64
import datetime
import hashlib
import hmac
import json
from urllib.parse import urlparse
import ssl
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from typing import Literal
import requests
import websocket  # 使用websocket_client

class Ws_Param(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, Spark_url):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.host = urlparse(Spark_url).netloc
        self.path = urlparse(Spark_url).path
        self.Spark_url = Spark_url

    # 生成url
    def create_url(self,method:Literal["GET","POST"]):
        #method websocket对话用GET embedding用POST
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + self.host + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += method + " " + self.path + " HTTP/1.1"

        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()

        signature_sha_base64 = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'

        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": self.host
        }
        # 拼接鉴权参数，生成url
        url = self.Spark_url + '?' + urlencode(v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        return url


class Spark_interface:
    def __init__(self,appid, api_key, api_secret, Spark_url,domain,temperature,max_tokens) -> None:
        self.answer = ''
        self.domain = domain
        self.appid = appid
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.wsParam = Ws_Param(appid, api_key, api_secret, Spark_url)
        websocket.enableTrace(False)

    # 收到websocket错误的处理
    def on_error(self,ws, error):
        print("### error:", error)

    # 收到websocket关闭的处理
    def on_close(self,ws,one,two):
        print(" ")

    # 收到websocket连接建立的处理
    def on_open(self,ws):
        thread.start_new_thread(self.run, (ws,))

    def run(self,ws, *args):
        data = json.dumps(self.gen_params(appid=ws.appid, domain= ws.domain,question=ws.question))
        ws.send(data)

    # 收到websocket消息的处理
    def on_message(self,ws, message):
        # print(message)
        data = json.loads(message)
        code = data['header']['code']
        if code != 0:
            print(f'请求错误: {code}, {data}')
            ws.close()
        else:
            choices = data["payload"]["choices"]
            status = choices["status"]
            content = choices["text"][0]["content"]
            # print(content,end ="")
            self.answer += content
            # print(1)
            if status == 2:
                ws.close()

    def gen_params(self,appid, domain,question):
        """
        通过appid和用户的提问来生成请参数
        """
        data = {
            "header": {
                "app_id": appid,
                "uid": "1234"
            },
            "parameter": {
                "chat": {
                    "domain": domain,
                    "random_threshold": 0.5,
                    "max_tokens": self.max_tokens,
                    "auditing": "default",
                    "temperature": self.temperature,
                }
            },
            "payload": {
                "message": {
                    "text": question
                }
            }
        }
        return data

    def ask(self,question):
        websock = websocket.WebSocketApp(self.wsParam.create_url("GET"), on_message=self.on_message, on_error=self.on_error, on_close=self.on_close, on_open=self.on_open)
        websock.appid = self.appid
        websock.domain = self.domain
        websock.question = question
        websock.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
        return self.answer

    def get_Embedding(self, text):
        #embedding，暂不可用
        param_dict = {
            'header': {
                'app_id': self.appid
            },
            'payload': {
                'text': text
            }
        }
        response = requests.post(url=self.wsParam.create_url("POST"), json=param_dict)
        result = json.loads(response.content.decode('utf-8'))
        return result


if __name__ == "__main__":
    appid = ""     #填写控制台中获取的 APPID 信息
    api_secret = ""   #填写控制台中获取的 APISecret 信息
    api_key =""    #填写控制台中获取的 APIKey 信息
    domain = "generalv2"    # v2.0版本
    Spark_url = "ws://spark-api.xf-yun.com/v2.1/chat"  # v2.0环境的地址
    Spark = Spark_interface(appid=appid,api_secret=api_secret,api_key=api_key,domain=domain,Spark_url=Spark_url)
    cont = "宇宙中存在暗物质吗"
    question = [{'role':'user','content':cont}]
    res = Spark.ask(question)
    print(res)
    embed_url = "http://knowledge-retrieval.cn-huabei-1.xf-yun.com/v1/aiui/embedding/query"
    Spark = Spark_interface(appid=appid,api_secret=api_secret,api_key=api_key,domain=domain,Spark_url=embed_url)
    res = Spark.get_Embedding(cont)
    print(res)