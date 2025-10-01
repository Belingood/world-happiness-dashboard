# World Happiness Report - Interactive Dashboard

![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.50-FF4B4B.svg?style=flat&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.3-150458.svg?style=flat&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-6.3-3F4F75.svg?style=flat&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

An interactive web application built with Streamlit for exploring, cleaning, and analyzing data from the annual World Happiness Report. This project demonstrates a complete data processing pipeline, from raw data ingestion to automated analytical insights.

---

##  Demo

<!-- 
    СОВЕТ: Сделай скриншот или короткую GIF-анимацию работающего приложения и вставь сюда.
    Это сделает твой README в 10 раз лучше!
    Пример: ![App Demo](demo.gif)
-->

## Features

-   **Robust Data Pipeline:**
    -   📂 **Dynamic File Upload:** Supports various yearly report formats (2022-2024).
    -   ✨ **Column Standardization:** Automatically standardizes inconsistent column names.
    -   🌍 **Data Enrichment:** Enriches datasets with missing region information using a master lookup file.
    -   🤝 **Intelligent Name Matching:** Uses fuzzy matching to resolve inconsistent country names (`Turkey` vs. `Turkiye`) and allows for manual override.
    -   ⚠️ **Conflict Detection:** Prevents mapping multiple source countries to the same canonical name.
    -   🧹 **Missing Value Imputation:** Lets the user choose a strategy (mean, median, or drop) for handling missing numerical data.

-   **Interactive Visualizations & Automated Analysis:**
    -   🗺️ **Global Happiness Map:** An interactive choropleth map of happiness scores.
    -   📈 **Correlation Scatter Plot:** Visualizes the relationship between GDP and happiness.
    -   🤖 **Automated Insights:**
        -   Automatically calculates and interprets the strength of the GDP-happiness correlation.
        -   Identifies outlier countries (happiest/unhappiest for their GDP level).
        -   Provides an automated ranking of the top 5 factors contributing to happiness.

-   **User-Friendly Interface:**
    -   -   **Sidebar Filtering:** Allows for focused analysis by filtering data by region.
    -   -   **Responsive Layout:** Built with Streamlit for a clean and modern web interface.

## Tech Stack

-   **Backend & Frontend:** [Streamlit](https://streamlit.io/)
-   **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
-   **Visualizations:** [Plotly Express](https://plotly.com/python/plotly-express/), [Seaborn](https://seaborn.pydata.org/), [Matplotlib](https://matplotlib.org/)
-   **Fuzzy String Matching:** [thefuzz](https://github.com/seatgeek/thefuzz)
-   **Statistical Analysis:** [Statsmodels](https://www.statsmodels.org/stable/index.html)

## Project Structure

```
world-happiness-dashboard/
├── data/                 # Source CSV files and master lookups
│   ├── WHR2022.csv
│   ├── WHR2023.csv
│   ├── WHR2024.csv
│   └── country_region_lookup.csv
├── scripts/              # Helper scripts for data preparation
│   ├── corrupt_data.py
│   └── create_lookup.py
├── .gitignore            # Specifies files for Git to ignore
├── app.py                # The main Streamlit application script
├── LICENSE               # MIT License file
├── README.md             # This file
└── requirements.txt      # Project dependencies
```

## Setup and Usage

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/world-happiness-dashboard.git
    cd world-happiness-dashboard
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    # On Windows
    .venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```
    The application will open in your default web browser.

## Data Source

The datasets used in this project are based on the World Happiness Report, sourced from [Kaggle](https://www.kaggle.com/datasets/mathurinache/world-happiness-report-2022).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.