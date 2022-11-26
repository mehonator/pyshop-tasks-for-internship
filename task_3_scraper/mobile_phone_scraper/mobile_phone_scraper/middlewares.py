# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html


import os
import signal
from importlib import import_module
from queue import Empty
from time import sleep, time
from multiprocess import Process, Queue

import undetected_chromedriver.v2 as uc
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import Chrome

from mobile_phone_scraper.spiders.mobile_spider import CustomSeleniumRequest
from mobile_phone_scraper.settings import UNDETECTED_CHROME_VERSION

TIME_OUT_SECONDS = 30
TRY_REQUEST = 5
SCROLL_PAUSE_TIME = 0.5
SLEEP_TIME_WAIT_COUNT_ELEMENTS = 3


class NotEnoughElements(Exception):
    pass


class BrowserFreeze(Exception):
    pass


class SeleniumGetProcess(Process):
    def __init__(
        self,
        driver_class,
        driver_kwargs,
        queue_request: Queue,
        queue_result_response: Queue,
        queue_pid_browser: Queue,
    ):
        self.driver_class = driver_class
        self.driver_kwargs = driver_kwargs
        self.queue_result = queue_result_response
        self.queue_request = queue_request
        self.queue_pid_browser = queue_pid_browser
        super().__init__()

    def run(self):
        self.driver: Chrome = self.driver_class(
            version_main=107, **self.driver_kwargs
        )
        self.queue_pid_browser.put(self.driver.browser_pid)
        while True:
            if self.queue_request.empty():
                continue

            request = None
            request = self.queue_request.get()

            if request:
                print('self.driver.get(request["url"])')
                self.driver.get(request["url"])

                self._scroll_down()

                if request["waiting_number_elements_by_xpath"]:
                    self._waiting_number_elements_by_xpath(
                        request["waiting_number_elements_by_xpath"]["xpath"],
                        request["waiting_number_elements_by_xpath"]["number"],
                    )

                for cookie_name, cookie_value in request["cookies_items"]:
                    self.driver.add_cookie(
                        {"name": cookie_name, "value": cookie_value}
                    )

                if request["wait_until"]:
                    WebDriverWait(self.driver, request["wait_until"]).until(
                        request["wait_until"]
                    )

                screenshot = None
                if request["screenshot"]:
                    screenshot = self.driver.get_screenshot_as_png()

                if request["script"]:
                    self.driver.execute_script(request.script)

                body = str.encode(self.driver.page_source)

                result_data = {
                    "response_data": {
                        "current_url": self.driver.current_url,
                        "body": body,
                        "encoding": "utf-8",
                    },
                    "request_data": {
                        "screenshot": screenshot,
                    },
                }
                self.queue_result.put(result_data)

    def _scroll_down(self):
        last_height = self.driver.execute_script(
            "return document.body.scrollHeight"
        )
        new_height = None
        while new_height != last_height:
            last_height = new_height
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            sleep(SCROLL_PAUSE_TIME)
            new_height = self.driver.execute_script(
                "return document.body.scrollHeight"
            )

    def _waiting_number_elements_by_xpath(self, xpath: str, number: int):
        length_elements = 0
        last_time = time()
        sleep(0.01)
        while (
            length_elements < number
            or time() - last_time < SLEEP_TIME_WAIT_COUNT_ELEMENTS
        ):
            length_elements = len(self.driver.find_elements(By.XPATH, xpath))
        if length_elements < number:
            raise NotEnoughElements


