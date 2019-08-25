import pandas as pd
import json
import re
from tqdm import tqdm

reg = re.compile('<.*?>')
json_list = []
for i in tqdm(range(1, 11)):
#for i in tqdm(range(1, 100)):
    try:
        with open('article/{}.json'.format(str(i))) as fp:
            js = json.load(fp)
        json_list.append(js)
    except Exception as ex:
        continue

df = pd.DataFrame(json_list)

df = df[['id', 'url', 'content']]
df['content'] = df['content'].apply(lambda x: reg.sub("", x))
mask = df['content'].apply(lambda x: len(str(x))>=100)
df = df[mask]

df.to_csv('article.csv')
