import os
import csv
import datetime

class FileManager:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_csv_data(self):
        """Read data from a CSV file and return it as a dictionary."""
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"CSV file '{self.file_path}' does not exist.")
        data_retrived = {}
        with open(self.file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for field in reader.fieldnames:
                data_retrived[field] = []
            for row in reader:
                for field in reader.fieldnames:
                    data_retrived[field].append(row[field])
        return data_retrived

    def write_csv_data(self, input_data):
        with open(self.file_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = list(input_data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            rows = [
                {key: input_data[key][i] for key in fieldnames}
                for i in range(len(next(iter(input_data.values()))))
            ]
            writer.writeheader()
            writer.writerows(rows)

    def merge_data(self, loaded_data, price='', product_name='', shop_name=''):
        """Extend loaded data by adding today's date and the given price.
        For other fields, append an empty string."""
        today = datetime.date.today().isoformat()
        for key in loaded_data:
            if key == "DATA":
                loaded_data[key].append(today)
            elif key == "CENA":
                loaded_data[key].append(price)
            elif key == "PRODUKT":
                loaded_data[key].append(product_name)
            elif key == "SKLEP":
                loaded_data[key].append(shop_name)
            else:
                loaded_data[key].append("")
        return loaded_data