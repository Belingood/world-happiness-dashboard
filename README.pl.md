# World Happiness Report - Interaktywny Dashboard

![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50-FF4B4B.svg?style=flat&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.3-150458.svg?style=flat&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-6.3-3F4F75.svg?style=flat&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

Interaktywna aplikacja webowa zbudowana przy użyciu Streamlit, przeznaczona do eksploracji, czyszczenia i analizy danych z corocznego Światowego Raportu Szczęścia (World Happiness Report). Projekt demonstruje kompletny potok przetwarzania danych, od surowych danych wejściowych po zautomatyzowane wnioski analityczne.

---

## Demo

<!-- 
    WSKAZÓWKA: Zrób zrzut ekranu lub krótką animację GIF działającej aplikacji i umieść ją tutaj.
    To sprawi, że plik README będzie wyglądał 10 razy lepiej!
    Przykład: ![Demo Aplikacji](demo.gif)
-->

## Funkcjonalności

-   **Solidny Potok Przetwarzania Danych:**
    -   📂 **Dynamiczne Przesyłanie Plików:** Obsługa różnych formatów raportów rocznych (2022-2024).
    -   ✨ **Standaryzacja Kolumn:** Automatyczna normalizacja niespójnych nazw kolumn.
    -   🌍 **Wzbogacanie Danych:** Uzupełnianie brakujących informacji o regionach na podstawie centralnego pliku referencyjnego.
    -   🤝 **Inteligentne Dopasowywanie Nazw:** Wykorzystuje dopasowanie przybliżone (fuzzy matching) do rozwiązywania problemu niespójnych nazw krajów (np. `Turkey` vs. `Turkiye`) i umożliwia ręczną korektę.
    -   ⚠️ **Wykrywanie Konfliktów:** Zapobiega mapowaniu wielu różnych krajów źródłowych do tej samej nazwy kanonicznej.
    -   🧹 **Imputacja Brakujących Wartości:** Umożliwia użytkownikowi wybór strategii (mediana, średnia lub usunięcie wierszy) do obsługi brakujących danych numerycznych.

-   **Interaktywne Wizualizacje i Automatyczna Analiza:**
    -   🗺️ **Globalna Mapa Szczęścia:** Interaktywna mapa choropleth prezentująca wskaźniki szczęścia.
    -   📈 **Wykres Korelacji:** Wizualizuje zależność między PKB a poziomem szczęścia.
    -   🤖 **Automatyczne Wnioski:**
        -   Automatycznie oblicza i interpretuje siłę korelacji między PKB a szczęściem.
        -   Identyfikuje kraje odstające (najbardziej/najmniej szczęśliwe w stosunku do ich poziomu PKB).
        -   Dostarcza automatyczny ranking 5 najważniejszych czynników wpływających na szczęście.

-   **Przyjazny Interfejs Użytkownika:**
    -   -   **Filtrowanie na Pasku Bocznym:** Umożliwia bardziej ukierunkowaną analizę poprzez filtrowanie danych według regionu.
    -   -   **Responsywny Interfejs:** Zbudowany z wykorzystaniem Streamlit dla czystego i nowoczesnego wyglądu.

## Stos Technologiczny

-   **Backend i Frontend:** [Streamlit](https://streamlit.io/)
-   **Przetwarzanie Danych:** [Pandas](https://pandas.pydata.org/)
-   **Wizualizacje:** [Plotly Express](https://plotly.com/python/plotly-express/), [Seaborn](https://seaborn.pydata.org/), [Matplotlib](https://matplotlib.org/)
-   **Dopasowywanie Ciągów Znaków:** [thefuzz](https://github.com/seatgeek/thefuzz)
-   **Analiza Statystyczna:** [Statsmodels](https://www.statsmodels.org/stable/index.html)

## Struktura Projektu

```
world-happiness-dashboard/
├── data/                 # Pliki CSV z danymi oraz pliki referencyjne
│   ├── WHR2022.csv
│   ├── WHR2023.csv
│   ├── WHR2024.csv
│   └── country_region_lookup.csv
├── scripts/              # Skrypty pomocnicze do przygotowania danych
│   └── corrupt_data.py
│   └── create_lookup.py
├── .gitignore            # Definiuje pliki ignorowane przez Git
├── app.py                # Główny skrypt aplikacji Streamlit
├── LICENSE               # Plik licencji MIT
├── README.md             # Ten plik (wersja angielska)
├── README.pl.md          # Ten plik (wersja polska)
└── requirements.txt      # Zależności projektu
```

## Instalacja i Uruchomienie

Aby uruchomić ten projekt lokalnie, postępuj zgodnie z poniższymi krokami:

1.  **Sklonuj repozytorium:**
    ```bash
    git clone https://github.com/TwojaNazwaUzytkownika/world-happiness-dashboard.git
    cd world-happiness-dashboard
    ```

2.  **Stwórz i aktywuj środowisko wirtualne (zalecane):**
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate
    ```

3.  **Zainstaluj wymagane zależności:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Uruchom aplikację Streamlit:**
    ```bash
    streamlit run app.py
    ```
    Aplikacja otworzy się w Twojej domyślnej przeglądarce internetowej.

## Źródło Danych

Zbiory danych użyte w tym projekcie pochodzą z raportu World Happiness Report, udostępnionego na platformie [Kaggle](https://www.kaggle.com/datasets/mathurinache/world-happiness-report-2022).

## Licencja

Ten projekt jest udostępniany na licencji MIT. Zobacz plik [LICENSE](LICENSE), aby uzyskać więcej informacji.