class CustomSeleniumMiddleware:
    def __init__(
        self,
        driver_name,
        driver_executable_path,
        driver_arguments,
        browser_executable_path,
    ):
        """Initialize the selenium webdriver

        Parameters
        ----------
        driver_name: str
            The selenium ``WebDriver`` to use
        driver_executable_path: str
            The path of the executable binary of the driver
        driver_arguments: list
            A list of arguments to initialize the driver
        browser_executable_path: str
            The path of the executable binary of the browser
        """

        webdriver_base_path = f"selenium.webdriver.{driver_name}"

        if driver_name == "undetected_chromedriver_chrome":
            driver_klass_module = import_module("undetected_chromedriver.v2")
            driver_options_module = import_module(
                "undetected_chromedriver._compat"
            )
            driver_options_klass = getattr(
                driver_options_module, "ChromeOptions"
            )
            self.driver_klass = driver_klass_module.Chrome
            driver_options = driver_options_klass()
            if browser_executable_path:
                driver_options.binary_location = browser_executable_path
            for argument in driver_arguments:
                driver_options.add_argument(argument)

            self.driver_kwargs = {
                "executable_path": driver_executable_path,
                f"{driver_name}_options": driver_options,
            }

        else:
            driver_klass_module = import_module(
                f"{webdriver_base_path}.webdriver"
            )
            self.driver_klass = getattr(driver_klass_module, "WebDriver")
            driver_options_module = import_module(
                f"{webdriver_base_path}.options"
            )
            driver_options_klass = getattr(driver_options_module, "Options")

            driver_options = driver_options_klass()
            if browser_executable_path:
                driver_options.binary_location = browser_executable_path
            for argument in driver_arguments:
                driver_options.add_argument(argument)

            self.driver_kwargs = {
                "executable_path": driver_executable_path,
                f"{driver_name}_options": driver_options,
            }
        self.driver: Chrome = uc.Chrome(
            version_main=UNDETECTED_CHROME_VERSION, **self.driver_kwargs
        )
        self.queue_result = Queue()
        self.queue_request = Queue()
        self.queue_pid_browser = Queue()
        self._set_driver_process()

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize the middleware with the crawler settings"""

        driver_name = crawler.settings.get("SELENIUM_DRIVER_NAME")
        driver_executable_path = crawler.settings.get(
            "SELENIUM_DRIVER_EXECUTABLE_PATH"
        )
        browser_executable_path = crawler.settings.get(
            "SELENIUM_BROWSER_EXECUTABLE_PATH"
        )
        driver_arguments = crawler.settings.get("SELENIUM_DRIVER_ARGUMENTS")

        if not driver_name or not driver_executable_path:
            raise NotConfigured(
                "SELENIUM_DRIVER_NAME and SELENIUM_DRIVER_EXECUTABLE_PATH must be set"
            )

        middleware = cls(
            driver_name=driver_name,
            driver_executable_path=driver_executable_path,
            driver_arguments=driver_arguments,
            browser_executable_path=browser_executable_path,
        )

        crawler.signals.connect(
            middleware.spider_closed, signals.spider_closed
        )

        return middleware

    def process_request(self, request, spider):
        """Process a request using the selenium driver if applicable"""

        if not isinstance(request, CustomSeleniumRequest):
            return None

        # sometimes the request freeze, start through multiprocessing
        result_data = self._freeze_resistant_get_request(request)
        self._update_request(request, result_data["request_data"])
        html_response = self._get_response(
            result_data["response_data"], request
        )
        return html_response

    def spider_closed(self):
        self._stop_driver_process()

    def _stop_driver_process(self):
        self.driver_process.kill()
        sleep(10)
        self.driver_process.close()
        os.kill(self.queue_pid_browser.get(), signal.SIGKILL)

    def _restart_driver(self):
        self._stop_driver_process()
        self._set_driver_process()

    def _get_request_data_for_multiprocessing(self, request) -> dict:
        cookies_items = [item for item in request.cookies.items()]
        data = {
            "url": request.url,
            "waiting_number_elements_by_xpath": request.waiting_number_elements_by_xpath,
            "cookies_items": cookies_items,
            "wait_time": request.wait_time,
            "screenshot": request.screenshot,
            "script": request.script,
            "wait_until": request.wait_until,
        }
        return data

    def _freeze_resistant_get_request(self, request) -> dict:
        request_data = self._get_request_data_for_multiprocessing(request)
        html_response_data = None
        for _ in range(TRY_REQUEST):
            while html_response_data is None:
                self.queue_request.put(request_data)
                try:
                    html_response_data = self.queue_result.get(
                        block=True, timeout=TIME_OUT_SECONDS
                    )
                except Empty:
                    self._restart_driver()
            if html_response_data is not None:
                return html_response_data

        if html_response_data is None:
            raise BrowserFreeze(
                f"не удаётся сделать запрос к {request.url}"
                "т.к. зависает на этом url"
            )

    def _update_request(self, request, request_data):
        if request_data["screenshot"]:
            request.meta["screenshot"] = request_data["screenshot"]

    def _get_response(self, response_data, request):
        return HtmlResponse(
            response_data["current_url"],
            body=response_data["body"],
            encoding=response_data["encoding"],
            request=request,
        )

    def _set_driver_process(self):
        self.driver_process = SeleniumGetProcess(
            self.driver_klass,
            self.driver_kwargs,
            self.queue_request,
            self.queue_result,
            self.queue_pid_browser,
        )
        self.driver_process.start()
