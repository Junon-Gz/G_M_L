import gradio as gr
import os

from utils.model import Openai,SparkAPI_offical
from utils.db.mivils import mivils
from utils.log.dailylog import Logger
logger =Logger(os.getcwd()+'/log/acc.log',level='debug').logger
from config import common_config
conf  = common_config()


mivils_obj = mivils(host=conf.milivus_conf['host'],port=conf.milivus_conf['port'])

def get_db_res(db_obj:mivils,db_name,vect,fields:list,anns_field,limit):
    '''
    ### 向量数据库search函数。\n
    参数:
    - db_obj：数据库对象。\n
    - vect：向量。\n
    - fields：需要查询的字段。\n
    - anns_field：向量字段。\n
    - limit: search返回数量。\n
    '''
    db_obj.connect_to_collection(db_name)
    search_params={
        "metric_type": "L2"
    }
    db_res = db_obj.Search(
            data=[vect],  # Embeded search value
            anns_field=anns_field,  # Search across embeddings
            param=search_params,
            limit=limit,  # Limit to five results per search
            output_fields=fields  # Include title field in result
        )
    return db_res

def check_messages_length(message,question):
    message += (
        "指令: 使用给定的搜索结果编写对查询的全面答复 。"
        "使用[页码]符号引用每个引用（每个结果的开头都有这个数字）。"
        "引文应该在每句话的末尾进行。如果搜索结果提到多个同名主题，请为每个主题创建单独的答案 。"
        "只包括结果中的信息，不添加任何其他信息 。 "
        "确保答案正确，不要输出虚假内容 。"
        "如果文本与查询无关，请以你根据你所学习的知识进行回答 。"
        "忽略与问题无关的异常值搜索结果 。只回答问题 。  "
        "答案应该简明扼要 。 逐步回答 。 \n\n查询: {question}\n回答: "
        )
    message += f"查询: {question}\n回答:"
    prompt = [{"role": "system", "content": "现在你是一个非常擅长学习搜索结果的客服机器人,你总是学习搜索结果内容并根据学习结果编写全面答复."},
            {"role": "user", "content": message}]
    length = Openai.num_tokens_from_messages(prompt)
    return length

def get_prompt(question,topn_chunks:list):
    '''
    ### 提示词生成函数。 \n
    参数:
    - question：用户提问内容。\n
    - topn_chunks：数据库匹配结果。\n
    '''
    prompt = ""
    prompt += '搜索结果:\n\n'
    #遍历向量数据库匹配内容
    for c in topn_chunks:
        length = check_messages_length(prompt + c + '\n\n',question)
        if  length < 4097:
            prompt += c + '\n\n'
        else:
            #切割符合长度跳出循环
            prompt = prompt+ c[:length-4097] + '\n\n'
            break

    prompt += (
        "指令: 使用给定的搜索结果编写对查询的全面答复 。"
        "使用[页码]符号引用每个引用（每个结果的开头都有这个数字）。"
        "引文应该在每句话的末尾进行。如果搜索结果提到多个同名主题，请为每个主题创建单独的答案 。"
        "只包括结果中的信息，不添加任何其他信息 。 "
        "确保答案正确，不要输出虚假内容 。"
        "如果文本与查询无关，请以你根据你所学习的只是进行回答 。"
        "忽略与问题无关的异常值搜索结果 。只回答问题 。  "
        "答案应该简明扼要 。 逐步回答 。 \n\n查询: {question}\n回答: "
    )

    prompt += f"查询: {question}\n回答:"
    return prompt

def get_model_res(question,chunks)->str:
    '''
    ### 请求模型获取答案函数。\n
    参数：
    - question:用户提问内容。\n
    - db_obj:数据库对象。\n
    '''
    prompt = get_prompt(question,chunks)
    logger.info(f"提问内容:\n{prompt}")
    answer = Openai.get_completion(prompt,temperature=0.1)
    # BUG:spark模型调用返回回复内容为空(疑似没有等待回复)
    # Spark = SparkAPI_offical.Spark_interface(appid=conf.spark_conf['appid'],api_secret=conf.spark_conf['api_secret'],api_key=conf.spark_conf['api_key'],domain=conf.spark_conf['domain'],Spark_url=conf.spark_conf['Spark_url'],temperature=conf.spark_conf['temperature'],max_tokens=conf.spark_conf['max_tokens'])
    # answer = Spark.ask([{'role':'user','content':prompt}])
    logger.info(f"回答内容:{answer}")
    return answer

def get_ans(question,request:gr.Request):
    '''
    ### gradio绑定函数。\n
    参数：
    - question:用户提问内容。\n
    - request:gradio默认请求对象。\n
    '''
    host = request.client.host
    logger.info(f"收到[{host}]用户提问：{question}")
    q_vec = Openai.get_vector(question)
    db_res = get_db_res(mivils_obj,"elc_answer_db",q_vec,fields=['id','title','answer'],anns_field='answer_vec',limit=10)
    logger.info(f"答案库匹配项：{','.join([str(hit.id) for hit in db_res[0]])}")
    chunks = []
    for hit in db_res[0]:
        # logger.info(f"{hit.id},{1-hit.score},{hit.entity.get('title')},{hit.entity.get('answer')}")
        chunks.append(f"{hit.id}.{hit.entity.get('answer')}")
    # db_res1 = get_db_res(mivils_obj,"elc_question_db",q_vec,fields=['id','title','answer'],anns_field='title_vec',limit=10)
    # logger.info("问题库匹配项：")
    # for hit in db_res1[0]:
    #     logger.info(f"{hit.id},{1-hit.score},{hit.entity.get('title')},{hit.entity.get('answer')}")
    model_answer = get_model_res(question,chunks)
    return model_answer,\
        gr.update(label=db_res[0][0].entity.get('title'),open=False,visible=True),gr.update(value=db_res[0][0].entity.get('answer')),\
        gr.update(label=db_res[0][1].entity.get('title'),open=False,visible=True),gr.update(value=db_res[0][1].entity.get('answer')),\
        gr.update(label=db_res[0][2].entity.get('title'),open=False,visible=True),gr.update(value=db_res[0][2].entity.get('answer')),\
        gr.update(label=db_res[0][3].entity.get('title'),open=False,visible=True),gr.update(value=db_res[0][3].entity.get('answer')),\
        gr.update(open=True)