# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pandas as pd

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class Yes24ProjectPipeline:
    def process_item(self, item, spider):
        # df = pd.DataFrame(item)

        return item


