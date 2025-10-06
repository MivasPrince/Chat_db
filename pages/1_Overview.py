import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.database import (
    list_tables, list_columns, get_table_count, 
    get_table_metadata, get_table_stats
)
from utils.visualizations import (
    create_bar_chart, create_pie_chart, create_table_summary_card,
    create_metric_card, apply_miva_theme, COLORS
)

# Page configuration
st.set_page_config(
    page_title="Overview - MIVA Dashboard",
    page_icon="📊",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page to access this section.")
    st.stop()

# Custom CSS
st.markdown("""
<style>
.overview-header {
    background: linear-gradient(135deg, #000080 0%, #1e3c72 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
}
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="overview-header">
    <h1 style='color: white; margin: 0;'>📊 Database Overview</h1>
    <p style='color: #F5F5F5; margin-top: 0.5rem;'>Comprehensive view of all database tables and statistics</p>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Loading database statistics..."):
    tables = list_tables()
    stats = get_table_stats()

if not tables:
    st.error("No tables found or unable to connect to database.")
    st.stop()

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(create_metric_card(
        "Total Tables", 
        stats.get('table_count', 0)
    ), unsafe_allow_html=True)

with col2:
    st.markdown(create_metric_card(
        "Total Columns", 
        stats.get('total_columns', 0)
    ), unsafe_allow_html=True)

with col3:
    st.markdown(create_metric_card(
        "Total Records", 
        f"{stats.get('total_records', 0):,}"
    ), unsafe_allow_html=True)

with col4:
    st.markdown(create_metric_card(
        "Database Size", 
        stats.get('db_size', 'N/A')
    ), unsafe_allow_html=True)

st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📋 Tables Summary", "📊 Visualizations", "🔍 Table Details", "📈 Statistics"])

with tab1:
    st.markdown("### 📋 All Database Tables")
    
    # Collect table information
    table_data = []
    for table in tables:
        try:
            metadata = get_table_metadata(table)
            columns_df = metadata.get('columns', pd.DataFrame())
            
            table_data.append({
                'Table Name': table,
                'Rows': metadata.get('row_count', 0),
                'Columns': len(columns_df) if not columns_df.empty else 0,
                'Size': metadata.get('size', 'N/A'),
                'Primary Keys': columns_df[columns_df['is_primary_key'] == True]['column_name'].tolist() if not columns_df.empty else []
            })
        except Exception as e:
            st.warning(f"Could not load metadata for {table}: {e}")
            continue
    
    if table_data:
        df_tables = pd.DataFrame(table_data)
        
        # Display as cards
        cols = st.columns(2)
        for idx, row in df_tables.iterrows():
            with cols[idx % 2]:
                pk_list = ", ".join(row['Primary Keys']) if row['Primary Keys'] else "None"
                st.markdown(create_table_summary_card(
                    row['Table Name'],
                    row['Rows'],
                    row['Columns'],
                    row['Size']
                ), unsafe_allow_html=True)
        
        # Also show as table
        st.markdown("### 📊 Summary Table")
        df_display = df_tables.copy()
        df_display['Primary Keys'] = df_display['Primary Keys'].apply(lambda x: ", ".join(x) if x else "None")
        st.dataframe(df_display, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("### 📊 Visual Analytics")
    
    if table_data:
        col1, col2 = st.columns(2)
        
        with col1:
            # Table size distribution
            fig_size = create_bar_chart(
                df_tables.sort_values('Rows', ascending=True).tail(10),
                x='Rows', y='Table Name',
                title="Top 10 Tables by Row Count"
            )
            fig_size.update_layout(height=400)
            fig_size.update_traces(orientation='h')
            st.plotly_chart(fig_size, use_container_width=True)
        
        with col2:
            # Columns distribution
            fig_cols = create_bar_chart(
                df_tables.sort_values('Columns', ascending=True).tail(10),
                x='Columns', y='Table Name',
                title="Top 10 Tables by Column Count"
            )
            fig_cols.update_layout(height=400)
            fig_cols.update_traces(orientation='h', marker_color=COLORS['navy'])
            st.plotly_chart(fig_cols, use_container_width=True)
        
        # Pie chart of table distribution by records
        total_records = df_tables['Rows'].sum()
        df_pie = df_tables.copy()
        df_pie['Percentage'] = (df_pie['Rows'] / total_records * 100).round(2)
        
        # Group small tables
        threshold = 5  # Group tables with less than 5% of records
        large_tables = df_pie[df_pie['Percentage'] >= threshold]
        small_tables_sum = df_pie[df_pie['Percentage'] < threshold]['Rows'].sum()
        
        if small_tables_sum > 0:
            large_tables = pd.concat([
                large_tables,
                pd.DataFrame([{
                    'Table Name': 'Others',
                    'Rows': small_tables_sum,
                    'Percentage': (small_tables_sum / total_records * 100)
                }])
            ])
        
        fig_pie = create_pie_chart(
            large_tables,
            values='Rows',
            names='Table Name',
            title="Record Distribution Across Tables"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.markdown("### 🔍 Detailed Table Information")
    
    selected_table = st.selectbox("Select a table to view details:", tables)
    
    if selected_table:
        metadata = get_table_metadata(selected_table)
        columns_df = metadata.get('columns', pd.DataFrame())
        
        if not columns_df.empty:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"#### Table: **{selected_table}**")
            with col2:
                st.metric("Total Rows", f"{metadata.get('row_count', 0):,}")
            with col3:
                st.metric("Table Size", metadata.get('size', 'N/A'))
            
            # Column details
            st.markdown("##### 📋 Column Information")
            
            # Format the columns dataframe
            columns_display = columns_df[['ordinal_position', 'column_name', 'data_type', 
                                         'is_nullable', 'column_default', 'is_primary_key']].copy()
            columns_display.columns = ['#', 'Column Name', 'Data Type', 'Nullable', 'Default', 'Primary Key']
            columns_display['Primary Key'] = columns_display['Primary Key'].apply(lambda x: '✓' if x else '')
            columns_display['Nullable'] = columns_display['Nullable'].apply(lambda x: 'Yes' if x == 'YES' else 'No')
            columns_display['Default'] = columns_display['Default'].fillna('-')
            
            st.dataframe(columns_display, use_container_width=True, hide_index=True)
            
            # Indexes
            if metadata.get('indexes'):
                st.markdown("##### 🔑 Indexes")
                indexes_df = pd.DataFrame(metadata['indexes'], columns=['Index Name', 'Definition'])
                st.dataframe(indexes_df, use_container_width=True, hide_index=True)
            
            # Data type distribution
            type_dist = columns_df['data_type'].value_counts()
            fig_types = go.Figure(data=[
                go.Bar(x=type_dist.index, y=type_dist.values,
                      marker_color=COLORS['red'])
            ])
            fig_types.update_layout(
                title=f"Data Type Distribution in {selected_table}",
                xaxis_title="Data Type",
                yaxis_title="Count"
            )
            apply_miva_theme(fig_types)
            st.plotly_chart(fig_types, use_container_width=True)

with tab4:
    st.markdown("### 📈 Database Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create summary statistics
        st.markdown("#### Summary Statistics")
        
        summary_stats = {
            'Metric': ['Average Rows per Table', 'Average Columns per Table', 
                      'Tables with >1000 rows', 'Tables with >10 columns'],
            'Value': [
                f"{df_tables['Rows'].mean():.0f}" if table_data else "0",
                f"{df_tables['Columns'].mean():.1f}" if table_data else "0",
                len(df_tables[df_tables['Rows'] > 1000]) if table_data else 0,
                len(df_tables[df_tables['Columns'] > 10]) if table_data else 0
            ]
        }
        
        st.dataframe(pd.DataFrame(summary_stats), use_container_width=True, hide_index=True)
    
    with col2:
        # Data growth potential
        st.markdown("#### Growth Analysis")
        
        if table_data:
            # Categorize tables by size
            def categorize_size(rows):
                if rows < 100:
                    return 'Small (<100)'
                elif rows < 1000:
                    return 'Medium (100-1K)'
                elif rows < 10000:
                    return 'Large (1K-10K)'
                else:
                    return 'Very Large (>10K)'
            
            df_tables['Size Category'] = df_tables['Rows'].apply(categorize_size)
            category_counts = df_tables['Size Category'].value_counts()
            
            fig_cat = go.Figure(data=[
                go.Pie(labels=category_counts.index, values=category_counts.values,
                      hole=0.3, marker_colors=[COLORS['navy'], COLORS['red'], 
                                              COLORS['light_navy'], COLORS['dark_red']])
            ])
            fig_cat.update_layout(title="Table Size Distribution")
            apply_miva_theme(fig_cat)
            st.plotly_chart(fig_cat, use_container_width=True)

# Footer
st.markdown("---")
st.info("""
**💡 Tips:**
- Click on any table in the Table Details tab to see its structure
- Use the Table Views page for detailed analysis of individual tables
- Navigate to Custom Analysis for writing custom SQL queries
- Check Advanced Analytics for filtered data visualizations
""")
