"""
Advanced visualization components for the dashboard.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional
from src.config.settings import AppConfig
from src.utils.logger import get_module_logger

logger = get_module_logger(__name__)


def create_geographic_heatmap(country_df: pd.DataFrame) -> go.Figure:
    """
    Create a choropleth map showing revenue by country.

    Args:
        country_df (pd.DataFrame): DataFrame with columns ['country', 'revenue']

    Returns:
        go.Figure: Plotly choropleth figure
    """
    try:
        fig = px.choropleth(
            country_df,
            locations='country',
            locationmode='country names',
            color='revenue',
            hover_name='country',
            hover_data={'revenue': ':,.0f', 'orders': ':,', 'customers': ':,'},
            color_continuous_scale='Blues',
            title='Global Sales Distribution',
            labels={'revenue': 'Revenue ($)'}
        )

        fig.update_layout(
            height=AppConfig.CHART_HEIGHT + 100,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='natural earth'
            )
        )

        logger.debug("Created geographic heatmap")
        return fig

    except Exception as e:
        logger.error(f"Error creating geographic heatmap: {e}")
        raise


def create_revenue_forecast_chart(
    historical_df: pd.DataFrame,
    periods: int = 30
) -> go.Figure:
    """
    Create a revenue forecast chart with trend line.

    Args:
        historical_df (pd.DataFrame): Historical revenue data
        periods (int): Number of periods to forecast

    Returns:
        go.Figure: Plotly figure with forecast
    """
    try:
        # Create figure
        fig = go.Figure()

        # Add historical data
        fig.add_trace(go.Scatter(
            x=historical_df['date'],
            y=historical_df['revenue'],
            mode='lines',
            name='Actual Revenue',
            line=dict(color='#1f77b4', width=2)
        ))

        # Add trend line (simple moving average)
        if len(historical_df) > 7:
            historical_df['ma7'] = historical_df['revenue'].rolling(window=7).mean()
            fig.add_trace(go.Scatter(
                x=historical_df['date'],
                y=historical_df['ma7'],
                mode='lines',
                name='7-Day Moving Average',
                line=dict(color='#ff7f0e', width=2, dash='dash')
            ))

        fig.update_layout(
            title='Revenue Trend with Moving Average',
            xaxis_title='Date',
            yaxis_title='Revenue ($)',
            height=AppConfig.CHART_HEIGHT,
            hovermode='x unified',
            showlegend=True
        )

        logger.debug("Created revenue forecast chart")
        return fig

    except Exception as e:
        logger.error(f"Error creating forecast chart: {e}")
        raise


def create_funnel_chart(data: pd.DataFrame, stages: list) -> go.Figure:
    """
    Create a funnel chart for conversion analysis.

    Args:
        data (pd.DataFrame): Data with stage values
        stages (list): List of stage names

    Returns:
        go.Figure: Plotly funnel chart
    """
    try:
        fig = go.Figure(go.Funnel(
            y=stages,
            x=data['count'].values,
            textinfo="value+percent initial",
            marker=dict(color=["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"])
        ))

        fig.update_layout(
            title='Customer Conversion Funnel',
            height=AppConfig.CHART_HEIGHT
        )

        logger.debug("Created funnel chart")
        return fig

    except Exception as e:
        logger.error(f"Error creating funnel chart: {e}")
        raise


def create_cohort_heatmap(cohort_df: pd.DataFrame) -> go.Figure:
    """
    Create a cohort analysis heatmap.

    Args:
        cohort_df (pd.DataFrame): Cohort data

    Returns:
        go.Figure: Plotly heatmap
    """
    try:
        fig = go.Figure(data=go.Heatmap(
            z=cohort_df.values,
            x=cohort_df.columns,
            y=cohort_df.index,
            colorscale='YlGnBu',
            hoverongaps=False,
            texttemplate='%{z:.1f}%',
            textfont={"size": 10}
        ))

        fig.update_layout(
            title='Customer Cohort Retention Analysis',
            xaxis_title='Months Since First Purchase',
            yaxis_title='Cohort (Month of First Purchase)',
            height=AppConfig.CHART_HEIGHT + 100
        )

        logger.debug("Created cohort heatmap")
        return fig

    except Exception as e:
        logger.error(f"Error creating cohort heatmap: {e}")
        raise


def create_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: Optional[str] = None,
    color_col: Optional[str] = None,
    title: str = "Scatter Plot"
) -> go.Figure:
    """
    Create an interactive scatter plot.

    Args:
        df (pd.DataFrame): Data
        x_col (str): X-axis column
        y_col (str): Y-axis column
        size_col (str, optional): Bubble size column
        color_col (str, optional): Color column
        title (str): Chart title

    Returns:
        go.Figure: Plotly scatter plot
    """
    try:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            size=size_col,
            color=color_col,
            hover_data=df.columns,
            title=title
        )

        fig.update_layout(height=AppConfig.CHART_HEIGHT)

        logger.debug(f"Created scatter plot: {title}")
        return fig

    except Exception as e:
        logger.error(f"Error creating scatter plot: {e}")
        raise


def create_treemap(
    df: pd.DataFrame,
    path_cols: list,
    values_col: str,
    title: str = "Treemap"
) -> go.Figure:
    """
    Create a treemap visualization.

    Args:
        df (pd.DataFrame): Data
        path_cols (list): Hierarchical path columns
        values_col (str): Values column
        title (str): Chart title

    Returns:
        go.Figure: Plotly treemap
    """
    try:
        fig = px.treemap(
            df,
            path=path_cols,
            values=values_col,
            title=title,
            color=values_col,
            color_continuous_scale='Blues'
        )

        fig.update_layout(height=AppConfig.CHART_HEIGHT + 100)

        logger.debug(f"Created treemap: {title}")
        return fig

    except Exception as e:
        logger.error(f"Error creating treemap: {e}")
        raise
