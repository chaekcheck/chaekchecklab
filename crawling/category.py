import requests
from bs4 import BeautifulSoup

import pandas as pd
import pickle
import copy


cate1_text = """
- 경제 경영: https://www.yes24.com/24/Category/Display/001001025
- 건강 취미: https://www.yes24.com/24/Category/Display/001001011
- 사회 정치: https://www.yes24.com/24/Category/Display/001001022
- 소설 시 희곡: https://www.yes24.com/24/Category/Display/001001046
- 에세이: https://www.yes24.com/24/Category/Display/001001047
- 역사: https://www.yes24.com/24/Category/Display/001001010
- 예술: https://www.yes24.com/24/Category/Display/001001007
- 인문: https://www.yes24.com/24/Category/Display/001001019
- 자기계발: https://www.yes24.com/24/Category/Display/001001026
- 자연과학: https://www.yes24.com/24/Category/Display/001001002
- 어린이 문학(그래픽노블): https://www.yes24.com/24/Category/Display/001001016001
"""
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}
basic_url = "https://www.yes24.com"


cate_all = {}

cate_1 = dict()
for line in cate1_text.strip().split('\n'):
    k, v = line.split(": ")
    k = k[2:]
    cate_1[k] = v

cate_all.update(cate_1)

before_cate = cate_1

idx = 1
while True:
    print(idx)
    new_cate = {}
    for cate_name, cate_url in before_cate.items():
        # print(cate_name, cate_url)
        res = requests.get(cate_url, headers= headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        box = soup.select_one('div#cateSubListWrap')
        try:
            new_cate.update({f"{cate_name} > {c.text}": basic_url+c['href'] for c in box.select('dt>a')})
        except AttributeError:
            pass
    if len(new_cate) == 0:
        break

    cate_all.update(new_cate)
    before_cate = copy.deepcopy(new_cate)
    idx += 1


with open('category_all.pickle', 'wb') as fw:
    pickle.dump(cate_all, fw)

# with open('cate2.pickle', 'rb') as fr:
#     cate2 = pickle.load(fr)