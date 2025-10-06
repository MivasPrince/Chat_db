"""Visualization utilities using Plotly"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Dict, List, Any
import streamlit as st

# MIVA brand colors
COLORS = {
    'navy': '#000080',
    'red': '#DC143C',
    'ash': '#F5F5F5',
    'light_navy': '#4169E1',
    'dark_red': '#B91C3C',
    'medium_ash': '#D3D3D3'
}

# Color palette for charts
COLOR_PALETTE = [
    COLORS['red'], COLORS['navy'], COLORS['light_navy'], 
    COLORS['dark_red'], '#FF6B6B', '#4ECDC4', '#45B7D1', 
    '#96CEB4', '#FFEAA7', '#DDA0DD'
]

def apply_miva_theme(fig):
    """Apply MIVA branding theme to plotly figures"""
    fig.update_layout(
        font=dict(family="Arial, sans-serif", color=COLORS['navy']),
        plot_bgcolor=COLORS['ash'],
        paper_bgcolor='white',
        title_font=dict(size=20, color=COLORS['navy']),
        showlegend=True,
        hovermode='closest',
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

def create_bar_chart(data: pd.DataFrame, x: str, y: str, title: str = "Bar Chart") -> go.Figure:
    """Create branded bar chart"""
    fig = px.bar(
        data, x=x, y=y, title=title,
        color_discrete_sequence=[COLORS['red']],
        template='plotly_white'
    )
    return apply_miva_theme(fig)

def create_pie_chart(data: pd.DataFrame, values: str, names: str, title: str = "Distribution") -> go.Figure:
    """Create branded pie chart"""
    fig = px.pie(
        data, values=values, names=names, title=title,
        color_discrete_sequence=COLOR_PALETTE,
        template='plotly_white'
    )
    return apply_miva_theme(fig)

def create_line_chart(data: pd.DataFrame, x: str, y: str, title: str = "Trend Analysis") -> go.Figure:
    """Create branded line chart"""
    fig = px.line(
        data, x=x, y=y, title=title,
        color_discrete_sequence=[COLORS['navy']],
        template='plotly_white',
        markers=True
    )
    fig.update_traces(line=dict(width=3))
    return apply_miva_theme(fig)

def create_scatter_plot(data: pd.DataFrame, x: str, y: str, color: str = None, 
                       size: str = None, title: str = "Scatter Plot") -> go.Figure:
    """Create branded scatter plot"""
    fig = px.scatter(
        data, x=x, y=y, color=color, size=size, title=title,
        color_discrete_sequence=COLOR_PALETTE,
        template='plotly_white'
    )
    return apply_miva_theme(fig)

def create_heatmap(data: pd.DataFrame, title: str = "Heatmap") -> go.Figure:
    """Create correlation heatmap"""
    # Select only numeric columns
    numeric_data = data.select_dtypes(include=[np.number])
    
    if numeric_data.empty:
        return None
    
    corr = numeric_data.corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale=[[0, COLORS['navy']], [0.5, 'white'], [1, COLORS['red']]],
        text=corr.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(title=title)
    
    return apply_miva_theme(fig)

def create_histogram(data: pd.DataFrame, column: str, bins: int = 30, title: str = "Distribution") -> go.Figure:
    """Create histogram with MIVA branding"""
    fig = px.histogram(
        data, x=column, nbins=bins, title=title,
        color_discrete_sequence=[COLORS['red']],
        template='plotly_white'
    )
    return apply_miva_theme(fig)

def create_box_plot(data: pd.DataFrame, y: str, x: str = None, title: str = "Box Plot") -> go.Figure:
    """Create box plot for outlier detection"""
    fig = px.box(
        data, x=x, y=y, title=title,
        color_discrete_sequence=[COLORS['navy']],
        template='plotly_white'
    )
    return apply_miva_theme(fig)

def create_time_series(data: pd.DataFrame, date_col: str, value_col: str, 
                      title: str = "Time Series Analysis") -> go.Figure:
    """Create time series visualization"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data[date_col],
        y=data[value_col],
        mode='lines+markers',
        name=value_col,
        line=dict(color=COLORS['navy'], width=2),
        marker=dict(color=COLORS['red'], size=6)
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title=date_col,
        yaxis_title=value_col,
        hovermode='x unified'
    )
    
    return apply_miva_theme(fig)

def create_gauge_chart(value: float, max_value: float, title: str = "Gauge") -> go.Figure:
    """Create gauge chart for KPIs"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24, 'color': COLORS['navy']}},
        gauge={
            'axis': {'range': [None, max_value], 'tickcolor': COLORS['navy']},
            'bar': {'color': COLORS['red']},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': COLORS['navy'],
            'steps': [
                {'range': [0, max_value * 0.5], 'color': COLORS['ash']},
                {'range': [max_value * 0.5, max_value * 0.75], 'color': COLORS['medium_ash']}
            ],
            'threshold': {
                'line': {'color': COLORS['dark_red'], 'width': 4},
                'thickness': 0.75,
                'value': max_value * 0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="white",
        font={'color': COLORS['navy'], 'family': "Arial"}
    )
    
    return fig

def create_treemap(data: pd.DataFrame, path: List[str], values: str, title: str = "Treemap") -> go.Figure:
    """Create treemap visualization"""
    fig = px.treemap(
        data, path=path, values=values, title=title,
        color_discrete_sequence=COLOR_PALETTE,
        template='plotly_white'
    )
    return apply_miva_theme(fig)

def create_sunburst(data: pd.DataFrame, path: List[str], values: str, title: str = "Sunburst") -> go.Figure:
    """Create sunburst chart"""
    fig = px.sunburst(
        data, path=path, values=values, title=title,
        color_discrete_sequence=COLOR_PALETTE,
        template='plotly_white'
    )
    return apply_miva_theme(fig)

def create_table_summary_card(table_name: str, row_count: int, column_count: int, size: str) -> str:
    """Create HTML card for table summary"""
    return f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['navy']} 0%, {COLORS['light_navy']} 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h3 style="margin: 0; color: white;">{table_name}</h3>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1rem;">
            <div>
                <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">Rows</p>
                <p style="margin: 0; font-size: 1.5rem; font-weight: bold;">{row_count:,}</p>
            </div>
            <div>
                <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">Columns</p>
                <p style="margin: 0; font-size: 1.5rem; font-weight: bold;">{column_count}</p>
            </div>
            <div>
                <p style="margin: 0; opacity: 0.8; font-size: 0.9rem;">Size</p>
                <p style="margin: 0; font-size: 1.5rem; font-weight: bold;">{size}</p>
            </div>
        </div>
    </div>
    """

def create_metric_card(label: str, value: Any, delta: Any = None, delta_color: str = "normal") -> str:
    """Create metric card with optional delta"""
    delta_html = ""
    if delta is not None:
        color = COLORS['red'] if delta_color == "inverse" else "#28a745"
        delta_html = f'<p style="margin: 0; color: {color}; font-size: 0.9rem;">Δ {delta}</p>'
    
    return f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {COLORS['red']};
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    ">
        <p style="margin: 0; color: {COLORS['navy']}; font-size: 0.9rem; opacity: 0.8;">{label}</p>
        <p style="margin: 0.5rem 0; color: {COLORS['navy']}; font-size: 2rem; font-weight: bold;">{value}</p>
        {delta_html}
    </div>
    """
