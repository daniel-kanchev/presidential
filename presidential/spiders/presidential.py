import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from presidential.items import Article


class presidentialSpider(scrapy.Spider):
    name = 'presidential'
    start_urls = ['https://www.presidential.com/News/']

    def parse(self, response):
        links = response.xpath('//div[@class="leftnav"]/ul[1]/li/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//div[@class="leftnav"]/ul[2]/li/a/@href').getall()
        yield from response.follow_all(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@class="body-content"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        date = content.pop(1)
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
