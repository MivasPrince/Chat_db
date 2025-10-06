import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import os
from utils.database import list_tables, get_table_data, execute_query
from utils.visualizations import (
    create_bar_chart, create_line_chart, create_scatter_plot,
    create_pie_chart, create_heatmap, create_histogram,
    create_box_plot, create_time_series, COLORS
)

# Page configuration
st.set_page_config(
    page_title="Advanced Analytics - MIVA Dashboard",
    page_icon="📈",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page to access this section.")
    st.stop()

# Function to display logo with Navy background
def display_logo():
    """Display MIVA logo with Navy background"""
    try:
        if os.path.exists("assets/miva_logo.png"):
            logo = Image.open("assets/miva_logo.png")
            col1, col2, col3 = st.columns([2, 3, 2])
            with col2:
                st.markdown("""
                <div style="background-color: #000080; padding: 1.5rem; border-radius: 10px; text-align: center; margin-bottom: 2rem;">
                """, unsafe_allow_html=True)
                st.image(logo, width=200)
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        pass

# Custom CSS
st.markdown(f"""
<style>
.analytics-header {{
    background: linear-gradient(135deg, {COLORS['navy']} 0%, #1e3c72 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
}}
.filter-section {{
    background-color: {COLORS['ash']};
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}}
.analysis-card {{
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    border-left: 4px solid {COLORS['red']};
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# Display logo
display_logo()

# Header
st.markdown("""
<div class="analytics-header">
    <h1 style='color: white; margin: 0;'>📈 Advanced Analytics</h1>
    <p style='color: #F5F5F5; margin-top: 0.5rem;'>Interactive data analysis with custom filters</p>
</div>
""", unsafe_allow_html=True)

# Get available tables
tables = list_tables()

if not tables:
    st.error("No tables found in the database.")
    st.stop()

# Initialize session state
if 'selected_data' not in st.session_state:
    st.session_state.selected_data = None
if 'filters_applied' not in st.session_state:
    st.session_state.filters_applied = False

# Sidebar filters
with st.sidebar:
    st.markdown("### 🎛️ Analysis Controls")
    
    # Table selection
    selected_table = st.selectbox(
        "📋 Select Table",
        tables,
        help="Choose a table to analyze"
    )
    
    # Load data limit
    row_limit = st.number_input(
        "📊 Row Limit",
        min_value=100,
        max_value=50000,
        value=1000,
        step=100,
        help="Limit rows for performance"
    )
    
    if st.button("🔄 Load Data", use_container_width=True):
        with st.spinner("Loading data..."):
            df = get_table_data(selected_table, row_limit)
            if not df.empty:
                st.session_state.selected_data = df
                st.session_state.current_table = selected_table
                st.success(f"✅ Loaded {len(df)} rows from {selected_table}")
            else:
                st.error("Failed to load data")
    
    st.markdown("---")
    
    # Dynamic filters based on loaded data
    if st.session_state.selected_data is not None:
        st.markdown("### 🔍 Data Filters")
        
        df = st.session_state.selected_data
        filtered_df = df.copy()
        
        # Get column types
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        text_cols = df.select_dtypes(include=['object']).columns.tolist()
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Numeric filters
        if numeric_cols:
            st.markdown("#### Numeric Filters")
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                min_val = float(df[col].min())
                max_val = float(df[col].max())
                
                col_range = st.slider(
                    f"{col}",
                    min_value=min_val,
                    max_value=max_val,
                    value=(min_val, max_val),
                    key=f"range_{col}"
                )
                
                filtered_df = filtered_df[
                    (filtered_df[col] >= col_range[0]) & 
                    (filtered_df[col] <= col_range[1])
                ]
        
        # Text filters
        if text_cols:
            st.markdown("#### Text Filters")
            for col in text_cols[:3]:  # Limit to first 3 text columns
                unique_vals = df[col].dropna().unique()
                if len(unique_vals) <= 20:  # Only show filter for columns with reasonable unique values
                    selected_vals = st.multiselect(
                        f"{col}",
                        options=unique_vals,
                        default=unique_vals[:min(5, len(unique_vals))],
                        key=f"multi_{col}"
                    )
                    if selected_vals:
                        filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]
        
        # Date filters
        if date_cols:
            st.markdown("#### Date Filters")
            for col in date_cols[:2]:  # Limit to first 2 date columns
                date_range = st.date_input(
                    f"{col} range",
                    value=(df[col].min(), df[col].max()),
                    key=f"date_{col}"
                )
                if len(date_range) == 2:
                    filtered_df = filtered_df[
                        (filtered_df[col] >= pd.Timestamp(date_range[0])) & 
                        (filtered_df[col] <= pd.Timestamp(date_range[1]))
                    ]
        
        if st.button("🎯 Apply Filters", use_container_width=True):
            st.session_state.filtered_data = filtered_df
            st.session_state.filters_applied = True
            st.success(f"✅ Filters applied: {len(filtered_df)} rows")

# Main content area
if st.session_state.selected_data is None:
    st.info("👈 Please select a table and load data from the sidebar to begin analysis.")
else:
    # Use filtered data if available, otherwise use original
    df = st.session_state.get('filtered_data', st.session_state.selected_data)
    
    # Display current data info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Table", st.session_state.get('current_table', 'N/A'))
    with col2:
        st.metric("Total Rows", f"{len(df):,}")
    with col3:
        st.metric("Total Columns", len(df.columns))
    with col4:
        status = "Filtered" if st.session_state.filters_applied else "Original"
        st.metric("Data Status", status)
    
    st.markdown("---")
    
    # Analysis tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Distributions", "📈 Trends", "🔗 Correlations", 
        "📉 Outliers", "📋 Summary Stats"
    ])
    
    with tab1:
        st.markdown("### 📊 Data Distributions")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        if numeric_cols:
            col1, col2 = st.columns(2)
            
            with col1:
                selected_numeric = st.selectbox(
                    "Select numeric column for histogram:",
                    numeric_cols
                )
                
                if selected_numeric:
                    fig_hist = create_histogram(
                        df, selected_numeric,
                        title=f"Distribution of {selected_numeric}"
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                if len(numeric_cols) >= 2:
                    selected_x = st.selectbox("X-axis:", numeric_cols)
                    selected_y = st.selectbox(
                        "Y-axis:", 
                        [col for col in numeric_cols if col != selected_x]
                    )
                    
                    fig_scatter = create_scatter_plot(
                        df, selected_x, selected_y,
                        title=f"{selected_x} vs {selected_y}"
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)
        
        if categorical_cols:
            st.markdown("#### Categorical Distributions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_cat = st.selectbox(
                    "Select categorical column:",
                    categorical_cols
                )
                
                if selected_cat:
                    value_counts = df[selected_cat].value_counts().head(10)
                    fig_bar = create_bar_chart(
                        pd.DataFrame({'Category': value_counts.index, 'Count': value_counts.values}),
                        'Category', 'Count',
                        title=f"Top 10 {selected_cat} Values"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                if selected_cat:
                    fig_pie = create_pie_chart(
                        pd.DataFrame({'Category': value_counts.index, 'Count': value_counts.values}),
                        'Count', 'Category',
                        title=f"{selected_cat} Distribution"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab2:
        st.markdown("### 📈 Trend Analysis")
        
        # Check for date columns
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if date_cols and numeric_cols:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                date_col = st.selectbox("Select date column:", date_cols)
                value_col = st.selectbox("Select value column:", numeric_cols)
                aggregation = st.selectbox(
                    "Aggregation:",
                    ["mean", "sum", "count", "max", "min"]
                )
            
            with col2:
                if date_col and value_col:
                    # Aggregate data by date
                    df_trend = df.groupby(pd.Grouper(key=date_col, freq='D'))[value_col].agg(aggregation).reset_index()
                    
                    fig_trend = create_time_series(
                        df_trend, date_col, value_col,
                        title=f"{aggregation.capitalize()} of {value_col} over Time"
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("📅 No date columns found for trend analysis. Time-based analysis requires date/datetime columns.")
    
    with tab3:
        st.markdown("### 🔗 Correlation Analysis")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if len(numeric_cols) >= 2:
            fig_corr = create_heatmap(df, title="Correlation Matrix")
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Top correlations
                st.markdown("#### 🔝 Top Correlations")
                corr_matrix = df[numeric_cols].corr()
                
                # Get upper triangle of correlation matrix
                upper_tri = corr_matrix.where(
                    np.triu(np.ones(corr_matrix.shape), k=1).astype(bool)
                )
                
                # Find top correlations
                corr_list = []
                for col in upper_tri.columns:
                    for row in upper_tri.index:
                        val = upper_tri.loc[row, col]
                        if pd.notna(val) and abs(val) < 1:
                            corr_list.append({
                                'Variable 1': row,
                                'Variable 2': col,
                                'Correlation': val,
                                'Absolute': abs(val)
                            })
                
                if corr_list:
                    corr_df = pd.DataFrame(corr_list).sort_values('Absolute', ascending=False).head(10)
                    corr_df['Correlation'] = corr_df['Correlation'].round(3)
                    st.dataframe(corr_df[['Variable 1', 'Variable 2', 'Correlation']], use_container_width=True)
        else:
            st.info("📊 Need at least 2 numeric columns for correlation analysis.")
    
    with tab4:
        st.markdown("### 📉 Outlier Detection")
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if numeric_cols:
            selected_outlier_col = st.selectbox(
                "Select column for outlier analysis:",
                numeric_cols
            )
            
            if selected_outlier_col:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_box = create_box_plot(
                        df, selected_outlier_col,
                        title=f"Box Plot - {selected_outlier_col}"
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
                
                with col2:
                    # Calculate outliers using IQR method
                    Q1 = df[selected_outlier_col].quantile(0.25)
                    Q3 = df[selected_outlier_col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    
                    outliers = df[(df[selected_outlier_col] < lower_bound) | 
                                 (df[selected_outlier_col] > upper_bound)]
                    
                    st.markdown("#### Outlier Statistics")
                    st.metric("Total Outliers", len(outliers))
                    st.metric("Percentage", f"{(len(outliers)/len(df)*100):.2f}%")
                    st.metric("Lower Bound", f"{lower_bound:.2f}")
                    st.metric("Upper Bound", f"{upper_bound:.2f}")
                    
                    if len(outliers) > 0:
                        st.markdown("##### Outlier Values")
                        st.dataframe(
                            outliers[[selected_outlier_col]].sort_values(selected_outlier_col),
                            use_container_width=True
                        )
    
    with tab5:
        st.markdown("### 📋 Statistical Summary")
        
        # Overall statistics
        st.markdown("#### Dataset Overview")
        st.dataframe(df.describe(), use_container_width=True)
        
        # Data types
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Data Types")
            dtype_df = pd.DataFrame({
                'Column': df.columns,
                'Type': df.dtypes.astype(str)
            })
            st.dataframe(dtype_df, use_container_width=True)
        
        with col2:
            st.markdown("#### Missing Values")
            missing_df = pd.DataFrame({
                'Column': df.columns,
                'Missing': df.isnull().sum(),
                'Percentage': (df.isnull().sum() / len(df) * 100).round(2)
            })
            missing_df = missing_df[missing_df['Missing'] > 0].sort_values('Missing', ascending=False)
            
            if not missing_df.empty:
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.success("✅ No missing values found!")

# Footer
st.markdown("---")
st.info("""
**💡 Tips:**
- Load data first from the sidebar before starting analysis
- Apply filters to focus on specific data subsets
- Use different tabs to explore various aspects of your data
- Export visualizations using the download button in each chart
""")

st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>© 2025 MIVA Open University. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
