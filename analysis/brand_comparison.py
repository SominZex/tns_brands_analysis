import streamlit as st
import pandas as pd
import plotly.express as px

def brand_comparison_analysis(data, selected_brands):
    st.subheader("Brand vs. Brand Comparison Analysis")

    # Filter data for selected brands
    filtered_data = data[data['brandName'].isin(selected_brands)]

    # Group by brandName and calculate total sales
    brand_comparison = (filtered_data.groupby('brandName')['sellingPrice']
                        .sum()
                        .sort_values(ascending=False)
                        .reset_index())

    # Display the brand comparison data
    st.dataframe(brand_comparison)

    # Sidebar options for chart customization
    st.sidebar.subheader("Brand Comparison Chart Settings")
    
    # Assign unique keys to interactive elements
    chart_type = st.sidebar.selectbox("Select Chart Type", ["Bar Chart", "Pie Chart", "Box Plot"], key="brand_comparison_chart_type")  # Unique key for selectbox
    color_scheme = st.sidebar.color_picker("Select Chart Color", "#3498DB", key="brand_comparison_color_picker")  # Unique key for color picker
    show_data_labels = st.sidebar.checkbox("Show Data Labels", False, key="brand_comparison_show_data_labels")  # Unique key for checkbox

    # Chart rendering based on user selection
    if chart_type == "Bar Chart":
        fig = px.bar(brand_comparison, x='brandName', y='sellingPrice', title="Brand Comparison by Sales",
                     labels={'sellingPrice': 'Sales', 'brandName': 'Brand'}, color_discrete_sequence=[color_scheme])
    elif chart_type == "Pie Chart":
        fig = px.pie(brand_comparison, names='brandName', values='sellingPrice', title="Brand Comparison by Sales",
                     color_discrete_sequence=[color_scheme])
    elif chart_type == "Box Plot":
        # Box plot requires sales data to be grouped by brand for distribution analysis
        fig = px.box(filtered_data, x='brandName', y='sellingPrice', title="Brand Sales Distribution",
                     labels={'sellingPrice': 'Sales', 'brandName': 'Brand'}, color_discrete_sequence=[color_scheme])

    if show_data_labels and chart_type != "Box Plot":
        fig.update_traces(textposition="inside" if chart_type == "Pie Chart" else "top center")

    st.plotly_chart(fig)
