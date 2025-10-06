import streamlit as st
import pandas as pd
from io import BytesIO
import xlsxwriter
from utils.database import execute_query, list_tables
from utils.visualizations import COLORS

# Page configuration
st.set_page_config(
    page_title="Custom Analysis - MIVA Dashboard",
    page_icon="🔍",
    layout="wide"
)

# Check authentication
if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.error("Please login from the main page to access this section.")
    st.stop()

# Custom CSS
st.markdown(f"""
<style>
.sql-header {{
    background: linear-gradient(135deg, {COLORS['navy']} 0%, #1e3c72 100%);
    padding: 2rem;
    border-radius: 10px;
    margin-bottom: 2rem;
    color: white;
}}
.query-box {{
    background-color: #f8f9fa;
    border: 2px solid {COLORS['navy']};
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}}
.export-section {{
    background-color: {COLORS['ash']};
    padding: 1.5rem;
    border-radius: 10px;
    margin-top: 1rem;
}}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="sql-header">
    <h1 style='color: white; margin: 0;'>🔍 Custom SQL Analysis</h1>
    <p style='color: #F5F5F5; margin-top: 0.5rem;'>Write custom queries and export results</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state for query history
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# Sidebar with quick templates
with st.sidebar:
    st.markdown("### 📝 Query Templates")
    
    tables = list_tables()
    
    if tables:
        selected_table = st.selectbox("Select table for template:", tables)
        
        templates = {
            "Select All": f"SELECT * FROM {selected_table} LIMIT 100;",
            "Count Records": f"SELECT COUNT(*) as total_records FROM {selected_table};",
            "Group By Template": f"SELECT column_name, COUNT(*) as count\nFROM {selected_table}\nGROUP BY column_name\nORDER BY count DESC;",
            "Filter Template": f"SELECT *\nFROM {selected_table}\nWHERE column_name = 'value'\nLIMIT 100;",
            "Join Template": f"SELECT t1.*, t2.column\nFROM {selected_table} t1\nJOIN other_table t2 ON t1.id = t2.id\nLIMIT 100;",
            "Aggregate Functions": f"SELECT \n  COUNT(*) as count,\n  AVG(numeric_column) as average,\n  MAX(numeric_column) as maximum,\n  MIN(numeric_column) as minimum\nFROM {selected_table};",
            "Date Filter": f"SELECT *\nFROM {selected_table}\nWHERE date_column >= '2024-01-01'\n  AND date_column <= '2024-12-31'\nORDER BY date_column DESC;"
        }
        
        template_choice = st.selectbox("Choose a template:", list(templates.keys()))
        
        if st.button("📋 Use Template", use_container_width=True):
            st.session_state.current_query = templates[template_choice]

# Main content area
tab1, tab2, tab3 = st.tabs(["✍️ Query Editor", "📜 Query History", "📚 SQL Reference"])

with tab1:
    # Query input area
    st.markdown("### 📝 SQL Query Editor")
    
    # Initialize query from session state or empty
    query = st.text_area(
        "Enter your SQL query:",
        value=st.session_state.get('current_query', ''),
        height=200,
        placeholder="SELECT * FROM table_name LIMIT 10;",
        key="query_input"
    )
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        execute_btn = st.button("▶️ Execute Query", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)
    with col3:
        format_btn = st.button("📐 Format", use_container_width=True)
    with col4:
        save_btn = st.button("💾 Save Query", use_container_width=True)
    
    if clear_btn:
        st.session_state.current_query = ""
        st.rerun()
    
    if format_btn and query:
        # Basic SQL formatting
        formatted = query.upper().replace('SELECT', 'SELECT\n  ')
        formatted = formatted.replace(',', ',\n  ')
        formatted = formatted.replace('FROM', '\nFROM')
        formatted = formatted.replace('WHERE', '\nWHERE')
        formatted = formatted.replace('GROUP BY', '\nGROUP BY')
        formatted = formatted.replace('ORDER BY', '\nORDER BY')
        formatted = formatted.replace('LIMIT', '\nLIMIT')
        st.session_state.current_query = formatted
        st.rerun()
    
    if save_btn and query:
        st.session_state.query_history.append({
            'query': query,
            'timestamp': pd.Timestamp.now()
        })
        st.success("✅ Query saved to history!")
    
    # Execute query
    if execute_btn and query:
        with st.spinner("Executing query..."):
            try:
                result_df, message = execute_query(query)
                
                if message == "success" and not result_df.empty:
                    st.success(f"✅ Query executed successfully! Found {len(result_df)} rows.")
                    st.session_state.last_result = result_df
                    
                    # Display results
                    st.markdown("### 📊 Query Results")
                    
                    # Show data info
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Rows", len(result_df))
                    with col2:
                        st.metric("Columns", len(result_df.columns))
                    with col3:
                        st.metric("Memory", f"{result_df.memory_usage(deep=True).sum() / 1024:.2f} KB")
                    
                    # Display dataframe
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Export section
                    st.markdown('<div class="export-section">', unsafe_allow_html=True)
                    st.markdown("### 💾 Export Options")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # CSV export
                        csv = result_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Excel export
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            result_df.to_excel(writer, sheet_name='Query Results', index=False)
                            
                            # Format the Excel file
                            workbook = writer.book
                            worksheet = writer.sheets['Query Results']
                            
                            # Add header format
                            header_format = workbook.add_format({
                                'bold': True,
                                'bg_color': COLORS['navy'],
                                'font_color': 'white',
                                'border': 1
                            })
                            
                            for col_num, value in enumerate(result_df.columns.values):
                                worksheet.write(0, col_num, value, header_format)
                        
                        excel_data = output.getvalue()
                        st.download_button(
                            label="📥 Download as Excel",
                            data=excel_data,
                            file_name="query_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    with col3:
                        # JSON export
                        json_str = result_df.to_json(orient='records', indent=2)
                        st.download_button(
                            label="📥 Download as JSON",
                            data=json_str,
                            file_name="query_results.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add to history
                    st.session_state.query_history.append({
                        'query': query,
                        'timestamp': pd.Timestamp.now(),
                        'rows': len(result_df),
                        'status': 'success'
                    })
                    
                elif message == "success" and result_df.empty:
                    st.warning("Query executed successfully but returned no results.")
                else:
                    st.info(message)
                    
            except Exception as e:
                st.error(f"❌ Error executing query: {str(e)}")
                st.session_state.query_history.append({
                    'query': query,
                    'timestamp': pd.Timestamp.now(),
                    'status': 'error',
                    'error': str(e)
                })

with tab2:
    st.markdown("### 📜 Query History")
    
    if st.session_state.query_history:
        # Convert to dataframe for display
        history_df = pd.DataFrame(st.session_state.query_history)
        
        # Display in reverse order (most recent first)
        for idx, row in history_df.iloc[::-1].iterrows():
            with st.expander(f"Query {len(history_df) - idx}: {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
                st.code(row['query'], language='sql')
                
                if 'status' in row:
                    if row['status'] == 'success':
                        st.success(f"✅ Success - {row.get('rows', 'N/A')} rows returned")
                    else:
                        st.error(f"❌ Error: {row.get('error', 'Unknown error')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"📋 Copy Query", key=f"copy_{idx}"):
                        st.session_state.current_query = row['query']
                        st.rerun()
                with col2:
                    if st.button(f"🗑️ Remove", key=f"remove_{idx}"):
                        st.session_state.query_history.pop(len(history_df) - idx - 1)
                        st.rerun()
        
        if st.button("🗑️ Clear All History"):
            st.session_state.query_history = []
            st.rerun()
    else:
        st.info("No queries in history yet. Execute a query to see it here.")

with tab3:
    st.markdown("### 📚 SQL Reference Guide")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### Basic SQL Commands
        
        **SELECT** - Retrieve data
        ```sql
        SELECT column1, column2 
        FROM table_name
        WHERE condition;
        ```
        
        **JOIN** - Combine tables
        ```sql
        SELECT * FROM table1
        INNER JOIN table2
        ON table1.id = table2.id;
        ```
        
        **GROUP BY** - Group results
        ```sql
        SELECT column, COUNT(*)
        FROM table
        GROUP BY column;
        ```
        
        **ORDER BY** - Sort results
        ```sql
        SELECT * FROM table
        ORDER BY column ASC/DESC;
        ```
        """)
    
    with col2:
        st.markdown("""
        #### Aggregate Functions
        
        - **COUNT()** - Count rows
        - **SUM()** - Sum values
        - **AVG()** - Average value
        - **MAX()** - Maximum value
        - **MIN()** - Minimum value
        
        #### Common Filters
        
        - **WHERE** column = value
        - **WHERE** column **LIKE** '%pattern%'
        - **WHERE** column **IN** (value1, value2)
        - **WHERE** column **BETWEEN** value1 **AND** value2
        - **WHERE** column **IS NULL**
        - **WHERE** column **IS NOT NULL**
        
        #### Date Functions
        
        - **CURRENT_DATE** - Today's date
        - **DATE_PART**('year', date_column)
        - **DATE_TRUNC**('month', date_column)
        """)
    
    st.markdown("---")
    
    st.markdown("""
    #### 💡 Query Best Practices
    
    1. **Always use LIMIT** when exploring data to avoid loading too many rows
    2. **Use specific column names** instead of SELECT * for better performance
    3. **Add indexes** on columns frequently used in WHERE clauses
    4. **Use JOIN** instead of subqueries when possible
    5. **Test queries** on small datasets first
    6. **Comment complex queries** for documentation
    
    #### ⚠️ Safety Tips
    
    - Be careful with **UPDATE** and **DELETE** statements
    - Always include a **WHERE** clause with DELETE/UPDATE
    - Use **transactions** for multiple related operations
    - **Backup data** before major modifications
    """)

# Footer
st.markdown("---")
st.info("""
**💡 Tips:**
- Use the templates in the sidebar for quick query generation
- Save frequently used queries to history
- Export results in your preferred format (CSV, Excel, JSON)
- Check the SQL Reference tab for syntax help
""")
