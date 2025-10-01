"""
================================================================================
World Happiness Report - Interactive Dashboard
================================================================================

This Streamlit application serves as an interactive tool for exploring and analyzing
data from the annual World Happiness Report. The project demonstrates a full data
pipeline, from data ingestion and cleaning to advanced visualization and automated analysis.

--------------------------------------------------------------------------------
Features:
--------------------------------------------------------------------------------
1.  **Dynamic File Upload:** Users can upload different yearly reports in CSV format.
2.  **Robust Data Processing Pipeline:**
    -   **Column Standardization:** A robust function standardizes inconsistent column
        names across different yearly reports.
    -   **Data Enrichment:** Enriches data by adding missing region information using
        a master lookup file (`country_region_lookup.csv`).
    -   **Fuzzy Name Matching:** Intelligently matches inconsistent country names
        (e.g., 'Turkey' vs. 'Turkiye') against the master list.
    -   **Interactive Data Cleaning:** If automatic matching fails, an interactive
        review panel allows the user to manually resolve ambiguities.
    -   **Missing Value Imputation:** Detects missing numerical data and lets the
        user choose an imputation strategy (mean, median, or drop).
3.  **Interactive Visualizations & Automated Analysis:**
    -   An interactive world map (choropleth) of happiness scores.
    -   A scatter plot showing the correlation between GDP and happiness, complete
        with an automated analysis of the relationship strength and identification
        of outliers.
    -   A correlation heatmap and an automated ranking of the top 5 factors that
        contribute most to happiness.
4.  **Filtering:** A sidebar allows users to filter the data by region for
    more focused analysis.

--------------------------------------------------------------------------------
To run the application:
--------------------------------------------------------------------------------
1.  Ensure all dependencies from `requirements.txt` are installed.
2.  Execute from the project's root directory:
    $ streamlit run app.py
================================================================================
"""

# --- 1. LIBRARY IMPORTS ---
import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import os
from thefuzz import process
import statsmodels.api as sm

# --- 2. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="World Happiness Analysis",
    page_icon="😊",
    layout="wide"
)


# --- 3. HELPER FUNCTIONS ---
def standardize_columns(dataframe):
    """
    Creates a new, clean DataFrame by standardizing column names from various
    report versions. It prioritizes columns prefixed with "Explained by:" to
    handle semantically duplicate columns (e.g., in the 2023 report).
    """
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
        # First pass: prioritize "Explained by:" columns
        for col_original in df_original.columns:
            if col_original in processed_original_cols: continue
            if col_original.lower().strip().startswith("explained by:"):
                col_clean_name = col_original.lower().replace('explained by: ', '').strip()
                if any(keyword in col_clean_name for keyword in keywords):
                    best_match_col = col_original
                    break
        # Second pass: if no priority match found, search all columns
        if not best_match_col:
            for col_original in df_original.columns:
                if col_original in processed_original_cols: continue
                col_clean_name = col_original.lower().strip()
                if any(keyword in col_clean_name for keyword in keywords):
                    best_match_col = col_original
                    break
        # If a match was found, copy the data to the new clean DataFrame
        if best_match_col:
            df_clean[standard_name] = df_original[best_match_col]
            processed_original_cols.add(best_match_col)
    # Copy any remaining, unmapped columns to the new DataFrame
    for col in df_original.columns:
        if col not in processed_original_cols:
            df_clean[col] = df_original[col]
    return df_clean


@st.cache_data
def load_lookup_data():
    """
    Loads and caches the master country-region lookup file to avoid re-reading
    it from disk on every script rerun.
    """
    try:
        lookup_path = os.path.join('data', 'country_region_lookup.csv')
        df_lookup = pd.read_csv(lookup_path)
        df_lookup.dropna(subset=['region'], inplace=True)
        return df_lookup
    except FileNotFoundError:
        st.error(
            "Master lookup file 'data/country_region_lookup.csv' not found! Please run 'scripts/create_lookup.py'.")
        return None


# --- 4. APP LAYOUT AND UI ---
st.title('😊 Interactive Dashboard: World Happiness Report Analysis')
st.write("An application to visualize and analyze data from the World Happiness Report.")
st.markdown("---")

# --- 5. FILE UPLOAD AND STATE MANAGEMENT ---
st.markdown("### Step 1: Upload a Data File")
uploaded_file = st.file_uploader("Choose a CSV file (supports 2022-2024 formats)", type="csv")

# Initialize session state to manage the data cleaning workflow
if 'data_cleaned' not in st.session_state:
    st.session_state.data_cleaned = False

