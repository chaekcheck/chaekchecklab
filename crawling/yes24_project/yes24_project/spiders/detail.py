import scrapy


class DetailSpider(scrapy.Spider):
    name = "detail"
    allowed_domains = ["www.yes24.com"]
    start_urls = ["https://www.yes24.com/Product/Goods/110157236"]

    def parse(self, response):
        # 품목 정보
        item_box = response.css('tbody.b_size')
        item_infos = [e.css('::text').get().strip() for e in item_box.css('td')]
        # print(item_infos)

        # Category
        cates = []
        for e in response.css('div#infoset_goodsCate li'):
            texts = [e.strip() for e in e.css('::text').getall()]
            cates.append("".join(texts))
        print(cates)

        # 책 소개
        intro = response.css('div.infoWrap_txtInner::text')
        # print(intro)
