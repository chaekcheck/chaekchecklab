import scrapy
from scrapy.http import Request

import pickle
import pandas as pd
import os
import re
import csv


class BasicSpider(scrapy.Spider):
    name = "basic"
    allowed_domains = ["www.yes24.com"]
    # start_urls = ["https://www.yes24.com/24/Category/Display/001001025007"]

    def start_requests(self):
        with open('D:/python_project/chaekchecklab/data/category/category_eb.pickle', 'rb') as fr:
            category = pickle.load(fr)
        
        for cate_name, cate_url in category.items():
            cate_code = cate_url.split('/')[-1]
            print(f"{cate_name} 시작합니다.")
            print(f"{cate_url}")
            yield Request(url=cate_url, meta={"cate_name": cate_name, "cate_code": cate_code}, callback=self.pagenate)
            
            # ^^^ for test
            # break

    def pagenate(self, response):
        last_page_link = response.css('div.yesUI_pagenS > a.end::attr(href)').get()
        max_page_num = int(re.search(r'\d+$', last_page_link).group(0))
        print(f"총 {max_page_num} 페이지")
        
        # ^^^ for test
        # max_page_num = 2

        for i in range(1, max_page_num+1):
            cate_page_url = response.url + f"?PageNumber={i}"
            yield Request(url=cate_page_url, meta=response.meta, callback=self.parse)
        return

    def parse(self, response):
        # self.logger.info(f'Get basic information in {response.url}')
        print(f'Get basic information in {response.url}')
        
        # 상품 박스 선택
        boxes = response.css('div.cCont_goodsSet')
        # print(boxes)

        basic_info_list = []
        for box in boxes:
            # title box
            name_box = box.css('div.goods_name')
            # title, url
            title_box = name_box.css('a')
            title_text = title_box.css('::text').get().strip()
            book_url = response.urljoin(title_box.attrib['href'])
            # full_name
            name_front = name_box.css('span.gd_nameF::text').get(default='')
            name_end = name_box.css('span.gd_nameE::text').get(default='')
            name_feature = name_box.css('span.gd_feature::text').get(default='')
            full_name = ' '.join(filter(None, [name_front, title_text, name_end, name_feature]))
            # pub_box
            pub_box = box.css('div.goods_pubGrp')
            authors = "".join(pub_box.css('span.goods_auth ::text').getall()).strip()
            # print(authors)
            publisher = pub_box.css('span.goods_pub::text').get(default='')
            # 기본 정보 리스트에 추가
            basic_info_list.append({
                'title': title_text,
                'full_name': full_name,
                'book_url': book_url,
                'authors': authors,
                'publisher': publisher
            })
        # self.save_info(basic_info_list, ['title', 'full_name', 'book_url', 'authors', 'publisher'], '001001025007')
        print(f"Saving {response.meta['cate_name']}")
        self.save_info(basic_info_list, ['title', 'full_name', 'book_url', 'authors', 'publisher'], response.meta['cate_code'])

    def save_info(self, basic_info_list, columns, cate_code):
        # 결과를 출력하거나 저장
        df = pd.DataFrame(basic_info_list, columns=columns)
        full_path = os.path.join(r"D:/python_project/chaekchecklab/data/basic", f"basic_{cate_code}.csv")

        # 최초 생성 이후 mode는 append
        if not os.path.exists(full_path):
            df.to_csv(full_path, index=False, mode='w', quoting=csv.QUOTE_MINIMAL)
        else:
            df.to_csv(full_path, index=False, mode='a', header=False, quoting=csv.QUOTE_MINIMAL)

        print(f"Saved in basic_{cate_code}.csv")
        return