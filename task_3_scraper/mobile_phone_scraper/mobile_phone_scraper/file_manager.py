import re
from mobile_phone_scraper.settings import RESULT
import os


class FileManager:
    ROOT_NAME_RAW_FILE = RESULT["root_name_raw_file"]
    EXTENSION_RAW_FILE = RESULT["extension_raw_file"]

    ROOT_NAME_OUT_FILE = RESULT["root_name_out_file"]
    EXTENSION_OUT_FILE = RESULT["extension_out_file"]

    SEPARATE_SYMBOL = RESULT["separate_symbol"]

    def get_next_name_raw_file(self) -> str:
        last_index = self._get_last_index_file_or_none(
            self.ROOT_NAME_RAW_FILE, self.EXTENSION_RAW_FILE
        )
        if last_index is None:
            return self._get_name_file(
                self.ROOT_NAME_RAW_FILE, self.EXTENSION_RAW_FILE, 0
            )
        return self._get_name_file(
            self.ROOT_NAME_RAW_FILE, self.EXTENSION_RAW_FILE, last_index + 1
        )

    def get_next_name_out_file(self) -> str:
        last_index_raw_file = self._get_last_index_file_or_none(
            self.ROOT_NAME_RAW_FILE, self.EXTENSION_RAW_FILE
        )
        return self._get_name_file(
            self.ROOT_NAME_OUT_FILE,
            self.EXTENSION_OUT_FILE,
            last_index_raw_file,
        )

    def get_last_name_raw_file(self) -> str:
        return self._get_last_file_or_none(
            self.ROOT_NAME_RAW_FILE, self.EXTENSION_RAW_FILE
        )

    def _get_name_file(
        self, root_name: str, extension: str, count: int
    ) -> str:
        return f"{root_name}{self.SEPARATE_SYMBOL}{count}.{extension}"

    def _get_last_file_or_none(self, root_name: str, extension: str) -> int:
        names_files = self._find_names(root_name, extension, "./")
        if len(names_files) == 0:
            return None
        names_files.sort(key=self._get_index_from_name)
        return names_files[-1]

    def _get_last_index_file_or_none(
        self, root_name: str, extension: str
    ) -> int:
        last_file = self._get_last_file_or_none(root_name, extension)
        if last_file is None:
            return None
        return self._get_index_from_name(last_file)

    def _find_names(self, root_name, extension, path):
        pattern_re = re.compile(
            rf"{root_name}{self.SEPARATE_SYMBOL}\d+\.{extension}"
        )
        result_files_names = []
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if pattern_re.match(file_name):
                    result_files_names.append(os.path.join(root, file_name))
        return result_files_names

    def _get_index_from_name(self, name) -> int:
        number_re = re.compile(r"\d+")
        number = number_re.findall(name)[0]
        return int(number)
