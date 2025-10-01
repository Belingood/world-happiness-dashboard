import pandas as pd
import numpy as np
import os

# --- НАСТРОЙКИ СКРИПТА ---

# Имя исходного файла, который мы будем "портить"
SOURCE_FILENAME = 'WHR2024.csv'

# Имя файла, в который сохраним результат
OUTPUT_FILENAME = 'WHR2024_with_missing.csv'

# Список колонок, в которых будем создавать пропуски
COLUMNS_TO_CORRUPT = [
    'Social support',
    'Healthy life expectancy',
    'Generosity'
]

# Процент строк, которые мы хотим "испортить" в каждой колонке (от 0.0 до 1.0)
# 0.1 = 10% данных будут удалены
CORRUPTION_PERCENTAGE = 0.1


# --- ЛОГИКА СКРИПТА ---

def corrupt_csv(source_path, output_path, columns, percentage):
    """
    Читает CSV-файл, удаляет заданный процент данных в указанных колонках
    и сохраняет результат в новый файл.
    """
    print(f"[*] Загрузка исходного файла: {source_path}")
    if not os.path.exists(source_path):
        print(f"[!] Ошибка: Исходный файл не найден по пути: {source_path}")
        return

    df = pd.read_csv(source_path)

    print("[*] Начало процесса 'порчи' данных...")

    for col in columns:
        if col in df.columns:
            # Определяем количество значений для удаления
            n_to_remove = int(len(df) * percentage)

            # Получаем случайные индексы строк, которые не содержат пропусков
            valid_indices = df[col].dropna().index
            if len(valid_indices) < n_to_remove:
                print(f"[*] Внимание: В колонке '{col}' недостаточно данных для удаления {n_to_remove} значений.")
                n_to_remove = len(valid_indices)

            indices_to_remove = np.random.choice(valid_indices, n_to_remove, replace=False)

            # Заменяем значения на NaN (пропуск)
            df.loc[indices_to_remove, col] = np.nan
            print(f"    - В колонке '{col}' удалено {n_to_remove} значений.")
        else:
            print(f"[!] Внимание: Колонка '{col}' не найдена в файле.")

    # Сохраняем результат
    df.to_csv(output_path, index=False)
    print(f"\n[*] Готово! Испорченные данные сохранены в файл: {output_path}")


if __name__ == "__main__":
    # Определяем пути относительно местоположения скрипта
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_file_path = os.path.join(base_dir, 'data', SOURCE_FILENAME)
    output_file_path = os.path.join(base_dir, 'data', OUTPUT_FILENAME)

    corrupt_csv(source_file_path, output_file_path, COLUMNS_TO_CORRUPT, CORRUPTION_PERCENTAGE)
