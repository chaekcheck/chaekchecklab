import scrapy
from scrapy.http import Request

import os
import pandas as pd
import csv
import re
import urllib

class DetailSpider(scrapy.Spider):
    name = "detail"
    allowed_domains = ["www.yes24.com"]
    # start_urls = ["https://www.yes24.com/Product/Goods/390811", "https://www.yes24.com/Product/Goods/3487710", "https://www.yes24.com/Product/Goods/3507854", "https://www.yes24.com/Product/Goods/3618840", "https://www.yes24.com/Product/Goods/3601572", "https://www.yes24.com/Product/Goods/133213071"]

    def start_requests(self):
        # 모든 카테고리의 book url 가져오기
        d_path = r"D:\python_project\chaekchecklab\data\basic"

        # ^^^ for test
        for f_name in os.listdir(d_path):
            # category_code
            category_code = f_name.split('.')[0]
            print(r"Category: {category_code}")
            
            # book list
            file_path = os.path.join(d_path, f_name)
            book_urls = pd.read_csv(file_path).book_url.to_list()
            # print(file_path, len(book_urls))

            # ^^^ for test
            for book_url in book_urls:
                yield Request(url=book_url, meta={"cate_code": category_code}, callback=self.parse)


    def parse(self, response):
        # self.logger.info(f'Get detail information in {response.url}')
        print(f'Get detail information in {response.url}')

        # 작가
        author_list = []

        author_links = response.css('span.moreAuthLiCont>ul>li>a::attr(href)').getall()
        if not author_links:
            author_links = response.css('span.gd_auth>a::attr(href)').getall()
        # print(author_links)

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
            author_list = response.css('span.moreAuthLiCont>ul>li>::text').getall()
            if not author_links:
                author_list = [response.css('span.gd_auth::text').get().strip()]
        # print(author_list)

        # 품목 정보
        item_box = response.css('tbody.b_size')
        item_infos = [e.css('::text').get().strip() for e in item_box.css('td')]
        # print(item_infos)

        # Category
        cates = []
        for e in response.css('div#infoset_goodsCate li'):
            texts = [e.strip() for e in e.css('::text').getall()]
            cates.append("".join(texts))
        # print(cates)

        # 책 소개
        intro = "".join(response.css('div.infoWrap_txtInner > textarea')[0].css(' ::text').getall()).strip()

        # 저장
        self.save_info([[response.url, author_list, str(item_infos), str(cates), intro]], ['book_url', 'author_list', 'item_infos', 'cates', 'intro'], response.meta['cate_code'])

    def save_info(self, detail_info_list, columns, cate_code):
        # print(detail_info_list)
        df = pd.DataFrame(detail_info_list, columns=columns)
        full_path = os.path.join(r"D:/python_project/chaekchecklab/data/detail", f"detail_{cate_code}.csv")

        # 최초 생성 이후 mode는 append
        if not os.path.exists(full_path):
            df.to_csv(full_path, index=False, mode='w', quoting=csv.QUOTE_MINIMAL)
        else:
            df.to_csv(full_path, index=False, mode='a', header=False, quoting=csv.QUOTE_MINIMAL)

        print(f"Saved in detail_{cate_code}.csv")
        return