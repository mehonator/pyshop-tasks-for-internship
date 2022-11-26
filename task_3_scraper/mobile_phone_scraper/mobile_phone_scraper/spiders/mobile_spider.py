from scrapy.exceptions import CloseSpider
from scrapy.spiders import Spider
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from mobile_phone_scraper.items import MobilePhoneScraperItem

domain_ozon = "www.ozon.ru"


class ExceptionRequestRetriesExceeded(Exception):
    pass


class CustomSeleniumRequest(SeleniumRequest):
    def __init__(
        self,
        wait_time=None,
        wait_until=None,
        screenshot=False,
        script=None,
        waiting_number_elements_by_xpath=None,
        *args,
        **kwargs,
    ):
        self.waiting_number_elements_by_xpath = (
            waiting_number_elements_by_xpath
        )
        super().__init__(
            wait_time, wait_until, screenshot, script, *args, **kwargs
        )


class MobileSpiderSpider(Spider):
    name = "mobile_spider"
    allowed_domains = ["www.ozon.ru"]
    start_urls = [
        "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/?sorting=rating&type=49659"
    ]

    current_count_phones = 0
    current_page = 1
    TRY_REQUEST = 3
    WAIT_TIME_SECONDS = 20
    COUNT_PHONES_IN_PAGE = 30
    XPATH_WAIT_PAGE_PHONES = "//span[contains(@class,'tsBodyL')]"

    def __init__(self, required_count_phones=100, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.REQUIRED_COUNT_PHONES = int(required_count_phones)

    def url_next_page_generator(self):
        self.current_page += 1
        return (
            "https://www.ozon.ru/category/telefony-i-smart-chasy-15501/"
            f"?page={self.current_page}&sorting=rating&type=49659"
        )

    def start_requests(self):
        for url in self.start_urls:
            print("procesing:" + url)
            yield CustomSeleniumRequest(
                url=url,
                callback=self.parse_page,
                waiting_number_elements_by_xpath={
                    "xpath": self.XPATH_WAIT_PAGE_PHONES,
                    "number": self.COUNT_PHONES_IN_PAGE,
                },
            )

    def parse_phone(self, response):
        mob_item = MobilePhoneScraperItem()
        os_version_or_none = response.xpath(
            "//dl//span[contains(text(), 'Версия')]/../../dd/text()"
        ).get()

        if not os_version_or_none:
            os_version_or_none = response.xpath(
                "//dl//span[contains(text(), 'Версия')]/../../dd/a/text()"
            ).get()
        mob_item["operating_system_version"] = os_version_or_none
        mob_item["name"] = response.xpath(
            "//div[@data-widget='webProductHeading']/h1/text()"
        ).get()
        mob_item["url"] = response.url

        self.current_count_phones += 1
        if self.current_count_phones > self.REQUIRED_COUNT_PHONES:
            raise CloseSpider("scraped enough phones")
        return mob_item

    def parse_page(self, response):
        hrefs_cards = response.css(".tile-hover-target")
        urls_phones = [i.attrib["href"] for i in hrefs_cards]
        urls_phones = list(set(urls_phones))
        for url_phone in urls_phones:
            abs_url = response.urljoin(url_phone)

            yield CustomSeleniumRequest(
                url=abs_url,
                callback=self.parse_phone,
                # wait_time=self.WAIT_TIME_SECONDS,
                # wait_until=EC.element_to_be_clickable(
                #     (By.XPATH, "//div[contains(text(), 'Общие')]")
                # ),
            )

        yield CustomSeleniumRequest(
            url=self.url_next_page_generator(),
            callback=self.parse_page,
            waiting_number_elements_by_xpath={
                "xpath": self.XPATH_WAIT_PAGE_PHONES,
                "number": self.COUNT_PHONES_IN_PAGE,
            },
        )
