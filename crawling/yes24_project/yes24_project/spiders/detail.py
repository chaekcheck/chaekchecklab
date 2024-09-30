import scrapy
from scrapy.http import Request

import os
import pandas as pd
import csv

class DetailSpider(scrapy.Spider):
    name = "detail"
    allowed_domains = ["www.yes24.com"]
    # start_urls = ["https://www.yes24.com/Product/Goods/110157236"]

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
            break


    def parse(self, response):
        self.logger.info(f'Get basic information in {response.url}')
        print(f'Get basic information in {response.url}')

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
        intro = response.css('div.infoWrap_txtInner textarea::text').get(default='').strip()
        # print(intro)

        self.save_info([[response.url, str(item_infos), str(cates), intro]], ['book_url', 'item_infos', 'cates', 'intro'], response.meta['cate_code'])

    def save_info(self, detail_info_list, columns, cate_code):
        # print(detail_info_list)
        df = pd.DataFrame(detail_info_list, columns=columns)
        full_path = os.path.join(r"D:/python_project/chaekchecklab/data/detail", f"detail_{cate_code}.csv")

        # 최초 생성 이후 mode는 append
        if not os.path.exists(full_path):
            df.to_csv(full_path, index=False, mode='w', quoting=csv.QUOTE_MINIMAL)
        else:
            df.to_csv(full_path, index=False, mode='a', header=False, quoting=csv.QUOTE_MINIMAL)

        return