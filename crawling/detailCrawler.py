import requests
from bs4 import BeautifulSoup

from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

import pandas as pd
import os, re, urllib, csv


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}

def get_detail_info(book_url):
    res = requests.get(book_url, headers= headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # 작가
    author_list = []

    author_links = [e['href'] for e in soup.select('span.moreAuthLiCont>ul>li>a')]
    if not author_links:
        author_links = [e['href'] for e in soup.select('span.gd_auth>a')]

    for author_link in author_links:
        author_name = re.search(r'author=(.+)$', author_link).group(1)
        if re.search(r'%..', author_name):
            author_name = urllib.parse.unquote(author_name).replace('+', ' ')
        try:
            author_code = re.search(r'authorNo=(\d+)', author_link).group(1)
            author_list.append([author_name, author_code])
        except AttributeError:
            # author_code = ''
            author_list.append([author_name])
    
    if not author_links:
        author_list = [e.text for e in soup.select('span.moreAuthLiCont>ul>li')]
        if not author_links:
            author_list = [e.text.strip() for e in soup.select('span.gd_auth')]
    # print(author_list)s


    # 품목 정보
    item_box = soup.select_one('tbody.b_size')
    item_infos = [e.text for e in item_box.select('td')]
    # print(item_infos)

    # Category
    cates = [e.text.strip().replace('\n>\n', ' > ') for e in soup.select('div#infoset_goodsCate li')]
    # print(cates)

    # 책 소개
    try:
        intro = soup.select_one('div.infoWrap_txtInner').text.strip()
    except AttributeError:
        intro = ""
    # print(intro)
    
    # break
    return [book_url, author_list, str(item_infos), str(cates), intro]


# for row in df.itertuples():
#     print(row.Index, row.book_url)
#     get_detail_info(row.book_url)


columns = ['book_url', 'author_list', 'item_infos', 'cates', 'intro']

basic_folder = r"D:\python_project\chaekchecklab\data\basic"
detail_folder = r"D:\python_project\chaekchecklab\data\detail"
basic_files = [f.split('_')[1] for f in os.listdir(basic_folder)]
detail_files = [f.split('_')[1] for f in os.listdir(detail_folder)]

file_set = set(basic_files) - set(detail_files)
cate_code_list = [s.split(".")[0] for s in file_set]

for cate_code in cate_code_list:
    file_path = os.path.join(basic_folder, f"basic_{cate_code}.csv")
    df = pd.read_csv(file_path)
    book_url_list = df.book_url.to_list()

    with ThreadPoolExecutor() as executor:
        results = list(tqdm(executor.map(get_detail_info, book_url_list), total=len(book_url_list)))

    df = pd.DataFrame(results, columns=columns)
    save_path = os.path.join(detail_folder, f"detail_{cate_code}.csv")

    # 최초 생성 이후 mode는 append
    if not os.path.exists(save_path):
        df.to_csv(save_path, index=False, mode='w', quoting=csv.QUOTE_MINIMAL)
    else:
        df.to_csv(save_path, index=False, mode='a', header=False, quoting=csv.QUOTE_MINIMAL)