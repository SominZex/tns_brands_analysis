import streamlit as st
import pandas as pd
import plotly.express as px

def profit_margin_analysis(data, selected_brands):
    st.markdown("<h1 style='text-align: center; color: green;'>Profit Analysis</h1>", unsafe_allow_html=True)

    # Filter data for selected brands
    filtered_data = data[data['brandName'].isin(selected_brands)]

    # Ensure sellingPrice and costPrice are numeric
    filtered_data['sellingPrice'] = pd.to_numeric(filtered_data['sellingPrice'], errors='coerce')
    filtered_data['costPrice'] = pd.to_numeric(filtered_data['costPrice'], errors='coerce')

    # Group by brand and calculate total sellingPrice and costPrice
    brand_grouped = (filtered_data.groupby('brandName')
                     .agg({'sellingPrice': 'sum', 'costPrice': 'sum'})
                     .reset_index())

    # Calculate average profit margin based on summed values
    brand_grouped['avg_profit_margin'] = ((brand_grouped['sellingPrice'] - brand_grouped['costPrice']) / 
                                          brand_grouped['sellingPrice']) * 100

    # Display data table with average profit margin
    st.dataframe(brand_grouped[['brandName', 'avg_profit_margin']])

    # Sidebar options for chart customization
    st.sidebar.subheader("Profit Margin Chart Settings")
    
    # Assign unique keys to interactive elements
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Scatter Plot"], key="profit_margin_chart_type")
    show_data_labels = st.sidebar.checkbox("Show Data Labels", False, key="profit_margin_show_data_labels")

    # Chart rendering based on user selection
    color_palette = px.colors.qualitative.Set3  # A predefined colorful palette from Plotly

    if chart_type == "Bar Chart":
        fig = px.bar(brand_grouped, x='brandName', y='avg_profit_margin', title="Average Profit Margin by Brand",
                     labels={'avg_profit_margin': 'Profit Margin (%)'}, color='brandName', color_discrete_sequence=color_palette)
        
        # Add data labels if checkbox is selected
        if show_data_labels:
            fig.update_traces(text=brand_grouped['avg_profit_margin'].round(2), textposition="inside")
            
    elif chart_type == "Scatter Plot":
        fig = px.scatter(brand_grouped, x='brandName', y='avg_profit_margin', title="Profit Margin by Brand",
                         labels={'avg_profit_margin': 'Profit Margin (%)'}, color='brandName', color_discrete_sequence=color_palette)

        # Add data labels if checkbox is selected
        if show_data_labels:
            fig.update_traces(text=brand_grouped['avg_profit_margin'].round(2), textposition="top center")

    st.plotly_chart(fig, use_container_width=True)
