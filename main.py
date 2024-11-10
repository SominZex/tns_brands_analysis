import streamlit as st
import pandas as pd
from utils.data_loader import load_data
from analysis.weekly_sales import weekly_sales_analysis
from analysis.store_performance_analysis import store_performance_analysis
from analysis.hourly_sales import hourly_sales_analysis
from analysis.category_breakdown import category_breakdown_analysis
from analysis.profit_margin_analysis import profit_margin_analysis
from analysis.top_products import top_products_analysis
from analysis.brand_comparison import brand_comparison_analysis
from analysis.brand_performance_analysis import brand_performance_analysis
from analysis.daily_sales_analysis import daily_sales_analysis

# Page configuration
st.set_page_config(page_title="Brand Analysis Dashboard", layout="wide")

# Load and preprocess data
@st.cache_data
def load_optimized_data(file):
    return load_data(file)



# Cache filtered data with date range and store filter
@st.cache_data
def filter_data(_data, brands, stores, start_date, end_date):
    if start_date is not None:
        start_date = pd.to_datetime(start_date, utc=True)
    if end_date is not None:
        end_date = pd.to_datetime(end_date, utc=True)

    _data['orderDate'] = pd.to_datetime(_data['orderDate'], utc=True)
    
    # Filter data based on selected date range, brands, and stores
    mask = (_data['orderDate'] >= start_date) & (_data['orderDate'] <= end_date) & \
           (_data['brandName'].isin(brands)) & (_data['storeName'].isin(stores))
    filtered_data = _data[mask]
    
    return filtered_data

# Add this after your existing filter_data function
@st.cache_data
def filter_data_by_date(_data, start_date, end_date):
    if start_date is not None:
        start_date = pd.to_datetime(start_date, utc=True)
    if end_date is not None:
        end_date = pd.to_datetime(end_date, utc=True)

    _data['orderDate'] = pd.to_datetime(_data['orderDate'], utc=True)
    
    # Filter data based on selected date range only
    mask = (_data['orderDate'] >= start_date) & (_data['orderDate'] <= end_date)
    date_filtered_data = _data[mask]
    
    # Aggregate by brands
    brand_aggregated = date_filtered_data.groupby('brandName').agg(
        total_sales=('sellingPrice', lambda x: (x * date_filtered_data.loc[x.index, 'quantity']).sum()),
        total_cost=('costPrice', lambda x: (x * date_filtered_data.loc[x.index, 'quantity']).sum()),
        total_quantity=('quantity', 'sum')
    ).reset_index()
    
    brand_aggregated['profit'] = brand_aggregated['total_sales'] - brand_aggregated['total_cost']
    brand_aggregated['profit_margin'] = (brand_aggregated['profit'] / brand_aggregated['total_sales']) * 100
    
    return date_filtered_data, brand_aggregated


# Cache brand list
@st.cache_data
def get_top_brands(data, n=10):
    return data['brandName'].value_counts().head(n).index.tolist()

# Cache store list
@st.cache_data
def get_top_stores(data, n=10):
    return data['storeName'].value_counts().head(n).index.tolist()

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
    st.session_state.last_upload = None

# Sidebar layout
with st.sidebar:
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    
    if uploaded_file:
        if st.session_state.last_upload != uploaded_file.name:
            with st.spinner('Loading data...'):
                st.session_state.data = load_optimized_data(uploaded_file)
                st.session_state.last_upload = uploaded_file.name
            st.success("Data loaded successfully!")
        
        data = st.session_state.data
        
        min_date = data['orderDate'].min()
        max_date = data['orderDate'].max()
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", min_date)
        with col2:
            end_date = st.date_input("End Date", max_date)
        
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        
        # Get the number of unique brands in the data
        unique_brands = data['brandName'].unique()
        n_brands_available = len(unique_brands)

        # Slider to select top N brands, affecting all analyses by default
        n_brands = st.number_input(
            "Select number of top brands to analyze", 
            min_value=1, 
            max_value=n_brands_available, 
            value=min(250, n_brands_available),
            step=1
        )
 
        # Get top brands based on the selected N
        top_brands = get_top_brands(data, n=n_brands)
        
        # Multiselect for narrowing down to specific brands within the top N brands
        selected_brands_sidebar = st.multiselect(
            "Select brands for analysis", 
            options=top_brands
        )
        
        # Get the number of unique stores in the data
        unique_stores = data['storeName'].unique()
        n_stores_available = len(unique_stores)

        # Get top stores based on the selected N (for store filter)
        top_stores = get_top_stores(data, n=n_stores_available)
        
        # Multiselect for narrowing down to specific stores within the top N stores
        selected_stores_sidebar = st.multiselect(
            "Select stores for analysis", 
            options=top_stores
        )

# Ensure that top_brands, selected_brands_sidebar, top_stores, and selected_stores_sidebar are defined before using them
if uploaded_file:
    # Use selected brands and stores from the sidebar if any are chosen, otherwise default to top brands and stores
    selected_brands = selected_brands_sidebar if selected_brands_sidebar else top_brands
    selected_stores = selected_stores_sidebar if selected_stores_sidebar else top_stores
    

    # Filter data based on selected brands, stores, and date range
    filtered_data = filter_data(data, selected_brands, selected_stores, start_date, end_date)
    
    date_filtered_data, brand_aggregated = filter_data_by_date(data, start_date, end_date)

    st.sidebar.markdown(f"**Data points:** {len(filtered_data):,}")
    
    try:
        with st.spinner('Analyzing data...'):
            if len(filtered_data) > 0:

                overall_analysis = filtered_data.groupby('brandName').agg(
                    total_sales=('sellingPrice', lambda x: (x * filtered_data.loc[x.index, 'quantity']).sum()),
                    total_cost=('costPrice', lambda x: (x * filtered_data.loc[x.index, 'quantity']).sum()),
                    total_quantity=('quantity', 'sum')
                ).reset_index()

                overall_analysis['profit'] = overall_analysis['total_sales'] - overall_analysis['total_cost']

                # Run all analyses with filtered_data based on selected brands, stores, or top brands/stores by default
                brand_performance_analysis(filtered_data, selected_brands, selected_stores)
                weekly_sales_analysis(filtered_data, selected_brands, top_brands)
                daily_sales_analysis(filtered_data, selected_brands, selected_stores)
                store_performance_analysis(data, date_filtered_data, selected_brands)
                hourly_sales_analysis(filtered_data, selected_brands)
                category_breakdown_analysis(filtered_data, selected_brands)
                profit_margin_analysis(filtered_data, selected_brands)
                top_products_analysis(filtered_data, selected_brands)
                # brand_comparison_analysis(filtered_data, selected_brands)
            else:
                st.warning("No data found for the selected criteria.")
    except Exception as e:
        st.error(f"An error occurred during analysis: {str(e)}")
        st.exception(e)
else:
    st.warning("Please upload a CSV file to begin analysis.")
