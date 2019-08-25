# coding:utf-8
import redis
import pandas as pd
import time
import re
import multiprocessing
import math

import jieba
from jieba import analyse
analyse.set_stop_words('stopword.txt')
jieba.load_userdict('user_dict.txt')
# jieba.enable_parallel(8)

# 建立redis连接，分为文章和词汇库
r = redis.Redis(host='localhost' , port='6379' , db=4 ,decode_responses=True)
rword = redis.Redis(host='localhost' , port='6379' , db=3 ,decode_responses=True)

# 文章清洗规则，去除里面的标点符号
# 写入文章redis库
reg_clean = re.compile(r"[0-9\s+\.\!\/_,$%^*()?;；:-【】+\"\']+|[+——！，;:。？、~@#￥%……&*（）]+")
df = pd.read_csv('./article.csv')
ids = df['id']
content = df['content']

for index in range(len(ids)):
    try:
        current_content = reg_clean.sub(" ", content[index])
        r.hset('article_detail', str(ids[index]), current_content)
    except:
        pass



# 插入词库redis
def cut_word(content_list, id_list, index):
    for article, article_id in zip(content_list, id_list):
        try:
            tags = analyse.extract_tags(article, topK=20, withWeight=True)
            for word, frequency in tags:
                rword.zadd(word, article_id, frequency)
        except Exception as ex:
            continue
        finally:
            pass

ids = r.hkeys('article_detail')
content = [r.hget('article_detail', id) for id in ids]
each_num = math.ceil(len(ids) / multiprocessing.cpu_count())
id_list = [ids[each_num*i:each_num*(i+1)] for i in range(multiprocessing.cpu_count())]
content_list = [content[each_num*i:each_num*(i+1)] for i in range(multiprocessing.cpu_count())]

t0 = time.time()
process_list = []
for index, each_id in enumerate(id_list):
    process_list.append(multiprocessing.Process(target=cut_word, args=(content_list[index], each_id, index)))
for each in process_list:
    each.start()
for each in process_list:
    each.join()
print(time.time()-t0)
