# --- 1. IMPORT BIBLIOTEK ---
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
from thefuzz import process
import statsmodels.api as sm

# --- 2. KONFIGURACJA STRONY ---
st.set_page_config(page_title="Analiza World Happiness Report", page_icon="😊", layout="wide")


# --- 3. FUNKCJE POMOCNICZE ---
# Funkcja standardize_columns pozostaje bez zmian
def standardize_columns(dataframe):
    df_original = dataframe.copy()
    rename_map = {
        'Country': ['country'], 'Region': ['regional indicator'],
        'Happiness Score': ['happiness score', 'ladder score'], 'GDP per capita': ['gdp per capita'],
        'Social Support': ['social support'], 'Life Expectancy': ['healthy life expectancy'],
        'Freedom': ['freedom to make life choices'], 'Generosity': ['generosity'],
        'Corruption': ['perceptions of corruption']
    }
    df_clean = pd.DataFrame()
    processed_original_cols = set()
    for standard_name, keywords in rename_map.items():
        best_match_col = None
        for col_original in df_original.columns:
            if col_original in processed_original_cols: continue
            if col_original.lower().strip().startswith("explained by:"):
                col_clean = col_original.lower().replace('explained by: ', '').strip()
                if any(keyword in col_clean for keyword in keywords):
                    best_match_col = col_original
                    break
        if not best_match_col:
            for col_original in df_original.columns:
                if col_original in processed_original_cols: continue
                col_clean = col_original.lower().strip()
                if any(keyword in col_clean for keyword in keywords):
                    best_match_col = col_original
                    break
        if best_match_col:
            df_clean[standard_name] = df_original[best_match_col]
            processed_original_cols.add(best_match_col)
    for col in df_original.columns:
        if col not in processed_original_cols:
            df_clean[col] = df_original[col]
    return df_clean


@st.cache_data
def load_lookup_data():
    try:
        lookup_path = os.path.join('data', 'country_region_lookup.csv')
        df_lookup = pd.read_csv(lookup_path)
        df_lookup.dropna(subset=['region'], inplace=True)
        return df_lookup
    except FileNotFoundError:
        st.error("Plik referencyjny 'data/country_region_lookup.csv' nie został znaleziony!")
        return None


# --- 4. TYTUŁ I OPIS APLIKACJI ---
st.title('😊 Interaktywny Dashboard: Analiza Światowego Raportu Szczęścia')
st.write("Aplikacja do wizualizacji i analizy danych z raportu 'World Happiness Report'.")
st.markdown("---")

# --- 5. PRZESYŁANIE PLIKU ---
st.markdown("### Krok 1: Prześlij plik z danymi")
uploaded_file = st.file_uploader("Wybierz plik CSV", type="csv")

# Инициализация session_state при первой загрузке
if 'data_cleaned' not in st.session_state:
    st.session_state.data_cleaned = False

# Сброс состояния при загрузке нового файла
if uploaded_file and uploaded_file.name != st.session_state.get('last_file_name', ''):
    st.session_state.data_cleaned = False
    st.session_state.last_file_name = uploaded_file.name

