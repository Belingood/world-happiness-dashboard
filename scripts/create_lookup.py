import pandas as pd
import os

# --- НАСТРОЙКИ ---
# Получаем абсолютный путь к папке, где лежит сам скрипт
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Строим пути к папке 'data' и к выходному файлу
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
OUTPUT_FILE = os.path.join(DATA_DIR, 'country_region_lookup.csv')
# Файлы для поиска регионов, в порядке приоритета (самые надежные - первыми)
REGION_SOURCE_FILES = ['WHR2024.csv', 'WHR2023.csv', 'WHR2022.csv']

def clean_country_name(name):
    """Очищает название страны от звездочек и лишних пробелов."""
    if isinstance(name, str):
        return name.replace('*', '').strip()
    return name

print("[*] Запуск скрипта для создания справочника стран...")

# --- Шаг 1: Сбор всех уникальных и очищенных названий стран ---
all_countries = set()
print("[*] Шаг 1: Сбор всех уникальных названий стран...")
for filename in os.listdir(DATA_DIR):
    if filename.endswith('.csv') and filename.startswith('WHR'):
        print(f"    - Обработка файла: {filename}")
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, filename))
            country_col = next((col for col in ['Country', 'Country name'] if col in df.columns), None)
            if country_col:
                for country in df[country_col].dropna().unique():
                    all_countries.add(clean_country_name(country))
        except Exception as e:
            print(f"      [!] Ошибка при чтении файла {filename}: {e}")

# --- Шаг 2: Создание словаря регионов из приоритетных источников ---
region_lookup = {}
print("\n[*] Шаг 2: Поиск регионов в исходных файлах...")
for filename in REGION_SOURCE_FILES:
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        print(f"    - Поиск в источнике: {filename}")
        try:
            df = pd.read_csv(filepath)
            country_col = next((col for col in ['Country', 'Country name'] if col in df.columns), None)
            region_col = next((col for col in ['Regional indicator', 'Region'] if col in df.columns), None)

            if country_col and region_col:
                for index, row in df.iterrows():
                    country = clean_country_name(row[country_col])
                    region = row[region_col]
                    # Добавляем регион только если для этой страны его еще нет
                    if country not in region_lookup and pd.notna(region):
                        region_lookup[country] = region
        except Exception as e:
            print(f"      [!] Ошибка при чтении файла {filename}: {e}")

# --- Шаг 3: Создание и заполнение итогового справочника ---
print("\n[*] Шаг 3: Создание итогового файла справочника...")
sorted_countries = sorted(list(all_countries))
lookup_df = pd.DataFrame(sorted_countries, columns=['canonical_name'])

# Применяем наш словарь для автоматического заполнения
lookup_df['region'] = lookup_df['canonical_name'].map(region_lookup)

# Сохраняем результат
lookup_df.to_csv(OUTPUT_FILE, index=False)

# --- Шаг 4: Отчет о проделанной работе ---
countries_with_region = lookup_df['region'].notna().sum()
countries_without_region = lookup_df['region'].isna().sum()
print(f"\n[*] Готово! Справочник сохранен в: {os.path.abspath(OUTPUT_FILE)}")
print(f"[*] Всего уникальных стран: {len(lookup_df)}")
print(f"[*] Автоматически заполнено регионов: {countries_with_region}")
print(f"[*] Требуется заполнить вручную: {countries_without_region}")

if countries_without_region > 0:
    missing_list = lookup_df[lookup_df['region'].isna()]['canonical_name'].tolist()
    print("\n[!] ПОЖАЛУЙСТА, ОТКРОЙТЕ ФАЙЛ И ЗАПОЛНИТЕ РЕГИОНЫ ДЛЯ СЛЕДУЮЩИХ СТРАН:")
    for country in missing_list:
        print(f"    - {country}")
