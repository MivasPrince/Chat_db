# app.py

import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import io

# --- Page Configuration ---
st.set_page_config(
    page_title="MIVA Open University - M&E Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for MIVA Branding ---
st.markdown("""
<style>
    :root {
        --miva-navy: #1a237e;
        --miva-red: #d32f2f;
        --miva-ash: #9e9e9e;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--miva-navy) 0%, var(--miva-red) 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .logo-container {
        background-color: var(--miva-navy);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid var(--miva-red);
        margin-bottom: 1rem;
    }
    
    .stButton>button {
        background-color: var(--miva-navy);
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 500;
    }
    
    .stButton>button:hover {
        background-color: var(--miva-red);
    }
    
    .table-header {
        background-color: var(--miva-navy);
        color: white;
        padding: 1rem;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Authentication ---
def hash_password(password):
    """Hashes password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    """Validates credentials against secrets.toml."""
    try:
        correct_username = (username == st.secrets["auth"]["username"])
        correct_password = (hash_password(password) == st.secrets["auth"]["hashed_password"])
        return correct_username and correct_password
    except Exception:
        st.error("Authentication configuration missing in secrets.toml.")
        return False

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="logo-container">
            <img src="https://miva.edu.ng/wp-content/uploads/2023/05/Miva-Logo-White-Vertical-1.png" width="200">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="main-header">
            <h2>Monitoring & Evaluation Dashboard</h2>
            <p>AI Chatbot Analytics & Insights</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Please Login")
        username = st.text_input("Username", key="username")
        password = st.text_input("Password", type="password", key="password")
        
        if st.button("Login", use_container_width=True):
            if check_credentials(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")

# --- Database Functions ---
@st.cache_data(ttl=300)
def load_table_data(table_name, limit=None):
    """Loads data from a table using credentials from st.secrets."""
    query = f'SELECT * FROM public."{table_name}"'
    if limit:
        query += f" LIMIT {limit}"
    try:
        with psycopg2.connect(**st.secrets["database"]) as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def execute_custom_query(query):
    """Executes a custom read-only query."""
    try:
        with psycopg2.connect(**st.secrets["database"]) as conn:
            return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Query Error: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_table_stats():
    """Gets row counts for all tables."""
    tables = ['chat_feedback', 'chat_sessions', 'chat_messages', 'otp_verifications', 'user_feedback', 'conversation_history']
    stats = {}
    try:
        with psycopg2.connect(**st.secrets["database"]) as conn:
            cursor = conn.cursor()
            for table in tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM public."{table}"')
                    stats[table] = cursor.fetchone()[0]
                except psycopg2.Error:
                    stats[table] = 0
            return stats
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return {table: 0 for table in tables}

@st.cache_data
def to_excel(df):
    """Converts DataFrame to Excel file in memory."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# --- Generic Page Function ---
def create_table_page(table_name, title, emoji):
    """Generic function to display a table, metrics, and download buttons."""
    st.markdown(f'<div class="table-header"><h2>{emoji} {title}</h2></div>', unsafe_allow_html=True)
    limit = 5000 if table_name in ["chat_messages", "conversation_history"] else None
    df = load_table_data(table_name, limit=limit)

    if df.empty:
        st.warning(f"No data available in the '{table_name}' table.")
        return

    st.metric(f"Total Records Displayed", f"{len(df):,}")
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"{table_name}_{datetime.now().strftime('%Y%m%d')}.csv")
    with col2:
        st.download_button("📥 Download Excel", to_excel(df), f"{table_name}_{datetime.now().strftime('%Y%m%d')}.xlsx")


# --- Page Implementations ---
def show_overview():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Overview</h1>
        <p>Comprehensive view of all database tables and key metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    stats = get_table_stats()
    
    st.subheader("📈 Database Summary")
    cols = st.columns(3)
    
    table_names = {
        'chat_feedback': ('💬 Chat Feedback', '#d32f2f'),
        'chat_sessions': ('🗨️ Chat Sessions', '#1a237e'),
        'chat_messages': ('📝 Messages', '#f57c00'),
        'otp_verifications': ('🔐 OTP Verifications', '#388e3c'),
        'user_feedback': ('⭐ User Feedback', '#7b1fa2'),
        'conversation_history': ('📜 Conversations', '#0288d1')
    }
    
    for idx, (table, count) in enumerate(stats.items()):
        with cols[idx % 3]:
            name, color = table_names.get(table, (table, '#9e9e9e'))
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {color}">
                <h3>{name}</h3>
                <h2 style="color: {color}">{count:,}</h2>
                <p>Total Records</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    df_feedback = load_table_data("chat_feedback")
    if not df_feedback.empty:
        with col1:
            if 'created_at' in df_feedback.columns:
                df_feedback['created_at'] = pd.to_datetime(df_feedback['created_at'])
                df_feedback['date'] = df_feedback['created_at'].dt.date
                daily_feedback = df_feedback.groupby('date').size().reset_index(name='count')
                fig = px.line(daily_feedback, x='date', y='count', title='Daily Feedback Trend', color_discrete_sequence=['#d32f2f'])
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if 'feedback_type' in df_feedback.columns:
                feedback_dist = df_feedback['feedback_type'].value_counts()
                fig = px.pie(values=feedback_dist.values, names=feedback_dist.index, title='Feedback Type Distribution', color_discrete_sequence=['#1a237e', '#d32f2f', '#9e9e9e'])
                st.plotly_chart(fig, use_container_width=True)

def show_custom_analysis():
    st.markdown('<div class="table-header"><h2>🔍 Custom SQL Analysis</h2></div>', unsafe_allow_html=True)
    
    st.warning("️️⚠️ **Security Advisory:** This feature runs live SQL queries. For security, connect to the database with a **read-only user** to prevent accidental or malicious data modification or deletion.", icon="🚨")
    
    st.markdown("""
    **Available Tables:** `chat_feedback`, `chat_sessions`, `chat_messages`, `otp_verifications`, `user_feedback`, `conversation_history`
    """)
    
    sample_query = "SELECT email, rating, feedback_type \nFROM public.chat_feedback \nWHERE rating < 3 \nLIMIT 100;"
    query = st.text_area("SQL Query:", value=sample_query, height=150)
    
    if st.button("🚀 Execute Query"):
        result_df = execute_custom_query(query)
        if not result_df.empty:
            st.success(f"✅ Query returned {len(result_df)} rows.")
            st.dataframe(result_df, use_container_width=True)
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 CSV", result_df.to_csv(index=False), f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            with col2:
                st.download_button("📥 Excel", to_excel(result_df), f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        else:
            st.info("Query executed, but returned no data.")

def show_advanced_analytics():
    st.markdown('<div class="table-header"><h2>📈 Advanced Analytics (Chat Feedback)</h2></div>', unsafe_allow_html=True)
    
    df = load_table_data("chat_feedback")
    if df.empty:
        st.warning("No chat feedback data available for analysis.")
        return
        
    col1, col2, col3 = st.columns(3)
    with col1:
        users = ['All'] + df['email'].unique().tolist() if 'email' in df.columns else ['All']
        selected_user = st.selectbox("Filter by User Email", users)
    with col2:
        ratings = ['All'] + sorted(df['rating'].dropna().unique().tolist()) if 'rating' in df.columns else ['All']
        selected_rating = st.selectbox("Filter by Rating", ratings)
    with col3:
        types = ['All'] + df['feedback_type'].unique().tolist() if 'feedback_type' in df.columns else ['All']
        selected_type = st.selectbox("Filter by Feedback Type", types)
    
    filtered_df = df.copy()
    if selected_user != 'All':
        filtered_df = filtered_df[filtered_df['email'] == selected_user]
    if selected_rating != 'All':
        filtered_df = filtered_df[filtered_df['rating'] == selected_rating]
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['feedback_type'] == selected_type]
    
    st.subheader(f"Filtered Results: {len(filtered_df)} records")
    
    if not filtered_df.empty and 'rating' in filtered_df.columns:
        fig = px.histogram(filtered_df, x='rating', nbins=5, title='Rating Distribution', color_discrete_sequence=['#1a237e'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(filtered_df, use_container_width=True)

# --- Main App Router ---
def main_dashboard():
    with st.sidebar:
        st.markdown("""
        <div class="logo-container">
            <img src="https://miva.edu.ng/wp-content/uploads/2023/05/Miva-Logo-White-Vertical-1.png" width="150">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Navigation")
        page = st.selectbox("Select Page", [
            "📊 Overview",
            "💬 Chat Feedback",
            "🗨️ Chat Sessions", 
            "📝 Chat Messages",
            "🔐 OTP Verifications",
            "⭐ User Feedback",
            "📜 Conversation History",
            "---",
            "🔍 Custom Analysis",
            "📈 Advanced Analytics"
        ])
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    if page == "📊 Overview":
        show_overview()
    elif page == "💬 Chat Feedback":
        create_table_page("chat_feedback", "Chat Feedback", "💬")
    elif page == "🗨️ Chat Sessions":
        create_table_page("chat_sessions", "Chat Sessions", "🗨️")
    elif page == "📝 Chat Messages":
        create_table_page("chat_messages", "Chat Messages", "📝")
    elif page == "🔐 OTP Verifications":
        create_table_page("otp_verifications", "OTP Verifications", "🔐")
    elif page == "⭐ User Feedback":
        create_table_page("user_feedback", "User Feedback", "⭐")
    elif page == "📜 Conversation History":
        create_table_page("conversation_history", "Conversation History", "📜")
    elif page == "🔍 Custom Analysis":
        show_custom_analysis()
    elif page == "📈 Advanced Analytics":
        show_advanced_analytics()

# --- App Entry Point ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page()
else:
    main_dashboard()
