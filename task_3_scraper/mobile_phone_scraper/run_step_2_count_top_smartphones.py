import pandas as pd

from mobile_phone_scraper.file_manager import FileManager


def count_top_os(input_file_name: str, output_file_name: str):
    df_phones = pd.read_json(input_file_name)
    df_agr_os = (
        df_phones.groupby(["operating_system_version"])
        .size()
        .reset_index(name="counts")
    )
    df_agr_os_sort_count = df_agr_os.sort_values(
        by=["counts"], ascending=False
    )
    df_agr_os_sort_count.to_csv(
        f"./{output_file_name}", header=None, index=None, sep=" ", mode="w"
    )


def main():
    file_manager = FileManager()
    print("Запуск рассчёта топа ОС смартфонов")
    count_top_os(
        input_file_name=file_manager.get_last_name_raw_file(),
        output_file_name=file_manager.get_next_name_out_file(),
    )
    print("Рассчёт завершен")


if __name__ == "__main__":
    main()