# Reset the cleaning state if a new file is uploaded
if uploaded_file and uploaded_file.name != st.session_state.get('last_file_name', ''):
    st.session_state.data_cleaned = False
    st.session_state.last_file_name = uploaded_file.name

# --- 6. MAIN DATA PROCESSING AND VISUALIZATION WORKFLOW ---
if uploaded_file is not None:
    df_lookup = load_lookup_data()

    if df_lookup is not None:
        # --- Stage 1: Initial Data Loading and Standardization ---
        df_raw = pd.read_csv(uploaded_file)
        df_processed = standardize_columns(df_raw)

        canonical_names = df_lookup['canonical_name'].tolist()

        # --- Stage 2: Country Name Matching (Automatic) ---
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

        # --- Stage 3: Interactive User Review for Unmatched Countries ---
        if unmatched_countries and not st.session_state.data_cleaned:
            with st.expander("⚠️ Unrecognized Countries Review - Action Required!", expanded=True):
                st.warning("Could not automatically match all country names. Please review the suggestions below.")
                user_choices = {}
                for country in unmatched_countries:
                    cleaned_name = country.replace('*', '').strip()
                    best_guesses = [guess[0] for guess in process.extract(cleaned_name, canonical_names, limit=3)]
                    options = best_guesses + ["(Skip / Keep Original Name)"]
                    user_choices[country] = st.selectbox(f"Select the correct match for **'{country}'**:", options,
                                                         index=0, key=f"select_{country}")

                if st.button("Apply and Verify Matches"):
                    final_mapping = mapping.copy()
                    for original, choice in user_choices.items():
                        if choice != "(Skip / Keep Original Name)":
                            final_mapping[original] = choice

                    # Conflict detection
                    chosen_canonical_names = list(final_mapping.values())
                    counts = pd.Series(chosen_canonical_names).value_counts()
                    duplicates = counts[counts > 1]
                    if not duplicates.empty:
                        st.error(
                            "Conflict detected! Multiple source countries were mapped to the same canonical name. Please correct your selections.")
                        for dup_name, _ in duplicates.items():
                            conflicting_originals = [orig for orig, can in final_mapping.items() if can == dup_name]
                            st.write(
                                f"- The name **'{dup_name}'** was chosen for: `{', '.join(conflicting_originals)}`")
                    else:
                        # If no conflicts, apply mapping and set state
                        df_processed['canonical_name'] = df_processed['Country'].map(final_mapping)
                        st.session_state.data_cleaned = True
                        st.success("Matches applied successfully! No conflicts found.")
                        st.rerun()
        else:
            st.session_state.data_cleaned = True

        # --- Stage 4: Final Data Enrichment and Display (if cleaning is complete) ---
        if st.session_state.data_cleaned:
            st.header("Step 2: Data Processing Pipeline")
            # Finalize country names
            df_processed['canonical_name'].fillna(df_processed['Country'], inplace=True)

            # Enrich with region data from lookup, ensuring only one 'Region' column
            if 'Region' in df_processed.columns: df_processed = df_processed.drop(columns=['Region'])
            df_enriched = pd.merge(df_processed, df_lookup, on='canonical_name', how='left')

            # Final cleanup
            df_enriched['Country'] = df_enriched['canonical_name']
            df_enriched.rename(columns={'region': 'Region'}, inplace=True)
            df_enriched.drop(columns=['canonical_name'], inplace=True)
            df_enriched['Region'].fillna('Unknown', inplace=True)
            df_processed = df_enriched

            # --- Stage 4a: Missing Value Imputation ---
            st.subheader("Missing Value Handling")
            missing_values = df_processed.isnull().sum()
            missing_values = missing_values[missing_values > 0]
            if not missing_values.empty:
                st.warning("Missing data detected! The table below shows the affected entries.")
                rows_with_missing = df_processed[df_processed.isnull().any(axis=1)]
                cols_with_missing = missing_values.index.tolist()
                if 'Country' in df_processed.columns and 'Country' not in cols_with_missing:
                    cols_with_missing.insert(0, 'Country')
                st.dataframe(rows_with_missing[cols_with_missing].reset_index(drop=True))
                strategy = st.radio("Choose an imputation strategy:",
                                    ('Fill with Median (recommended)', 'Fill with Mean', 'Drop Rows with Missing Data'))
                df_cleaned = df_processed.copy()
                for col in missing_values.index:
                    if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                        if strategy == 'Fill with Median (recommended)':
                            df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)
                        elif strategy == 'Fill with Mean':
                            df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)
                if strategy == 'Drop Rows with Missing Data': df_cleaned.dropna(inplace=True)
                st.success(f"Strategy applied: **{strategy}**. Data has been cleaned.")
            else:
                st.info("No missing values found in the data.")
                df_cleaned = df_processed.copy()

            # --- Stage 4b: Sidebar Filtering ---
            st.sidebar.header("Filter Options")
            if 'Region' in df_cleaned.columns and df_cleaned['Region'].nunique() > 1:
                all_regions = sorted([str(region) for region in df_cleaned['Region'].unique() if pd.notna(region)])
                selected_regions = st.sidebar.multiselect("Filter by region:", options=all_regions, default=all_regions)
                df_filtered = df_cleaned[df_cleaned['Region'].isin(selected_regions)]
            else:
                df_filtered = df_cleaned

            # --- Stage 5: Visualization and Automated Analysis ---
            st.header("Step 3: Visualization and Automated Analysis")
            st.subheader("Processed Data Table")
            st.dataframe(df_filtered, height=300, use_container_width=True)

            st.subheader("Global Happiness Map")
            fig_map = px.choropleth(df_filtered, locations='Country', locationmode='country names',
                                    color='Happiness Score', hover_name='Country',
                                    color_continuous_scale=px.colors.sequential.Plasma,
                                    title='Worldwide Happiness Score Distribution')
            st.plotly_chart(fig_map, use_container_width=True)

            st.subheader("GDP per Capita vs. Happiness Score")
            fig_scatter = px.scatter(df_filtered, x='GDP per capita', y='Happiness Score', hover_name='Country',
                                     title='Relationship between GDP per Capita and Happiness', trendline='ols')
            st.plotly_chart(fig_scatter, use_container_width=True)

            with st.container(border=True):
                st.markdown("#### 🤖 Automated Chart Analysis")
                correlation = df_filtered['GDP per capita'].corr(df_filtered['Happiness Score'])


                def interpret_correlation(c):
                    if c > 0.7:
                        return f"**Very Strong Positive Relationship** (Correlation: {c:.2f}). Higher GDP is strongly associated with higher happiness."
                    elif c > 0.4:
                        return f"**Moderate Positive Relationship** (Correlation: {c:.2f}). A noticeable, but not perfect, link exists between GDP and happiness."
                    elif c > 0.1:
                        return f"**Weak Positive Relationship** (Correlation: {c:.2f}). GDP has a minor positive impact on happiness."
                    else:
                        return "No significant relationship detected."


                st.info(interpret_correlation(correlation))

                X = df_filtered['GDP per capita'].dropna()
                y = df_filtered.loc[X.index, 'Happiness Score'].dropna()
                X = sm.add_constant(X)
                if len(X) > 1:
                    model = sm.OLS(y, X).fit()
                    residuals = model.resid
                    happiest_for_gdp_idx = residuals.idxmax()
                    unhappiest_for_gdp_idx = residuals.idxmin()
                    happiest_country = df_filtered.loc[happiest_for_gdp_idx, 'Country']
                    unhappiest_country = df_filtered.loc[unhappiest_for_gdp_idx, 'Country']
                    st.markdown(f"""
                    - **Top Positive Outlier:** **{happiest_country}** is significantly happier than its GDP level would predict.
                    - **Top Negative Outlier:** **{unhappiest_country}** is less happy than its GDP level would suggest.
                    """)

            st.subheader("Which Factors Matter Most for Happiness?")
            numeric_cols = ['Happiness Score', 'GDP per capita', 'Social Support', 'Life Expectancy', 'Freedom',
                            'Generosity', 'Corruption']
            existing_cols = [col for col in numeric_cols if col in df_filtered.columns]
            if len(existing_cols) > 1:
                correlation_matrix = df_filtered[existing_cols].corr()
                fig_heatmap, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', ax=ax)
                ax.set_title('Correlation Matrix of Happiness Factors')
                st.pyplot(fig_heatmap)

                with st.container(border=True):
                    st.markdown("#### 🤖 Automated Factor Ranking")
                    corr_with_happiness = correlation_matrix['Happiness Score'].drop('Happiness Score').sort_values(
                        ascending=False)
                    st.write("Top 5 factors positively correlated with happiness based on this data:")
                    top_factors = corr_with_happiness.head(5)
                    cols = st.columns(len(top_factors))
                    for i, (factor, value) in enumerate(top_factors.items()):
                        with cols[i]:
                            st.metric(label=f"**{i + 1}. {factor}**", value=f"{value:.2f}")
            else:
                st.warning("Not enough data to build a correlation matrix.")

else:
    # Clear session state if the file is un-uploaded
    if 'data_cleaned' in st.session_state:
        del st.session_state.data_cleaned
    st.info("Please upload a CSV file to begin the analysis.")
