import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
from HW_steam.HW_steam.items import HwSteamItem
import re

queries = ['minecraft', 'indie', 'strategies']
pages = [i for i in range(1, 3)]


def clean_text(rgx_list, text):
    new_text = text
    for rgx_match in rgx_list:
        new_text = re.sub(rgx_match, '', new_text)
    return new_text


class SteamspiderSpider(scrapy.Spider):
    name = 'SteamSpider'

    def start_requests(self):
        global page
        for query in queries:
            for page in pages:
                url = 'https://store.steampowered.com/search/?' + urlencode(
                    {'term': query, 'page': str(page)})
                yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        games = set()
        for res in response.xpath('//div[contains(@id, "search_resultsRows")]/a/@href').extract():
            games.add(res)

        for game in games:
            yield scrapy.Request(url=game, callback=self.parse)

        url = urlparse(response.url[-1]) + str(page)
        yield scrapy.Request(url=url, callback=self.parse_keyword_response)

    def parse(self, response):
        item = HwSteamItem()
        game_name = response.xpath('//div[contains(@class,"apphub_AppName")]/text()').extract()
        game_category = response.xpath('//div[contains(@class,"blockbg")]/a[2]/text()').extract()
        game_review_count = response.xpath(
            '//div[@class="user_reviews"]/div[@itemprop="aggregateRating"]//span[contains(@class,"responsive_hidden")]/text()').extract()
        game_score = response.xpath('//span[contains(@class,"game_review_summary positive")]/text()').extract()
        game_release_date = response.xpath('//div[contains(@class, "release_date")]/div[2]/text()').extract()
        game_developer = response.xpath('//div[@id="developers_list"]/a/text()').extract()
        game_tags = response.xpath('//div[contains(@class,"glance_tags popular_tags")]/a/text()').extract()
        game_price = response.xpath('//div[contains(@class ,"discount_final_price")]/text()').extract()
        game_platforms = response.xpath('//div[contains(@class, "game_area_purchase_platform")]/span').extract()

        if len(game_name) != 0:
            item['game_name'] = ''.join(game_name[0]).strip()

        item['game_category'] = ''.join(game_category).strip()

        item['game_review_count'] = ''.join(game_review_count).strip()
        item['game_review_count'] = item['game_review_count'][1:item['game_review_count'].find(')')]

        if len(game_score) != 0:
            item['game_score'] = ''.join(game_score[0]).strip()

        item['game_release_date'] = ''.join(game_release_date).strip()

        item['game_developer'] = ''.join(game_developer).strip()

        item['game_tags'] = ''.join(game_tags).strip().split()

        item['game_price'] = ''.join(game_price).strip()

        if item['game_price'] != '':
            item['game_price'] = item['game_price'][:item['game_price'].find(' ')] + ' RUB'

        item['game_platforms'] = sorted(list(
            set(map(lambda x: clean_text(['<span class="platform_img ', '</span>', '">'], x), game_platforms))),
            reverse=True)
        yield item
