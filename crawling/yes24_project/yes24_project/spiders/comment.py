import scrapy
from scrapy.http import Request, Response

import requests
from bs4 import BeautifulSoup

import pandas as pd
import os
import time
import re
import csv


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36'}


def get_comments(cmt_page_url, book_url):
    res = requests.get(cmt_page_url, headers= headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    user_ids = []
    cmt_dates = []
    ratings = []

    cmts = soup.select('div.review_etc')
    for cmt in cmts:
        # User ID
        user_id = re.search(r'\d{6}', cmt.select_one('em.txt_id>a')['onclick']).group(0)
        user_ids.append(user_id)
        # cmt_date
        cmt_date = cmt.select_one('em.txt_date').text
        cmt_dates.append(cmt_date)
        # 평점
        rating = re.search(r'\d+', cmt.select_one('span.review_rating').text).group(0)
        ratings.append(rating)

    # cmt_url
    # cmt_urls = [e['href'] for e in soup.select('div.review_lnk>p>a')]
    # cmt_text
    cmt_texts = [e.text.strip().replace('\xa0', '') for e in soup.select('div.origin div.review_cont')]

    return list(zip([book_url]*len(cmts), user_ids, cmt_dates, ratings, cmt_texts))


class CommentSpider(scrapy.Spider):
    name = "comment"
    allowed_domains = ["www.yes24.com"]
    # start_urls = ["https://www.yes24.com/Product/communityModules/GoodsReviewList/110157236"]
    cmt_url = "https://www.yes24.com/Product/communityModules/GoodsReviewList/{}?goodsSetYn=N&Sort=2&PageNumber={}&DojungAfterBuy=1&Type=Purchase&_={}"


    def start_requests(self):
        # 모든 카테고리의 book url
        d_path = r"D:\python_project\chaekchecklab\data\basic"

        for f_name in os.listdir(d_path):
            # category_code
            category_code = f_name.split('.')[0]
            # print(category_code)
            
            # book list
            file_path = os.path.join(d_path, f_name)
            book_urls = pd.read_csv(file_path).url.to_list()
            # print(file_path, len(book_urls))

            for book_url in book_urls:
                yield Request(url=book_url, meta={"cate_code": category_code}, callback=self.parse)
                break
        return
    
    def parse(self, response: Response):
        book_url = f"https://www.yes24.com/Product/Goods/{response.url.split('/')[-1]}"

        comment_list = []
        p_idx = 1
        while True:
            epoch_time = int(time.time())
            comment_page_url = self.cmt_url.format(book_url, p_idx, epoch_time)
            # print(comment_page_url)

            comments = get_comments(comment_page_url, book_url)
            if not comments:
                break
            comment_list.extend(comments)
            p_idx += 1
        
        # print(comment_list)
        self.save_info(comment_list, ['book_url', 'user_ids', 'cmt_dates', 'ratings', 'cmt_texts'], response.meta['cate_code'])
        return

    def save_info(self, comment_list, columns, cate_code):
        # 결과를 출력하거나 저장
        df = pd.DataFrame(comment_list, columns=columns)
        full_path = os.path.join(r"D:/python_project/chaekchecklab/data/comment", f"comment_{cate_code}.csv")

        # 최초 생성 이후 mode는 append
        if not os.path.exists(full_path):
            df.to_csv(full_path, index=False, mode='w', quoting=csv.QUOTE_MINIMAL)
        else:
            df.to_csv(full_path, index=False, mode='a', header=False, quoting=csv.QUOTE_MINIMAL)
        return
