import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Page configuration
st.set_page_config(page_title="Climate Risk Analysis Dashboard", page_icon="🌐", layout="wide")

# Title and description
st.title("Climate-Driven Disaster Risk Reduction Analysis")
st.markdown("""
This dashboard provides an interactive analysis of climate-driven disasters (Flood, Storm, Wildfire, Extreme Temperature) 
to support Disaster Risk Reduction (DRR) strategies, utilizing the same dataset as the accompanying Jupyter Notebook.
""")

# Cache data loading to improve performance
@st.cache_data
def load_data():
    base_dir = r'C:\Users\ADWAITH CM\Climate week'
    try:
        # Attempt to load the primary dataset
        file_path = os.path.join(base_dir, 'natural_disasters.csv')
        if not os.path.exists(file_path):
            file_path = os.path.join(base_dir, 'data2.csv')
            if not os.path.exists(file_path):
                st.error("Error: Neither 'natural_disasters.csv' nor 'data2.csv' found. Please verify files are in the directory.")
                return None
        df = pd.read_csv(file_path, encoding='latin-1')
        print("Dataset loaded successfully")
        return df
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return None

# Load and filter data
df = load_data()
if df is not None:
    climate_disasters = ['Flood', 'Storm', 'Wildfire', 'Extreme temperature']
    df_climate = df[df['Disaster Type'].isin(climate_disasters)].copy()

    # Handle missing values
    df_climate['Total Deaths'] = df_climate['Total Deaths'].fillna(0)
    df_climate['Total Affected'] = df_climate['Total Affected'].fillna(0)
    df_climate['Total Damages (\'000 US$)'] = df_climate['Total Damages (\'000 US$)'].fillna(
        df_climate['Total Damages (\'000 US$)'].mean()
    )

    # Sidebar for filters
    st.sidebar.header("Filter Options")
    years = sorted(df_climate['Year'].unique())
    selected_years = st.sidebar.slider(
        "Select Year Range",
        min_value=min(years),
        max_value=max(years),
        value=(min(years), max(years))
    )
    selected_disasters = st.sidebar.multiselect(
        "Select Disaster Types",
        options=sorted(df_climate['Disaster Type'].unique()),
        default=sorted(df_climate['Disaster Type'].unique())
    )

    # Apply filters
    mask = (
        (df_climate['Year'].between(selected_years[0], selected_years[1])) &
        (df_climate['Disaster Type'].isin(selected_disasters))
    )
    filtered_df = df_climate[mask]

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events", len(filtered_df))
    with col2:
        st.metric("Total Deaths", f"{filtered_df['Total Deaths'].sum():,.0f}")
    with col3:
        st.metric("Total Affected", f"{filtered_df['Total Affected'].sum():,.0f}")
    with col4:
        total_damages = filtered_df['Total Damages (\'000 US$)'].sum()
        st.metric("Total Damages (USD)", f"${total_damages:,.0f}k")

    # Temporal Analysis
    st.header("Temporal Analysis of Climate Disasters")
    yearly_trends = filtered_df.groupby('Year').size()
    fig1, ax1 = plt.subplots(figsize=(8, 4))  # Reduced from (12, 6) to (8, 4)
    ax1.plot(yearly_trends.index, yearly_trends.values, marker='o', linewidth=1.5, color='b')
    ax1.set_title("Trend of Climate-Driven Disasters")
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Number of Events")
    ax1.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # Disaster Distribution and Impact Analysis
    st.header("Disaster Distribution and Impact Analysis")
    col1, col2 = st.columns(2)
    with col1:
        disaster_counts = filtered_df['Disaster Type'].value_counts()
        fig2, ax2 = plt.subplots(figsize=(6, 4))  # Reduced from (10, 6) to (6, 4)
        disaster_counts.plot(kind='bar', ax=ax2, edgecolor='black')
        ax2.set_title("Distribution of Disaster Types")
        ax2.set_xlabel("Disaster Type")
        ax2.set_ylabel("Count")
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    with col2:
        impact_cols = ['Total Deaths', 'Total Affected', 'Total Damages (\'000 US$)']
        correlation_matrix = filtered_df[impact_cols].corr()
        fig3, ax3 = plt.subplots(figsize=(6, 4))  # Reduced from (8, 6) to (6, 4)
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        ax3.set_title("Correlation of Impact Measures")
        st.pyplot(fig3)

    # Detailed Data View
    st.header("Detailed Dataset View")
    st.dataframe(filtered_df)