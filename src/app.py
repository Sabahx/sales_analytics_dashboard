"""
Sales Analytics Dashboard - Main Application

A comprehensive e-commerce analytics dashboard providing insights into
sales performance, customer behavior, product analytics, and geographic trends.

Author: Sabah Aljajeh
Repository: https://github.com/Sabahx/sales_analytics_dashboard
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import analytics functions from modular structure
from src.analytics.kpis import get_kpis, get_sales_summary
from src.analytics.revenue import (
    get_revenue_trend,
    get_monthly_revenue,
    get_monthly_growth,
    get_sales_by_hour,
    get_sales_by_day_of_week
)
from src.analytics.customer import (
    get_customer_segments,
    get_customer_lifetime_value,
    get_top_customers
)
from src.analytics.product import get_top_products
from src.analytics.geographic import (
    get_revenue_by_country,
    get_country_performance_detailed
)
from src.analytics.forecasting import (
    get_revenue_forecast,
    get_forecast_comparison
)

# Import configuration
from src.config.settings import AppConfig
from src.config.constants import CHART_CONFIG, LOADING_MESSAGES, ERROR_MESSAGES
from src.utils.logger import get_module_logger
from src.utils.filters import get_date_range, get_available_countries, get_available_products
from src.utils.export import export_to_csv, export_to_excel, format_for_export

# Initialize logger
logger = get_module_logger(__name__)

# Configure Streamlit page
st.set_page_config(
    page_title=AppConfig.PAGE_TITLE,
    page_icon=AppConfig.PAGE_ICON,
    layout=AppConfig.LAYOUT,
    initial_sidebar_state=AppConfig.INITIAL_SIDEBAR_STATE
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)


# ==================== DATA LOADING WITH CACHING ====================

@st.cache_data(ttl=AppConfig.CACHE_TTL, show_spinner=LOADING_MESSAGES['kpis'])
def load_kpis() -> Dict[str, Any]:
    """Load key performance indicators with caching."""
    try:
        logger.debug("Loading KPIs...")
        return get_kpis()
    except Exception as e:
        logger.error(f"Error loading KPIs: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return {}


@st.cache_data(ttl=AppConfig.CACHE_TTL, show_spinner=LOADING_MESSAGES['revenue'])
def load_summary() -> Dict[str, Any]:
    """Load sales summary data with caching."""
    try:
        logger.debug("Loading summary data...")
        return get_sales_summary()
    except Exception as e:
        logger.error(f"Error loading summary: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return {}


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_revenue_trend() -> pd.DataFrame:
    """Load daily revenue trend data."""
    try:
        logger.debug("Loading revenue trend...")
        return get_revenue_trend()
    except Exception as e:
        logger.error(f"Error loading revenue trend: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_monthly_revenue() -> pd.DataFrame:
    """Load monthly revenue data."""
    try:
        logger.debug("Loading monthly revenue...")
        return get_monthly_revenue()
    except Exception as e:
        logger.error(f"Error loading monthly revenue: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_monthly_growth() -> pd.DataFrame:
    """Load month-over-month growth data."""
    try:
        logger.debug("Loading growth data...")
        return get_monthly_growth()
    except Exception as e:
        logger.error(f"Error loading growth data: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_top_products(limit: int = AppConfig.TOP_PRODUCTS_LIMIT) -> pd.DataFrame:
    """Load top products by revenue."""
    try:
        logger.debug(f"Loading top {limit} products...")
        return get_top_products(limit)
    except Exception as e:
        logger.error(f"Error loading products: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_country_detailed() -> pd.DataFrame:
    """Load detailed country performance data."""
    try:
        logger.debug("Loading country performance data...")
        return get_country_performance_detailed()
    except Exception as e:
        logger.error(f"Error loading country data: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_customer_segments() -> pd.DataFrame:
    """Load customer segmentation data."""
    try:
        logger.debug("Loading customer segments...")
        return get_customer_segments()
    except Exception as e:
        logger.error(f"Error loading customer segments: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_customer_lifetime_value() -> pd.DataFrame:
    """Load customer lifetime value data."""
    try:
        logger.debug("Loading customer lifetime value...")
        return get_customer_lifetime_value()
    except Exception as e:
        logger.error(f"Error loading CLV data: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_top_customers(limit: int = AppConfig.TOP_CUSTOMERS_LIMIT) -> pd.DataFrame:
    """Load top customers by spending."""
    try:
        logger.debug("Loading top customers...")
        return get_top_customers(limit)
    except Exception as e:
        logger.error(f"Error loading top customers: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_sales_by_hour() -> pd.DataFrame:
    """Load sales patterns by hour of day."""
    try:
        logger.debug("Loading hourly sales...")
        return get_sales_by_hour()
    except Exception as e:
        logger.error(f"Error loading hourly sales: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL)
def load_sales_by_day() -> pd.DataFrame:
    """Load sales patterns by day of week."""
    try:
        logger.debug("Loading daily sales...")
        return get_sales_by_day_of_week()
    except Exception as e:
        logger.error(f"Error loading daily sales: {e}")
        st.error(ERROR_MESSAGES['query_failed'])
        return pd.DataFrame()


@st.cache_data(ttl=AppConfig.CACHE_TTL * 2)  # Cache forecasts longer
def load_revenue_forecast(periods: int = 30):
    """Load revenue forecast data."""
    try:
        logger.debug(f"Generating {periods}-day revenue forecast...")
        return get_revenue_forecast(periods=periods, include_history=True)
    except Exception as e:
        logger.error(f"Error generating forecast: {e}")
        st.error(f"Failed to generate forecast: {str(e)}")
        return pd.DataFrame(), {}


@st.cache_data(ttl=AppConfig.CACHE_TTL * 2)
def load_forecast_comparison():
    """Load forecast accuracy comparison."""
    try:
        logger.debug("Loading forecast comparison...")
        return get_forecast_comparison()
    except Exception as e:
        logger.error(f"Error loading forecast comparison: {e}")
        return pd.DataFrame()


# ==================== HELPER FUNCTIONS ====================

def format_currency(value: float) -> str:
    """Format value as currency using AppConfig settings."""
    return f"{AppConfig.CURRENCY_SYMBOL}{value:,.{AppConfig.DECIMAL_PLACES}f}"


def format_number(value: float) -> str:
    """Format value as number with thousand separators."""
    return f"{value:{AppConfig.THOUSAND_SEPARATOR}}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value:.{AppConfig.DECIMAL_PLACES-1}f}%"


def create_metric_card(label: str, value: str, delta: str = None) -> None:
    """Create a styled metric card."""
    if delta:
        st.metric(label, value, delta)
    else:
        st.metric(label, value)


# ==================== MAIN APPLICATION ====================

def main():
    """Main application entry point."""

    # ==================== SIDEBAR FILTERS ====================
    with st.sidebar:
        st.header("🔍 Filters & Options")

        # Date range filter
        st.subheader("Date Range")
        try:
            min_date, max_date = get_date_range()
            date_range = st.date_input(
                "Select date range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date,
                help="Filter data by date range"
            )
        except Exception as e:
            logger.error(f"Error loading date range: {e}")
            date_range = None

        st.markdown("---")

        # Country filter
        st.subheader("Countries")
        try:
            all_countries = get_available_countries()
            selected_countries = st.multiselect(
                "Select countries",
                options=all_countries,
                default=None,
                help="Filter by specific countries (leave empty for all)"
            )
        except Exception as e:
            logger.error(f"Error loading countries: {e}")
            selected_countries = []

        st.markdown("---")

        # Product filter
        st.subheader("Products")
        try:
            top_products_list = get_available_products(limit=50)
            selected_products = st.multiselect(
                "Select products",
                options=top_products_list,
                default=None,
                help="Filter by specific products (leave empty for all)"
            )
        except Exception as e:
            logger.error(f"Error loading products: {e}")
            selected_products = []

        st.markdown("---")

        # Display filter summary
        st.subheader("Active Filters")
        filter_count = 0
        if date_range and len(date_range) == 2:
            st.info(f"📅 {date_range[0]} to {date_range[1]}")
            filter_count += 1
        if selected_countries:
            st.info(f"🌍 {len(selected_countries)} countries")
            filter_count += 1
        if selected_products:
            st.info(f"📦 {len(selected_products)} products")
            filter_count += 1

        if filter_count == 0:
            st.success("No filters applied - showing all data")

        # Refresh button
        st.markdown("---")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # ==================== HEADER ====================
    st.title("📊 Sales Analytics Dashboard")
    st.markdown("**E-commerce Sales Performance Analysis**")

    # Show filter info in main area
    if date_range and len(date_range) == 2:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"📅 Showing data from **{date_range[0]}** to **{date_range[1]}**")
        with col2:
            pass  # Reserved for export buttons

    st.markdown("---")

    # Load data
    with st.spinner("Loading dashboard data..."):
        summary = load_summary()
        kpis = load_kpis()

    if not summary or not kpis:
        st.error("Failed to load dashboard data. Please check database connection.")
        return

    # ==================== OVERVIEW SECTION ====================
    st.subheader("📈 Overview")

    # Primary KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        create_metric_card("💰 Total Revenue", format_currency(kpis['revenue']))
    with col2:
        create_metric_card("🛒 Orders", format_number(kpis['orders']))
    with col3:
        create_metric_card("👥 Customers", format_number(kpis['customers']))
    with col4:
        create_metric_card("📦 Products", format_number(summary['total_products']))
    with col5:
        create_metric_card("🌍 Countries", str(summary['total_countries']))

    # Secondary KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        create_metric_card("📊 Avg Order Value", f"${kpis['avg_order']:.2f}")
    with col2:
        create_metric_card("💳 Avg Transaction", f"${summary['avg_transaction']:.2f}")
    with col3:
        days_active = (summary['last_sale'] - summary['first_sale']).days
        create_metric_card("📅 Data Period", f"{days_active} days")

    st.markdown("---")

    # ==================== REVENUE ANALYSIS ====================
    st.subheader("📈 Revenue Analysis")

    tab1, tab2, tab3 = st.tabs(["📅 Daily Trend", "📊 Monthly Analysis", "📈 Growth Rate"])

    with tab1:
        trend_df = load_revenue_trend()
        if not trend_df.empty:
            fig = px.line(
                trend_df, x='date', y='revenue',
                title='Daily Revenue Trend',
                labels={'date': 'Date', 'revenue': 'Revenue ($)'}
            )
            fig.update_traces(line_color='#1f77b4', line_width=2)
            fig.update_layout(
                hovermode='x unified',
                plot_bgcolor='white',
                height=AppConfig.CHART_HEIGHT
            )
            st.plotly_chart(fig, width='stretch')

    with tab2:
        monthly_df = load_monthly_revenue()
        if not monthly_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    monthly_df, x='month', y='revenue',
                    title='Monthly Revenue',
                    labels={'month': 'Month', 'revenue': 'Revenue ($)'},
                    color='revenue',
                    color_continuous_scale='Blues'
                )
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(height=AppConfig.CHART_HEIGHT)
                st.plotly_chart(fig, width='stretch')

            with col2:
                fig = px.line(
                    monthly_df, x='month', y='orders',
                    title='Monthly Orders',
                    labels={'month': 'Month', 'orders': 'Orders'},
                    markers=True
                )
                fig.update_xaxes(tickangle=-45)
                fig.update_layout(height=AppConfig.CHART_HEIGHT)
                st.plotly_chart(fig, width='stretch')

    with tab3:
        growth_df = load_monthly_growth()
        if not growth_df.empty:
            # Create bar chart with conditional coloring
            colors = ['#28a745' if x > 0 else '#dc3545' for x in growth_df['growth_rate'].fillna(0)]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=growth_df['month'],
                y=growth_df['growth_rate'],
                marker_color=colors,
                text=growth_df['growth_rate'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A"),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Growth: %{y:.1f}%<extra></extra>'
            ))
            fig.update_layout(
                title='Month-over-Month Growth Rate',
                xaxis_title='Month',
                yaxis_title='Growth Rate (%)',
                showlegend=False,
                height=AppConfig.CHART_HEIGHT,
                plot_bgcolor='white'
            )
            fig.update_xaxes(tickangle=-45)
            st.plotly_chart(fig, width='stretch')

            # Show data table
            with st.expander("📋 View Monthly Data"):
                st.dataframe(growth_df, width='stretch')

    st.markdown("---")

    # ==================== ML FORECASTING ====================
    st.subheader("🔮 Revenue Forecasting (ML-Powered)")

    tab1, tab2 = st.tabs(["📈 Future Predictions", "📊 Forecast Accuracy"])

    with tab1:
        col1, col2 = st.columns([3, 1])

        with col2:
            forecast_days = st.selectbox(
                "Forecast Period",
                options=[7, 14, 30, 60, 90],
                index=2,
                help="Number of days to forecast into the future"
            )
            st.info(f"Using Facebook Prophet ML model with automatic seasonality detection")

        with col1:
            with st.spinner(f"Generating {forecast_days}-day forecast using ML model..."):
                forecast_df, forecast_summary = load_revenue_forecast(periods=forecast_days)

            if not forecast_df.empty:
                # Create forecast visualization
                fig = go.Figure()

                # Historical data
                historical = forecast_df[forecast_df['ds'] <= pd.Timestamp.now()]
                future = forecast_df[forecast_df['ds'] > pd.Timestamp.now()]

                # Add historical line
                if not historical.empty:
                    fig.add_trace(go.Scatter(
                        x=historical['ds'],
                        y=historical['yhat'],
                        name='Historical (fitted)',
                        line=dict(color='#1f77b4', width=2),
                        mode='lines'
                    ))

                # Add forecast line
                if not future.empty:
                    fig.add_trace(go.Scatter(
                        x=future['ds'],
                        y=future['yhat'],
                        name='Forecast',
                        line=dict(color='#ff7f0e', width=2, dash='dash'),
                        mode='lines'
                    ))

                    # Add confidence interval
                    fig.add_trace(go.Scatter(
                        x=future['ds'].tolist() + future['ds'].tolist()[::-1],
                        y=future['yhat_upper'].tolist() + future['yhat_lower'].tolist()[::-1],
                        fill='toself',
                        fillcolor='rgba(255,127,14,0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Interval',
                        showlegend=True
                    ))

                fig.update_layout(
                    title=f'{forecast_days}-Day Revenue Forecast',
                    xaxis_title='Date',
                    yaxis_title='Revenue ($)',
                    hovermode='x unified',
                    height=500,
                    plot_bgcolor='white'
                )

                st.plotly_chart(fig, use_container_width=True)

                # Display forecast summary
                if forecast_summary:
                    st.markdown("#### 📊 Forecast Summary")
                    col1, col2, col3, col4 = st.columns(4)

                    with col1:
                        avg_daily = forecast_summary.get('avg_predicted_value', 0)
                        create_metric_card(
                            "📈 Avg Daily Revenue",
                            format_currency(avg_daily)
                        )

                    with col2:
                        total_predicted = forecast_summary.get('total_predicted_value', 0)
                        create_metric_card(
                            "💰 Total Forecast",
                            format_currency(total_predicted)
                        )

                    with col3:
                        trend = forecast_summary.get('trend_direction', 'stable')
                        trend_emoji = "📈" if trend == "increasing" else "📉" if trend == "decreasing" else "➡️"
                        create_metric_card(
                            "📊 Trend",
                            f"{trend_emoji} {trend.capitalize()}"
                        )

                    with col4:
                        accuracy = forecast_summary.get('accuracy_metrics', {})
                        if accuracy:
                            acc_pct = accuracy.get('accuracy_percent', 0)
                            create_metric_card(
                                "🎯 Model Accuracy",
                                f"{acc_pct:.1f}%"
                            )

                # Show forecast data table
                with st.expander("📋 View Forecast Data"):
                    future_only = forecast_df[forecast_df['ds'] > pd.Timestamp.now()].copy()
                    future_only['date'] = future_only['ds'].dt.date
                    future_only['predicted_revenue'] = future_only['yhat'].apply(lambda x: f"${x:,.2f}")
                    future_only['lower_bound'] = future_only['yhat_lower'].apply(lambda x: f"${x:,.2f}")
                    future_only['upper_bound'] = future_only['yhat_upper'].apply(lambda x: f"${x:,.2f}")
                    display_df = future_only[['date', 'predicted_revenue', 'lower_bound', 'upper_bound']]
                    st.dataframe(display_df, use_container_width=True)

    with tab2:
        st.markdown("### Model Accuracy Validation")
        st.info("Comparing actual vs predicted values for the last 30 days to validate model accuracy")

        comparison_df = load_forecast_comparison()

        if not comparison_df.empty:
            # Create comparison chart
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=comparison_df['date'],
                y=comparison_df['actual_revenue'],
                name='Actual Revenue',
                line=dict(color='#1f77b4', width=2),
                mode='lines+markers'
            ))

            fig.add_trace(go.Scatter(
                x=comparison_df['date'],
                y=comparison_df['predicted_revenue'],
                name='Predicted Revenue',
                line=dict(color='#ff7f0e', width=2, dash='dash'),
                mode='lines+markers'
            ))

            fig.update_layout(
                title='Actual vs Predicted Revenue (Last 30 Days)',
                xaxis_title='Date',
                yaxis_title='Revenue ($)',
                hovermode='x unified',
                height=400,
                plot_bgcolor='white'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Calculate accuracy metrics
            mae = comparison_df['difference'].abs().mean()
            mape = (comparison_df['difference'].abs() / comparison_df['actual_revenue']).mean() * 100
            accuracy = 100 - mape

            col1, col2, col3 = st.columns(3)
            with col1:
                create_metric_card("🎯 Accuracy", f"{accuracy:.1f}%")
            with col2:
                create_metric_card("📊 Avg Error", format_currency(mae))
            with col3:
                rmse = (comparison_df['difference'] ** 2).mean() ** 0.5
                create_metric_card("📏 RMSE", format_currency(rmse))

            # Show comparison table
            with st.expander("📋 View Detailed Comparison"):
                comparison_display = comparison_df.copy()
                comparison_display['date'] = comparison_display['date'].dt.date
                comparison_display['actual_revenue'] = comparison_display['actual_revenue'].apply(lambda x: f"${x:,.2f}")
                comparison_display['predicted_revenue'] = comparison_display['predicted_revenue'].apply(lambda x: f"${x:,.2f}")
                comparison_display['difference'] = comparison_display['difference'].apply(lambda x: f"${x:,.2f}")
                comparison_display['difference_pct'] = comparison_display['difference_pct'].apply(lambda x: f"{x:.1f}%")
                st.dataframe(comparison_display, use_container_width=True)
        else:
            st.warning("Insufficient historical data for accuracy comparison (minimum 60 days required)")

    st.markdown("---")

    # ==================== PRODUCT PERFORMANCE ====================
    st.subheader("🏆 Product Performance")

    col1, col2 = st.columns([2, 1])

    with col1:
        products_df = load_top_products(15)
        if not products_df.empty:
            fig = px.bar(
                products_df,
                x='revenue',
                y='product',
                orientation='h',
                title='Top 15 Products by Revenue',
                labels={'revenue': 'Revenue ($)', 'product': 'Product'},
                color='revenue',
                color_continuous_scale='Viridis',
                hover_data=['units_sold', 'orders']
            )
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=500
            )
            st.plotly_chart(fig, width='stretch')

    with col2:
        if not products_df.empty:
            st.markdown("#### 📊 Product Insights")
            top_product = products_df.iloc[0]

            create_metric_card("🥇 Top Product", top_product['product'][:30] + "...")
            create_metric_card("💰 Revenue", format_currency(top_product['revenue']))
            create_metric_card("📦 Units Sold", format_number(top_product['units_sold']))
            create_metric_card("🛒 Orders", format_number(top_product['orders']))

            st.markdown("---")

            # Calculate concentration
            total_revenue = kpis['revenue']
            top_5_revenue = products_df.head(5)['revenue'].sum()
            top_5_percent = (top_5_revenue / total_revenue) * 100

            st.info(f"📊 **Top 5 products** generate **{top_5_percent:.1f}%** of total revenue")

    # Product data table with export
    with st.expander("📋 View All Product Data"):
        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.dataframe(products_df, width='stretch')
        with col2:
            if not products_df.empty:
                csv_data = export_to_csv(format_for_export(products_df))
                st.download_button(
                    label="📥 CSV",
                    data=csv_data,
                    file_name="product_performance.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        with col3:
            if not products_df.empty:
                excel_data = export_to_excel(format_for_export(products_df))
                st.download_button(
                    label="📥 Excel",
                    data=excel_data,
                    file_name="product_performance.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

    st.markdown("---")

    # ==================== GEOGRAPHIC ANALYSIS ====================
    st.subheader("🌍 Geographic Performance")

    country_df = load_country_detailed()
    if not country_df.empty:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Revenue by Country")
            top_10_countries = country_df.head(10)

            fig = px.pie(
                top_10_countries,
                values='revenue',
                names='country',
                title='Revenue Distribution (Top 10 Countries)',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=AppConfig.CHART_HEIGHT)
            st.plotly_chart(fig, width='stretch')

        with col2:
            st.markdown("#### Orders by Country")

            fig = px.bar(
                top_10_countries,
                x='country',
                y='orders',
                title='Orders by Country (Top 10)',
                color='orders',
                color_continuous_scale='Blues',
                hover_data=['customers', 'revenue']
            )
            fig.update_xaxes(tickangle=-45)
            fig.update_layout(height=AppConfig.CHART_HEIGHT)
            st.plotly_chart(fig, width='stretch')

        # Country details table
        with st.expander("📋 View Country Performance Details"):
            st.dataframe(country_df, width='stretch')

    st.markdown("---")

    # ==================== CUSTOMER ANALYSIS ====================
    st.subheader("👥 Customer Analysis")

    tab1, tab2, tab3 = st.tabs(["👥 Customer Segments", "💰 Lifetime Value", "🌟 Top Customers"])

    with tab1:
        segments_df = load_customer_segments()
        if not segments_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(
                    segments_df,
                    values='customers',
                    names='segment',
                    title='Customer Distribution by Segment',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(height=AppConfig.CHART_HEIGHT)
                st.plotly_chart(fig, width='stretch')

            with col2:
                fig = px.bar(
                    segments_df,
                    x='segment',
                    y='customers',
                    title='Customer Count by Segment',
                    color='customers',
                    color_continuous_scale='Greens'
                )
                fig.update_layout(height=AppConfig.CHART_HEIGHT)
                st.plotly_chart(fig, width='stretch')

    with tab2:
        clv_df = load_customer_lifetime_value()
        if not clv_df.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.bar(
                    clv_df,
                    x='segment',
                    y='avg_clv',
                    title='Average Customer Lifetime Value by Segment',
                    color='avg_clv',
                    color_continuous_scale='YlOrRd',
                    labels={'avg_clv': 'Avg CLV ($)', 'segment': 'Segment'}
                )
                fig.update_layout(height=AppConfig.CHART_HEIGHT)
                st.plotly_chart(fig, width='stretch')

            with col2:
                fig = px.bar(
                    clv_df,
                    x='segment',
                    y='avg_orders',
                    title='Average Orders per Customer by Segment',
                    color='avg_orders',
                    color_continuous_scale='Blues',
                    labels={'avg_orders': 'Avg Orders', 'segment': 'Segment'}
                )
                fig.update_layout(height=AppConfig.CHART_HEIGHT)
                st.plotly_chart(fig, width='stretch')

            # CLV insights
            st.markdown("#### 💡 CLV Insights")
            vip_data = clv_df[clv_df['segment'] == 'VIP'].iloc[0]
            low_value_data = clv_df[clv_df['segment'] == 'Low Value'].iloc[0]

            col1, col2, col3 = st.columns(3)
            with col1:
                create_metric_card("🌟 VIP Customers", format_number(vip_data['customer_count']))
            with col2:
                create_metric_card("💰 VIP Avg CLV", format_currency(vip_data['avg_clv']))
            with col3:
                multiplier = vip_data['avg_clv'] / low_value_data['avg_clv']
                create_metric_card("📊 VIP vs Low Value", f"{multiplier:.1f}x more valuable")

            with st.expander("📋 View CLV Details"):
                st.dataframe(clv_df, width='stretch')

    with tab3:
        top_customers_df = load_top_customers(20)
        if not top_customers_df.empty:
            fig = px.bar(
                top_customers_df,
                x='customer_id',
                y='total_spent',
                title='Top 20 Customers by Total Spending',
                color='total_spent',
                color_continuous_scale='Reds',
                hover_data=['orders', 'avg_transaction']
            )
            fig.update_layout(height=AppConfig.CHART_HEIGHT)
            st.plotly_chart(fig, width='stretch')

            with st.expander("📋 View Top Customers Data"):
                st.dataframe(top_customers_df, width='stretch')

    st.markdown("---")

    # ==================== TIME-BASED PATTERNS ====================
    st.subheader("⏰ Sales Patterns by Time")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Sales by Hour of Day")
        hour_df = load_sales_by_hour()
        if not hour_df.empty:
            fig = px.line(
                hour_df,
                x='hour',
                y='revenue',
                title='Revenue by Hour',
                labels={'hour': 'Hour of Day', 'revenue': 'Revenue ($)'},
                markers=True,
                hover_data=['transactions']
            )
            fig.update_xaxes(dtick=1)
            fig.update_layout(height=AppConfig.CHART_HEIGHT)
            st.plotly_chart(fig, width='stretch')

            peak_hour = hour_df.loc[hour_df['revenue'].idxmax()]
            st.info(f"🕐 **Peak Hour:** {int(peak_hour['hour'])}:00 with {format_currency(peak_hour['revenue'])} in sales")

    with col2:
        st.markdown("#### Sales by Day of Week")
        day_df = load_sales_by_day()
        if not day_df.empty:
            fig = px.bar(
                day_df,
                x='day_name',
                y='revenue',
                title='Revenue by Day of Week',
                color='revenue',
                color_continuous_scale='Viridis',
                hover_data=['orders']
            )
            fig.update_layout(height=AppConfig.CHART_HEIGHT)
            st.plotly_chart(fig, width='stretch')

            peak_day = day_df.loc[day_df['revenue'].idxmax()]
            st.info(f"📅 **Peak Day:** {peak_day['day_name'].strip()} with {format_currency(peak_day['revenue'])} in sales")

    st.markdown("---")

    # ==================== KEY INSIGHTS ====================
    st.subheader("💡 Key Business Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 🎯 Market Concentration")
        if not country_df.empty and kpis:
            uk_data = country_df[country_df['country'] == 'United Kingdom']
            if not uk_data.empty:
                uk_revenue = uk_data['revenue'].values[0]
                uk_percent = (uk_revenue / kpis['revenue']) * 100
                st.warning(
                    f"⚠️ **{uk_percent:.1f}%** of revenue from UK\n\n"
                    f"**Risk:** High market concentration\n\n"
                    f"**Action:** Diversify to other markets"
                )

    with col2:
        st.markdown("#### 👑 VIP Impact")
        if not clv_df.empty and kpis:
            vip_count = clv_df[clv_df['segment'] == 'VIP']['customer_count'].values[0]
            vip_percent = (vip_count / kpis['customers']) * 100
            vip_clv = clv_df[clv_df['segment'] == 'VIP']['avg_clv'].values[0]
            st.success(
                f"🌟 **{vip_percent:.1f}%** of customers are VIPs\n\n"
                f"Avg spend: **{format_currency(vip_clv)}**\n\n"
                f"**Action:** VIP retention program critical"
            )

    with col3:
        st.markdown("#### 📈 Growth Trend")
        if not growth_df.empty:
            recent_growth = growth_df.tail(3)['growth_rate'].mean()
            if pd.notna(recent_growth):
                if recent_growth > 0:
                    st.info(
                        f"📊 Avg growth (last 3 months): **+{recent_growth:.1f}%**\n\n"
                        f"**Trend:** Positive momentum\n\n"
                        f"**Action:** Maintain strategy"
                    )
                else:
                    st.error(
                        f"📊 Avg growth (last 3 months): **{recent_growth:.1f}%**\n\n"
                        f"**Trend:** Declining\n\n"
                        f"**Action:** Review strategy"
                    )

    st.markdown("---")

    # ==================== FOOTER ====================
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📊 Data Quality**")
        st.caption(f"✅ {format_number(summary['total_transactions'])} transactions analyzed")
        st.caption(f"✅ {summary['total_countries']} countries covered")

    with col2:
        st.markdown("**📅 Coverage Period**")
        st.caption(f"📆 From: {summary['first_sale'].date()}")
        st.caption(f"📆 To: {summary['last_sale'].date()}")

    with col3:
        st.markdown("**👤 Created By**")
        st.caption("[Sabah Aljajeh](https://www.linkedin.com/in/sabah-saleh/)")
        st.caption("[GitHub](https://github.com/Sabahx) | [Portfolio](https://portofolio-alpha-coral.vercel.app/)")


# ==================== APPLICATION ENTRY POINT ====================
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.exception(e)
