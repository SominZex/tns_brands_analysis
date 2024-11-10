import streamlit as st
import pandas as pd
import plotly.express as px

def profit_margin_analysis(data, selected_brands):
    st.markdown("<h1 style='text-align: center; color: green;'>Profit Analysis</h1>", unsafe_allow_html=True)

    # Filter data for selected brands
    filtered_data = data[data['brandName'].isin(selected_brands)]

    # Ensure sellingPrice, costPrice, and quantity are numeric
    filtered_data['sellingPrice'] = pd.to_numeric(filtered_data['sellingPrice'], errors='coerce')
    filtered_data['costPrice'] = pd.to_numeric(filtered_data['costPrice'], errors='coerce')
    filtered_data['quantity'] = pd.to_numeric(filtered_data['quantity'], errors='coerce')

    # Calculate total selling price and total cost price by multiplying by quantity
    filtered_data['total_sellingPrice'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_costPrice'] = filtered_data['costPrice'] * filtered_data['quantity']

    # Group by brand and sum the total sellingPrice and total costPrice
    brand_grouped = (filtered_data.groupby('brandName')
                     .agg({'total_sellingPrice': 'sum', 'total_costPrice': 'sum'})
                     .reset_index())

    # Calculate average profit margin based on summed values
    brand_grouped['avg_profit_margin'] = ((brand_grouped['total_sellingPrice'] - brand_grouped['total_costPrice']) / 
                                          brand_grouped['total_sellingPrice']) * 100

    # Display data table with all required features, including total_sellingPrice and total_costPrice
    st.dataframe(brand_grouped)

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
