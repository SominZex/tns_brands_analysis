import streamlit as st
import pandas as pd
import plotly.express as px

def weekly_sales_analysis(data, selected_brands_sidebar, top_brands):
    st.markdown("<h1 style='text-align: center; color: green;'>Weekly Sales</h1>", unsafe_allow_html=True)

    # Ensure that data and top_brands are available
    if data is None or (selected_brands_sidebar is None and top_brands is None):
        st.warning("Please upload data and select at least one brand.")
        return

    # Filter data for the selected brands (sidebar filter)
    if len(selected_brands_sidebar) > 0:
        filtered_data = data[data['brandName'].isin(selected_brands_sidebar)]
    else:
        filtered_data = data

    # Further filter data based on top N brands if top_brands is provided
    if top_brands:
        filtered_data = filtered_data[filtered_data['brandName'].isin(top_brands)]

    # Check if filtered data is empty
    if filtered_data.empty:
        st.warning("No sales data available for the selected brands.")
        return

    # Extract the day of the week and month from orderDate
    filtered_data['day'] = filtered_data['orderDate'].dt.day_name()
    filtered_data['month'] = filtered_data['orderDate'].dt.month_name()

    # Calculate total selling price by multiplying sellingPrice with quantity
    filtered_data['total_selling_price'] = filtered_data['sellingPrice'] * filtered_data['quantity']
    filtered_data['total_cost_price'] = filtered_data['costPrice'] * filtered_data['quantity']

    # Aggregate sales data based on unique brandName and day of the week
    weekly_sales = (
        filtered_data.groupby(['month', 'brandName', 'day'], as_index=False)
        .agg(
            total_selling_price=('total_selling_price', 'sum'),
            total_cost_price=('total_cost_price', 'sum'),
            total_quantity=('quantity', 'sum'),
            category_count=('categoryName', 'nunique')
        )
        .sort_values(by=['month', 'day'])
    )

    # Pivot the DataFrame to create separate columns for each day
    sales_by_day = weekly_sales.pivot_table(
        index=['month', 'brandName'],
        columns='day',
        values='total_selling_price',
        fill_value=0
    ).reset_index()

    weekly_sales_data = (
        filtered_data.groupby(['day', 'brandName'], as_index=False)
        .agg(
            total_selling_price=('total_selling_price', 'sum'),
            total_cost_price=('total_cost_price', 'sum'),
            total_quantity=('quantity', 'sum'),
            category_count=('categoryName', 'nunique')
        )
        .sort_values(by='day')
    )


    # Aggregate sales data based on brand, month, and dynamic week label
    filtered_data['month_year'] = filtered_data['orderDate'].dt.to_period('M') 
    filtered_data['week_number'] = filtered_data.groupby('month_year')['orderDate'].transform(
        lambda x: (x.dt.day - 1) // 7 + 1 
    )
    filtered_data['week_label'] = 'Week ' + filtered_data['week_number'].astype(str)
   
    weekly_sales_by_week = (
        filtered_data.groupby(['month', 'brandName', 'week_label'], as_index=False)
        .agg(
            total_selling_price=('total_selling_price', 'sum'),
            total_cost_price=('total_cost_price', 'sum'),
            total_quantity=('quantity', 'sum'),
            category_count=('categoryName', 'nunique')
        )
        .sort_values(by=['month', 'week_label'])
    )

    # Pivot the DataFrame to create separate columns for each week label
    sales_by_week = weekly_sales_by_week.pivot_table(
        index=['month', 'brandName'],
        columns='week_label',
        values='total_selling_price',
        fill_value=0
    ).reset_index()


    # Calculate weekly sales growth percentage
    sales_by_week_growth = sales_by_week.copy()
    week_columns = sales_by_week.columns[2:]

    # Calculate percentage growth for each week column relative to the previous week
    for i in range(1, len(week_columns)):
        week, prev_week = week_columns[i], week_columns[i - 1]
        sales_by_week_growth[f"{week}_growth"] = (
            (sales_by_week[week] - sales_by_week[prev_week]) / sales_by_week[prev_week]
        ) * 100

    # Remove 'month' and 'Week 5' columns along with 'Week 5_growth'
    columns_to_remove = ['month', 'Week 5', 'Week 5_growth']
    sales_by_week_growth = sales_by_week_growth.drop(columns=[col for col in columns_to_remove if col in sales_by_week_growth.columns])

    # Format growth columns (round and add percentage symbol, also apply color formatting)
    def format_growth(val):
        if isinstance(val, (int, float)):
            rounded_val = round(val, 2)
            formatted_val = f"{rounded_val}%"
            color = 'red' if val < 0 else 'green'
            return f'<span style="color:{color}">{formatted_val}</span>'
        return val

    # Apply formatting to growth columns
    growth_columns = [col for col in sales_by_week_growth.columns if 'growth' in col]
    for col in growth_columns:
        sales_by_week_growth[col] = sales_by_week_growth[col].apply(format_growth)

    # Convert the DataFrame to HTML
    html_table = sales_by_week_growth.to_html(escape=False)

    # Display the weekly sales with growth percentage using Markdown to allow HTML rendering
    st.markdown("<h4 style='text-align: center; color: green;'>Week-wise Sales with Growth Percentage</h4>", unsafe_allow_html=True)
    st.markdown(html_table, unsafe_allow_html=True)


    # Sidebar options for chart customization
    st.sidebar.subheader("Weekly Sales Chart Settings")
    chart_type = st.sidebar.selectbox(
        "Select Chart Type", 
        ["Line Chart", "Bar Chart", "Area Chart", "Donut Chart"], 
        index=1
    )
    color_scheme = px.colors.qualitative.Plotly
    
    # Chart rendering based on user selection
    if chart_type == "Line Chart":
        fig = px.line(
            weekly_sales_data,
            x='day',
            y='total_selling_price',
            color='brandName',
            title="Weekly Sales Trend",
            labels={'total_selling_price': 'Sales'},
            color_discrete_sequence=color_scheme
        )
    elif chart_type == "Bar Chart":
        fig = px.bar(
            weekly_sales_data,
            x='day',
            y='total_selling_price',
            color='brandName',
            title="Weekly Sales Trend",
            labels={'total_selling_price': 'Sales'},
            color_discrete_sequence=color_scheme
        )
    elif chart_type == "Area Chart":
        fig = px.area(
            weekly_sales_data,
            x='day',
            y='total_selling_price',
            color='brandName',
            title="Weekly Sales Trend",
            labels={'total_selling_price': 'Sales'},
            color_discrete_sequence=color_scheme
        )
    elif chart_type == "Donut Chart":
        # Aggregate total sales for donut chart
        donut_data = sales_by_day.melt(id_vars=['month', 'brandName'], value_vars=sales_by_day.columns[2:], 
                                         var_name='day', value_name='total_selling_price')
        fig = px.pie(
            donut_data,
            names='day',
            values='total_selling_price',
            title="Sales Distribution by Day",
            hole=0.4,
            color_discrete_sequence=color_scheme
        )
        fig.update_layout(height=600)



    # Plot the sales trend by week for each brand (added plot)
    sales_by_week_trend = sales_by_week.melt(id_vars=['month', 'brandName'], value_vars=sales_by_week.columns[2:], 
                                             var_name='week_label', value_name='total_selling_price')

    # Plotting the trend of sales by week
    fig_week_trend = px.line(
        sales_by_week_trend,
        x='week_label',
        y='total_selling_price',
        color='brandName',
        title="Weekly Sales Trend by Brand",
        labels={'total_selling_price': 'Sales'},
        color_discrete_sequence=color_scheme
    )

    # Display the weekly sales trend plot
    st.plotly_chart(fig_week_trend, use_container_width=True)


    # Display the Plotly chart in Streamlit with container width adjustment
    st.plotly_chart(fig, use_container_width=True)

    # Display the original weekly sales dataframe (existing analysis)
    # st.markdown("<h4 style='text-align: center; color: green;'>Weekly Sales Dataframe</h4>", unsafe_allow_html=True)
    # st.dataframe(sales_by_day)



