# Dashboard Analizy Szczęścia

Projekt na przedmiot "Systemy Przetwarzania i Wizualizacji Danych".

## Opis

Interaktywna aplikacja webowa zbudowana w oparciu o framework Streamlit, która pozwala na analizę danych z corocznego raportu "World Happiness Report". Aplikacja realizuje kluczowe etapy pracy z danymi:

1.  **Pozyskanie danych:** Użytkownik może załadować plik CSV z raportem za dowolny rok.
2.  **Przetworzenie danych:** Aplikacja automatycznie standaryzuje nazwy kolumn, wykrywa brakujące dane i pozwala użytkownikowi wybrać strategię ich uzupełnienia.
3.  **Wizualizacja danych:** Wyniki analizy prezentowane są w formie interaktywnego dashboardu zawierającego mapę, wykresy oraz dane zagregowane.

## Struktura Projektu

```
.
├── data/                 # Zbiory danych w formacie CSV
├── report/               # Sprawozdanie z projektu
├── app.py                # Główny kod aplikacji Streamlit
├── requirements.txt      # Zależności projektu
└── README.md             # Ten plik
```

## Instrukcja uruchomienia

1.  Sklonuj repozytorium lub pobierz pliki projektu.
2.  Upewnij się, że masz zainstalowanego Pythona w wersji 3.8+.
3.  Zainstaluj wymagane biblioteki:
    ```bash
    pip install -r requirements.txt
    ```
4.  Uruchom aplikację:
    ```bash
    streamlit run app.py
    ```
5.  Otwórz przeglądarkę i przejdź pod adres wskazany w terminalu (zazwyczaj `http://localhost:8501`).