if uploaded_file is not None:
    df_lookup = load_lookup_data()

    if df_lookup is not None:
        # --- ETAP 1: PRZETWARZANIE WSTĘPNE ---
        df_raw = pd.read_csv(uploaded_file)
        df_processed = standardize_columns(df_raw)

        canonical_names = df_lookup['canonical_name'].tolist()

        # Automatyczne mapowanie
        unmatched_countries = []
        mapping = {}
        for country in df_processed['Country'].dropna().unique():
            cleaned_name = country.replace('*', '').strip()
            match = process.extractOne(cleaned_name, canonical_names, score_cutoff=90)
            if match:
                mapping[country] = match[0]
            else:
                unmatched_countries.append(country)

        df_processed['canonical_name'] = df_processed['Country'].map(mapping)

        # --- ETAP 2: INTERAKTYWNE REWIZJA (JEŚLI POTRZEBNE) ---
        if unmatched_countries and not st.session_state.data_cleaned:
            with st.expander("⚠️ Przegląd Nierozpoznanych Krajów - Wymagana Akcja!", expanded=True):
                st.warning(
                    "Nie udało się automatycznie dopasować wszystkich krajów. Proszę, zweryfikuj poniższe propozycje.")

                user_choices = {}
                for country in unmatched_countries:
                    cleaned_name = country.replace('*', '').strip()
                    best_guesses = [guess[0] for guess in process.extract(cleaned_name, canonical_names, limit=3)]
                    options = best_guesses + ["(Pomiń / Pozostaw oryginalną nazwę)"]

                    user_choices[country] = st.selectbox(
                        f"Wybierz poprawne dopasowanie для **'{country}'**:",
                        options, index=0, key=f"select_{country}"
                    )

                if st.button("Zastosuj i zweryfikuj poprawki"):
                    # Budujemy finalne mapowanie
                    final_mapping = mapping.copy()
                    for original, choice in user_choices.items():
                        if choice != "(Pomiń / Pozostaw oryginalną nazwę)":
                            final_mapping[original] = choice

                    # --- НОВЫЙ БЛОК: ПРОВЕРКА НА КОНФЛИКТЫ ---
                    chosen_canonical_names = list(final_mapping.values())
                    counts = pd.Series(chosen_canonical_names).value_counts()
                    duplicates = counts[counts > 1]

                    if not duplicates.empty:
                        st.error(
                            "Wykryto konflikt! Kilka różnych krajów zostało zmapowanych do tej samej nazwy kanonicznej. Proszę poprawić swój wybór.")
                        for dup_name, count in duplicates.items():
                            conflicting_originals = [orig for orig, can in final_mapping.items() if can == dup_name]
                            st.write(
                                f"- Nazwa **'{dup_name}'** została wybrana dla: `{', '.join(conflicting_originals)}`")
                    else:
                        # Если конфликтов нет, применяем и сохраняем состояние
                        df_processed['canonical_name'] = df_processed['Country'].map(final_mapping)
                        st.session_state['data_cleaned'] = True
                        st.success("Poprawki zostały pomyślnie zastosowane! Brak konfliktów.")
                        st.rerun()  # Перезапускаем скрипт, чтобы скрыть этот блок и показать результаты

        else:  # Если все zmapowano автоматически или уже исправлено
            st.session_state.data_cleaned = True

        # --- ETAP 3: FINALIZACJA I WIZUALIZACJA (TYLKO GDY DANE SĄ GOTOWE) ---
        if st.session_state.data_cleaned:
            df_processed['canonical_name'].fillna(df_processed['Country'], inplace=True)

            if 'Region' in df_processed.columns:
                df_processed = df_processed.drop(columns=['Region'])

            df_enriched = pd.merge(df_processed, df_lookup, on='canonical_name', how='left')
            df_enriched['Country'] = df_enriched['canonical_name']
            df_enriched.rename(columns={'region': 'Region'}, inplace=True)
            df_enriched.drop(columns=['canonical_name'], inplace=True)
            df_enriched['Region'].fillna('Brak danych', inplace=True)

            if not unmatched_countries:  # Показываем сообщение только если не было ручного ревью
                st.success("Dane załadowane, przetworzone i gotowe do analizy!")

            df_processed = df_enriched

            st.header("Etap 2: Analiza Danych")
            st.subheader("Obsługa brakujących wartości")
            # ... (остальная часть кода без изменений) ...
            missing_values = df_processed.isnull().sum()
            missing_values = missing_values[missing_values > 0]
            if not missing_values.empty:
                st.warning("Wykryto brakujące dane! Tabela poniżej pokazuje problematyczne wpisy.")
                rows_with_missing = df_processed[df_processed.isnull().any(axis=1)]
                cols_with_missing = missing_values.index.tolist()
                if 'Country' in df_processed.columns and 'Country' not in cols_with_missing:
                    cols_with_missing.insert(0, 'Country')
                st.dataframe(rows_with_missing[cols_with_missing].reset_index(drop=True))
                strategy = st.radio("Wybierz strategię:",
                                    ('Uzupełnij medianą (zalecane)', 'Uzupełnij średnią', 'Usuń wiersze z brakami'))
                df_cleaned = df_processed.copy()
                for col in missing_values.index:
                    if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                        if strategy == 'Uzupełnij medianą (zalecane)':
                            df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)
                        elif strategy == 'Uzupełnij średnią':
                            df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)
                if strategy == 'Usuń wiersze z brakami': df_cleaned.dropna(inplace=True)
                st.success(f"Zastosowano strategię: **{strategy}**. Dane oczyszczone.")
            else:
                st.info("W danych nie znaleziono brakujących wartości.")
                df_cleaned = df_processed.copy()

            st.sidebar.header("Opcje filtrowania")
            if 'Region' in df_cleaned.columns and df_cleaned['Region'].nunique() > 1:
                all_regions = sorted([str(region) for region in df_cleaned['Region'].unique() if pd.notna(region)])
                selected_regions = st.sidebar.multiselect("Wybierz regiony:", options=all_regions, default=all_regions)
                df_filtered = df_cleaned[df_cleaned['Region'].isin(selected_regions)]
            else:
                df_filtered = df_cleaned

            st.subheader("Tabela danych")
            st.dataframe(df_filtered, height=400)

            st.subheader("Mapa wskaźnika szczęścia na świecie")
            fig_map = px.choropleth(df_filtered, locations='Country', locationmode='country names',
                                    color='Happiness Score', hover_name='Country',
                                    color_continuous_scale=px.colors.sequential.Plasma,
                                    title='Poziom szczęścia w poszczególnych krajach')
            st.plotly_chart(fig_map, use_container_width=True)

            st.subheader("Zależność poziomu szczęścia od PKB per capita")
            fig_scatter = px.scatter(df_filtered, x='GDP per capita', y='Happiness Score', hover_name='Country',
                                     title='Zależność wskaźnika szczęścia od PKB per capita', trendline='ols')
            st.plotly_chart(fig_scatter, use_container_width=True)

            st.subheader("Które czynniki są najważniejsze dla poczucia szczęścia?")
            numeric_cols = ['Happiness Score', 'GDP per capita', 'Social Support', 'Life Expectancy', 'Freedom',
                            'Generosity', 'Corruption']
            existing_cols = [col for col in numeric_cols if col in df_filtered.columns]
            if len(existing_cols) > 1:
                correlation_matrix = df_filtered[existing_cols].corr()
                fig_heatmap, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
                ax.set_title('Macierz korelacji czynników wpływających na szczęście')
                st.pyplot(fig_heatmap)
else:
    # Сброс состояния, если файл был выгружен
    if 'data_cleaned' in st.session_state:
        del st.session_state['data_cleaned']
    st.info("Proszę przesłać plik CSV, aby rozpocząć analizę.")

# Uruchomienie aplikacji z terminala: streamlit run app.py
