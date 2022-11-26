import os
from scrapy.cmdline import execute
from mobile_phone_scraper.file_manager import FileManager


os.chdir(os.path.dirname(os.path.realpath(__file__)))


def main():
    file_manager = FileManager()
    name_raw_file = file_manager.get_next_name_raw_file()

    try:
        execute(
            [
                "scrapy",
                "crawl",
                "mobile_spider",
                "-a",
                "required_count_phones=100",
                "-o",
                name_raw_file,
            ]
        )

    except SystemExit as e:
        print(e)


if __name__ == "__main__":
    main()
