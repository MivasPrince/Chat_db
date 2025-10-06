import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import os
from io import BytesIO
import xlsxwriter
from utils.database import (
    list_tables, get_table_data, get_table_metadata,
    get_table_count, list_columns
)
from utils.visualizations import (
    create_bar_chart, create_pie_chart, create_line_chart,
    create_histogram, create_heatmap, create_box_plot,
    create_table_summary_card, COLORS
)

# Page configuration
st.set_page_config(
    page_title="Table Views - MIVA Dashboard",
    page_icon="📋",
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
.table-header {{
    background: linear-gradient(135deg, {COLORS['navy']} 0%, #1e3c72 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
}}
.table-card {{
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    border: 1px solid #e0e0e0;
    margin-bottom: 1rem;
    transition: all 0.3s;
    cursor: pointer;
}}
.table-card:hover {{
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
}}
.selected-table {{
    border-left: 4px solid {COLORS['red']};
    background: linear-gradient(90deg, rgba(220,20,60,0.05) 0%, white 100%);
}}
</style>
""", unsafe_allow_html=True)

# Display logo
display_logo()

# Header
st.markdown("""
<div class="table-header">
    <h1 style='color: white; margin: 0;'>📋 Table Views</h1>
    <p style='color: #F5F5F5; margin-top: 0.5rem;'>Detailed analysis and visualization for each table</p>
</div>
""", unsafe_allow_html=True)

# Get available tables
tables = list_tables()

if not tables:
    st.error("No tables found in the database.")
    st.stop()

# Table selection
col1, col2 = st.columns([1, 3])

with col1:
    st.markdown("### 📂 Available Tables")
    
    # Display tables as a list with metrics
    for table in tables:
        try:
            count = get_table_count(table)
            metadata = get_table_metadata(table)
            size = metadata.get('size', 'N/A') if metadata else 'N/A'
            
            # Create clickable table card
            if st.button(
                f"📊 {table}\n{count:,} rows | {size}",
                key=f"btn_{table}",
                use_container_width=True
            ):
                st.session_state.selected_table = table
                st.session_state.table_data = None  # Reset data
        except Exception as e:
            if st.button(f"📊 {table}", key=f"btn_{table}", use_container_width=True):
                st.session_state.selected_table = table
                st.session_state.table_data = None

with col2:
    if 'selected_table' not in st.session_state:
        st.info("👈 Select a table from the left panel to view its details and visualizations.")
    else:
        selected_table = st.session_state.selected_table
        
        # Table header
        st.markdown(f"## 📊 {selected_table}")
        
        # Load table metadata safely
        try:
            metadata = get_table_metadata(selected_table)
            columns_df = list_columns(selected_table)
            
            # Safely get row count
            row_count = metadata.get('row_count', 0) if metadata else 0
            if row_count == 0:
                row_count = get_table_count(selected_table)
            
            # Display table statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Rows", f"{row_count:,}")
            with col2:
                st.metric("Total Columns", len(columns_df) if not columns_df.empty else 0)
            with col3:
                st.metric("Table Size", metadata.get('size', 'N/A') if metadata else 'N/A')
            with col4:
                pk_count = len(columns_df[columns_df['is_primary_key'] == True]) if not columns_df.empty else 0
                st.metric("Primary Keys", pk_count)
            
        except Exception as e:
            st.warning(f"Could not load metadata: {e}")
            row_count = 1000  # Default value
            columns_df = pd.DataFrame()
        
        st.markdown("---")
        
        # Data loading section
        st.markdown("### 📥 Load Data")
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            # Fixed slider with safe values
            max_rows = min(10000, row_count) if row_count > 0 else 10000
            default_rows = min(1000, max_rows)
            
            # Use number input instead of slider to avoid the error
            rows_to_load = st.number_input(
                "Number of rows to load:",
                min_value=100,
                max_value=max_rows,
                value=default_rows,
                step=100,
                help=f"Maximum available: {row_count:,} rows"
            )
        
        with col2:
            load_btn = st.button("🔄 Load Data", use_container_width=True)
        
        with col3:
            if st.button("🔄 Refresh Metadata", use_container_width=True):
                st.rerun()
        
        if load_btn:
            with st.spinner(f"Loading {rows_to_load} rows from {selected_table}..."):
                try:
                    df = get_table_data(selected_table, int(rows_to_load))
                    if not df.empty:
                        st.session_state.table_data = df
                        st.success(f"✅ Loaded {len(df)} rows successfully!")
                    else:
                        st.error("Failed to load data or table is empty.")
                except Exception as e:
                    st.error(f"Error loading data: {e}")
        
        # Display data and visualizations if loaded
        if 'table_data' in st.session_state and st.session_state.table_data is not None:
            df = st.session_state.table_data
            
            # Create tabs for different views
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Data Preview", "📊 Visualizations", "📈 Statistics", 
                "🔍 Column Analysis", "🗂️ Schema"
            ])
            
            with tab1:
                st.markdown("### 📋 Data Preview")
                
                # Search/filter functionality
                search_col, filter_col = st.columns([2, 1])
                
                with search_col:
                    search_term = st.text_input("🔍 Search in data:", "")
                
                with filter_col:
                    columns_to_show = st.multiselect(
                        "Select columns:",
                        df.columns.tolist(),
                        default=df.columns.tolist()[:min(10, len(df.columns))]  # Show first 10 columns by default
                    )
                
                # Apply search filter
                display_df = df[columns_to_show] if columns_to_show else df
                
                if search_term:
                    mask = display_df.astype(str).apply(
                        lambda x: x.str.contains(search_term, case=False, na=False)
                    ).any(axis=1)
                    display_df = display_df[mask]
                
                # Display data
                st.dataframe(display_df, use_container_width=True)
                
                # Display info
                st.info(f"Showing {len(display_df)} rows × {len(display_df.columns)} columns")
                
                # Export options
                st.markdown("### 💾 Export Data")
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download as CSV",
                        data=csv,
                        file_name=f"{selected_table}_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    # Excel export
                    try:
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            display_df.to_excel(writer, sheet_name=selected_table[:31], index=False)  # Sheet name max 31 chars
                            
                            # Get the workbook and worksheet
                            workbook = writer.book
                            worksheet = writer.sheets[selected_table[:31]]
                            
                            # Add a format for headers
                            header_format = workbook.add_format({
                                'bold': True,
                                'bg_color': '#000080',
                                'font_color': 'white',
                                'border': 1
                            })
                            
                            # Write the headers
                            for col_num, value in enumerate(display_df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                        
                        excel_data = output.getvalue()
                        
                        st.download_button(
                            "📥 Download as Excel",
                            data=excel_data,
                            file_name=f"{selected_table}_data.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Error creating Excel file: {e}")
            
            with tab2:
                st.markdown("### 📊 Automatic Visualizations")
                
                numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
                
                # Numeric visualizations
                if numeric_cols:
                    st.markdown("#### Numeric Column Analysis")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if len(numeric_cols) >= 1:
                            selected_num = st.selectbox("Select numeric column:", numeric_cols)
                            if selected_num:
                                fig_hist = create_histogram(
                                    df, selected_num,
                                    title=f"Distribution of {selected_num}"
                                )
                                st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with col2:
                        if len(numeric_cols) >= 2:
                            # Correlation heatmap for numeric columns
                            fig_heatmap = create_heatmap(
                                df[numeric_cols],
                                title="Correlation Matrix"
                            )
                            if fig_heatmap:
                                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                # Categorical visualizations
                if categorical_cols:
                    st.markdown("#### Categorical Column Analysis")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        selected_cat = st.selectbox("Select categorical column:", categorical_cols)
                        if selected_cat:
                            value_counts = df[selected_cat].value_counts().head(10)
                            fig_bar = create_bar_chart(
                                pd.DataFrame({'Category': value_counts.index, 'Count': value_counts.values}),
                                'Count', 'Category',
                                title=f"Top 10 {selected_cat} Values"
                            )
                            fig_bar.update_traces(orientation='h')
                            st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with col2:
                        if selected_cat:
                            fig_pie = create_pie_chart(
                                pd.DataFrame({'Category': value_counts.index[:5], 'Count': value_counts.values[:5]}),
                                'Count', 'Category',
                                title=f"Top 5 {selected_cat} Distribution"
                            )
                            st.plotly_chart(fig_pie, use_container_width=True)
                
                # Time series if date columns exist
                if date_cols and numeric_cols:
                    st.markdown("#### Time Series Analysis")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        date_col = st.selectbox("Date column:", date_cols)
                        value_col = st.selectbox("Value column:", numeric_cols)
                    
                    with col2:
                        if date_col and value_col:
                            # Aggregate by date
                            df_time = df.groupby(df[date_col].dt.date)[value_col].mean().reset_index()
                            df_time.columns = [date_col, value_col]
                            
                            fig_line = create_line_chart(
                                df_time, date_col, value_col,
                                title=f"Average {value_col} over Time"
                            )
                            st.plotly_chart(fig_line, use_container_width=True)
            
            with tab3:
                st.markdown("### 📈 Statistical Summary")
                
                # Basic statistics
                st.markdown("#### Descriptive Statistics")
                st.dataframe(df.describe(), use_container_width=True)
                
                # Additional statistics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Data Quality Metrics")
                    quality_metrics = {
                        'Metric': [
                            'Total Records',
                            'Complete Records',
                            'Records with Nulls',
                            'Duplicate Records',
                            'Unique Records',
                            'Data Completeness'
                        ],
                        'Value': [
                            len(df),
                            len(df.dropna()),
                            len(df) - len(df.dropna()),
                            len(df) - len(df.drop_duplicates()),
                            len(df.drop_duplicates()),
                            f"{(len(df.dropna()) / len(df) * 100):.2f}%"
                        ]
                    }
                    st.dataframe(pd.DataFrame(quality_metrics), use_container_width=True, hide_index=True)
                
                with col2:
                    st.markdown("#### Memory Usage")
                    memory_usage = df.memory_usage(deep=True)
                    memory_df = pd.DataFrame({
                        'Column': memory_usage.index,
                        'Memory (KB)': (memory_usage.values / 1024).round(2)
                    })
                    st.dataframe(memory_df, use_container_width=True, hide_index=True)
                    
                    total_memory = memory_usage.sum() / 1024 / 1024
                    st.metric("Total Memory Usage", f"{total_memory:.2f} MB")
            
            with tab4:
                st.markdown("### 🔍 Column Analysis")
                
                selected_column = st.selectbox("Select a column to analyze:", df.columns.tolist())
                
                if selected_column:
                    col_data = df[selected_column]
                    col_dtype = str(col_data.dtype)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("#### Basic Info")
                        st.metric("Data Type", col_dtype)
                        st.metric("Non-Null Count", col_data.notna().sum())
                        st.metric("Null Count", col_data.isna().sum())
                        st.metric("Null Percentage", f"{(col_data.isna().sum() / len(col_data) * 100):.2f}%")
                    
                    with col2:
                        st.markdown("#### Unique Values")
                        st.metric("Unique Count", col_data.nunique())
                        st.metric("Unique Percentage", f"{(col_data.nunique() / len(col_data) * 100):.2f}%")
                        
                        if col_data.dtype in ['object', 'category']:
                            value_counts = col_data.value_counts()
                            if not value_counts.empty:
                                most_common = value_counts.iloc[0]
                                st.metric("Most Common", f"{value_counts.index[0]} ({most_common})")
                    
                    with col3:
                        if col_data.dtype in [np.number]:
                            st.markdown("#### Statistics")
                            st.metric("Mean", f"{col_data.mean():.2f}")
                            st.metric("Median", f"{col_data.median():.2f}")
                            st.metric("Std Dev", f"{col_data.std():.2f}")
                            st.metric("Range", f"{col_data.min():.2f} - {col_data.max():.2f}")
            
            with tab5:
                st.markdown("### 🗂️ Table Schema")
                
                if not columns_df.empty:
                    # Format schema information
                    schema_df = columns_df.copy()
                    schema_df['Primary Key'] = schema_df['is_primary_key'].apply(lambda x: '🔑' if x else '')
                    schema_df['Nullable'] = schema_df['is_nullable'].apply(lambda x: '✅' if x == 'YES' else '❌')
                    
                    # Clean up default values
                    schema_df['column_default'] = schema_df['column_default'].fillna('-')
                    schema_df['column_default'] = schema_df['column_default'].apply(
                        lambda x: str(x)[:50] + '...' if len(str(x)) > 50 else str(x)
                    )
                    
                    # Select and rename columns for display
                    display_schema = schema_df[[
                        'ordinal_position', 'column_name', 'data_type',
                        'Nullable', 'column_default', 'Primary Key'
                    ]]
                    display_schema.columns = [
                        'Position', 'Column Name', 'Data Type',
                        'Nullable', 'Default Value', 'PK'
                    ]
                    
                    st.dataframe(display_schema, use_container_width=True, hide_index=True)
        
        else:
            st.info("👆 Click 'Load Data' to view table contents and generate visualizations.")

# Footer
st.markdown("---")
st.info("""
**💡 Tips:**
- Select a table from the left panel to view its details
- Load data to enable visualizations and analysis
- Use the different tabs to explore various aspects of the table
- Export data in CSV or Excel format for external analysis
- Column Analysis tab provides detailed statistics for individual columns
""")

st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    <p>© 2025 MIVA Open University. All rights reserved.</p>
</div>
""", unsafe_allow_html=True)
