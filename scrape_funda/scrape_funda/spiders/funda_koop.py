import scrapy
import json
from bs4 import BeautifulSoup


class FundaSpider(scrapy.Spider):
    name = "funda_koop"


    def start_requests(self):
        urls = [
#            "https://www.funda.nl/en/koop/1072am/beschikbaar/65-80-woonopp/2+slaapkamers/+5km/sorteer-datum-af/",
#            "https://www.funda.nl/en/koop/amsterdam/beschikbaar/0-800000/60+woonopp/3-dagen/sorteer-datum-af/",  # 3 days
            "https://www.funda.nl/en/koop/amsterdam/beschikbaar/0-800000/60+woonopp/sorteer-datum-af/"
        ]
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)


    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        for item in soup.find_all("li", "search-result"):
            relative_url = item.find("a", attrs={"data-object-url-tracking": "resultlist"})["href"]
            url = response.urljoin(relative_url)
            print(f"::::::: NEW URL: {url}")
            yield scrapy.Request(url, callback=self.parse_item)

        next_page = soup.find('a', attrs={'rel': 'next'})
        if next_page:
            next_page = response.urljoin(next_page["href"])
            yield scrapy.Request(next_page, callback=self.parse)

    def _get_feature(self, soup, feature_name):
        feature = soup.find("section", "object-kenmerken").find("dt", text=feature_name)
        if feature:
            return feature.find_next("span").text
        return None


    def parse_item(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        json_data = json.loads(soup.find_all('script', type='application/ld+json')[-1].string)
        yield {
            "url": response.url,
            "address": soup.find("span", "object-header__title").text,
            "postcode": json_data.get("postcode"),
            "city": json_data.get("plaats"),
            "neighbourhood": json_data.get("buurt"),
            "price": json_data.get("vraagprijs"),
            "rooms": json_data.get("aantalkamers"),
            "construction_year": json_data.get("bouwjaar"),
            "energy_label": json_data.get("energieklasse"),
            "sqm": json_data.get("woonoppervlakte"),
            "erfpacht": json_data.get("erfpacht"),
            "cvketel": json_data.get("cvketel"),
            "terrace": json_data.get("dakterras"),
            "garden": json_data.get("tuin"),
            "balcony": json_data.get("balkon"),
            "listed_since": self._get_feature(soup, "Listed since"),
            "expenses": self._get_feature(soup, "VVE (Owners Association) contribution"),
            "located_at": self._get_feature(soup, "Located at"),
        }

