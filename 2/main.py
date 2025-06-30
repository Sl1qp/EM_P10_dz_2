import asyncio
import datetime
import aiohttp
import os
import requests
import database as db
import pandas as pd

from async_pars import get_ref
from urllib.parse import urlparse

folder_path = ".\\trades_file"
exclude_patterns = [
            "Итого",
            "Секция Биржи: «Нефтепродукты» АО «СПбМТСБ»",
            "Единица измерения: Метрическая тонна",
            "Итого по секции"
        ]
columns_mapping = {
    'Код\nИнструмента': 'exchange_product_id',
    'Наименование\nИнструмента': 'delivery_product_name',
    'Базис\nпоставки': 'delivery_basis_name',
    'Объем\nДоговоров\nв единицах\nизмерения': 'volume',
    'Обьем\nДоговоров,\nруб.': 'total',
    'Количество\nДоговоров,\nшт.': 'count'
}


def download_xls(url) -> str:
    parsed_url = urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    try:
        os.mkdir(folder_path)
    except Exception:
        pass

    response = requests.get(url, stream=True)
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "wb") as f:
        for i in response.iter_content(chunk_size=8192):
            f.write(i)
    print(f"\nФайл {file_path} сохранён!")
    return file_path


async def parse_data(page: int) -> list:
    trade_ref = []
    async with aiohttp.ClientSession() as session:
        ref = await get_ref(page, session)
        for date in ref:
            trade_ref.append(date)

    trade_ref.sort()
    return trade_ref


def main():
    engine, Session = db.get_engine_and_session()
    db.create_table(engine)

    stopper = 0
    for page in range(1, 389):
        table_urls = asyncio.run(parse_data(page))

        for table_url in table_urls:
            table_name = download_xls(f"https://spimex.com/{table_url}")
            if int(table_name[22:26]) <= 2023:
                print(f"Дата не соответствует - {table_name[22:26]} - {stopper}")
                os.remove(table_name)
                stopper += 1
                if stopper == 15:
                    return
                continue

            date = f"{table_name[28:30]}.{table_name[26:28]}.{table_name[22:26]}"
            trade_date = datetime.datetime.strptime(date, "%d.%m.%Y")

            try:
                td = pd.read_excel(table_name, engine="xlrd", skiprows=6, header=None)

                header_row = None
                for i, row in td.iterrows():
                    if any("Код\nИнструмента" in str(cell) for cell in row):
                        header_row = i
                        break

                if header_row is not None:
                    td.columns = td.iloc[header_row]
                    td = td.iloc[header_row + 1:]
                else:
                    print(f"Заголовки не найдены в файле {table_name}")
                    continue

                for column, new_column in columns_mapping.items():
                    if new_column in ["volume", "total", "count"]:
                        td[column] = td[column].replace('-', '0', regex=True)
                        td[column] = pd.to_numeric(td[column], errors='coerce')
                    else:
                        td[column] = td[column].astype(str).str.strip()
                os.remove(table_name)
            except Exception:
                print(f"Ошибка при считывании файла - {table_name}")
                continue


            filtered_td = td[td['Количество\nДоговоров,\nшт.'] > 0]

            with Session(bind=engine) as session:
                for index, row in filtered_td.iterrows():
                    if row['Код\nИнструмента'].startswith("Итого") or row['Код\nИнструмента'] == "nan":
                        continue
                    exchange_product_id = row['Код\nИнструмента']
                    exchange_product_name = row['Наименование\nИнструмента']
                    delivery_basis_name = row['Базис\nпоставки']
                    volume = row['Объем\nДоговоров\nв единицах\nизмерения']
                    total = row['Обьем\nДоговоров,\nруб.']
                    count = row['Количество\nДоговоров,\nшт.']

                    trade_obj = db.spimex_trading_results(
                        exchange_product_id=exchange_product_id,
                        exchange_product_name=exchange_product_name,
                        oil_id=exchange_product_id[:4],
                        delivery_basis_id=exchange_product_id[4:7],
                        delivery_basis_name=delivery_basis_name,
                        delivery_type_id=exchange_product_id[-1],
                        volume=float(volume),
                        total=int(total),
                        count=int(count),
                        date=trade_date,
                        created_on=datetime.datetime.now(),
                        updated_on=datetime.datetime.now()
                    )
                    db.insert_to_db(trade_obj, session)

                print("Успешно сохранено в бд!")


if "__main__" == __name__:
    main()
