import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import io

# Page configuration
st.set_page_config(
    page_title="MIVA Open University - M&E Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for MIVA branding
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

# Database configuration
DB_CONFIG = {
    "host": "16.170.143.253",
    "port": 5432,
    "user": "admin",
    "password": "password123",
    "database": "miva_ai_db"
}

# Authentication
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_credentials(username, password):
    return username == "miva_admin" and hash_password(password) == hash_password("password")

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

# Database functions
@st.cache_data(ttl=300)
def load_table_data(table_name, limit=None):
    query = f"SELECT * FROM {table_name}"
    if limit:
        query += f" LIMIT {limit}"
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql(query, conn)

@st.cache_data(ttl=300)
def execute_custom_query(query):
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql(query, conn)

@st.cache_data(ttl=300)
def get_table_stats():
    with psycopg2.connect(**DB_CONFIG) as conn:
        cursor = conn.cursor()
        tables = ['chat_feedback', 'chat_sessions', 'chat_messages', 'otp_verifications', 'user_feedback', 'conversation_history']
        stats = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            except:
                stats[table] = 0
        return stats

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

# Main dashboard
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
        show_chat_feedback()
    elif page == "🗨️ Chat Sessions":
        show_chat_sessions()
    elif page == "📝 Chat Messages":
        show_chat_messages()
    elif page == "🔐 OTP Verifications":
        show_otp_verifications()
    elif page == "⭐ User Feedback":
        show_user_feedback()
    elif page == "📜 Conversation History":
        show_conversation_history()
    elif page == "🔍 Custom Analysis":
        show_custom_analysis()
    elif page == "📈 Advanced Analytics":
        show_advanced_analytics()

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
    
    with col1:
        df_feedback = load_table_data("chat_feedback")
        if 'created_at' in df_feedback.columns and len(df_feedback) > 0:
            df_feedback['created_at'] = pd.to_datetime(df_feedback['created_at'])
            df_feedback['date'] = df_feedback['created_at'].dt.date
            daily_feedback = df_feedback.groupby('date').size().reset_index(name='count')
            
            fig = px.line(daily_feedback, x='date', y='count', 
                         title='Daily Feedback Trend',
                         color_discrete_sequence=['#d32f2f'])
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'feedback_type' in df_feedback.columns and len(df_feedback) > 0:
            feedback_dist = df_feedback['feedback_type'].value_counts()
            fig = px.pie(values=feedback_dist.values, names=feedback_dist.index,
                        title='Feedback Type Distribution',
                        color_discrete_sequence=['#1a237e', '#d32f2f', '#9e9e9e'])
            st.plotly_chart(fig, use_container_width=True)

def show_chat_feedback():
    st.markdown('<div class="table-header"><h2>💬 Chat Feedback Analysis</h2></div>', unsafe_allow_html=True)
    df = load_table_data("chat_feedback")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Feedback", len(df))
    with col2:
        avg_rating = df['rating'].mean() if 'rating' in df.columns and len(df) > 0 else 0
        st.metric("Avg Rating", f"{avg_rating:.2f}")
    with col3:
        thumbs_up = len(df[df['feedback_type'] == 'thumbs_up']) if 'feedback_type' in df.columns else 0
        st.metric("Thumbs Up", thumbs_up)
    with col4:
        thumbs_down = len(df[df['feedback_type'] == 'thumbs_down']) if 'feedback_type' in df.columns else 0
        st.metric("Thumbs Down", thumbs_down)
    
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"chat_feedback_{datetime.now().strftime('%Y%m%d')}.csv")
    with col2:
        st.download_button("📥 Download Excel", to_excel(df), f"chat_feedback_{datetime.now().strftime('%Y%m%d')}.xlsx")

def show_chat_sessions():
    st.markdown('<div class="table-header"><h2>🗨️ Chat Sessions Analysis</h2></div>', unsafe_allow_html=True)
    df = load_table_data("chat_sessions")
    st.metric("Total Sessions", len(df))
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"chat_sessions_{datetime.now().strftime('%Y%m%d')}.csv")
    with col2:
        st.download_button("📥 Download Excel", to_excel(df), f"chat_sessions_{datetime.now().strftime('%Y%m%d')}.xlsx")

def show_chat_messages():
    st.markdown('<div class="table-header"><h2>📝 Chat Messages Analysis</h2></div>', unsafe_allow_html=True)
    df = load_table_data("chat_messages", limit=5000)
    st.metric("Total Messages", len(df))
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"chat_messages_{datetime.now().strftime('%Y%m%d')}.csv")
    with col2:
        st.download_button("📥 Download Excel", to_excel(df), f"chat_messages_{datetime.now().strftime('%Y%m%d')}.xlsx")

def show_otp_verifications():
    st.markdown('<div class="table-header"><h2>🔐 OTP Verifications</h2></div>', unsafe_allow_html=True)
    df = load_table_data("otp_verifications")
    st.metric("Total OTPs", len(df))
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"otp_verifications_{datetime.now().strftime('%Y%m%d')}.csv")
    with col2:
        st.download_button("📥 Download Excel", to_excel(df), f"otp_verifications_{datetime.now().strftime('%Y%m%d')}.xlsx")

def show_user_feedback():
    st.markdown('<div class="table-header"><h2>⭐ User Feedback</h2></div>', unsafe_allow_html=True)
    df = load_table_data("user_feedback")
    st.metric("Total Feedback", len(df))
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"user_feedback_{datetime.now().strftime('%Y%m%d')}.csv")
    with col2:
        st.download_button("📥 Download Excel", to_excel(df), f"user_feedback_{datetime.now().strftime('%Y%m%d')}.xlsx")

def show_conversation_history():
    st.markdown('<div class="table-header"><h2>📜 Conversation History</h2></div>', unsafe_allow_html=True)
    df = load_table_data("conversation_history", limit=1000)
    st.metric("Total Conversations", len(df))
    st.dataframe(df, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("📥 Download CSV", df.to_csv(index=False), f"conversation_history_{datetime.now().strftime('%Y%m%d')}.csv")
    with col2:
        st.download_button("📥 Download Excel", to_excel(df), f"conversation_history_{datetime.now().strftime('%Y%m%d')}.xlsx")

def show_custom_analysis():
    st.markdown('<div class="table-header"><h2>🔍 Custom SQL Analysis</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Create Custom Queries
    **Available Tables:** chat_feedback, chat_sessions, chat_messages, otp_verifications, user_feedback, conversation_history
    """)
    
    sample_queries = {
        "Select All Feedback": "SELECT * FROM chat_feedback LIMIT 100",
        "Average Rating by Date": "SELECT DATE(created_at) as date, AVG(rating) as avg_rating FROM chat_feedback GROUP BY DATE(created_at) ORDER BY date DESC",
        "Top Users": "SELECT email, COUNT(*) as count FROM chat_feedback GROUP BY email ORDER BY count DESC LIMIT 10"
    }
    
    selected = st.selectbox("Sample Queries:", ["Custom"] + list(sample_queries.keys()))
    query = st.text_area("SQL Query:", value=sample_queries.get(selected, "SELECT * FROM chat_feedback LIMIT 100"), height=150)
    
    if st.button("🚀 Execute Query"):
        try:
            result_df = execute_custom_query(query)
            st.success(f"✅ {len(result_df)} rows returned")
            st.dataframe(result_df, use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("📥 CSV", result_df.to_csv(index=False), f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            with col2:
                st.download_button("📥 Excel", to_excel(result_df), f"query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def show_advanced_analytics():
    st.markdown('<div class="table-header"><h2>📈 Advanced Analytics</h2></div>', unsafe_allow_html=True)
    
    df = load_table_data("chat_feedback")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        users = ['All'] + df['email'].unique().tolist() if 'email' in df.columns else ['All']
        selected_user = st.selectbox("Filter by User", users)
    with col2:
        ratings = ['All'] + sorted(df['rating'].unique().tolist()) if 'rating' in df.columns else ['All']
        selected_rating = st.selectbox("Filter by Rating", ratings)
    with col3:
        types = ['All'] + df['feedback_type'].unique().tolist() if 'feedback_type' in df.columns else ['All']
        selected_type = st.selectbox("Filter by Type", types)
    
    filtered = df.copy()
    if selected_user != 'All' and 'email' in df.columns:
        filtered = filtered[filtered['email'] == selected_user]
    if selected_rating != 'All' and 'rating' in df.columns:
        filtered = filtered[filtered['rating'] == selected_rating]
    if selected_type != 'All' and 'feedback_type' in df.columns:
        filtered = filtered[filtered['feedback_type'] == selected_type]
    
    st.subheader(f"Filtered Results: {len(filtered)} records")
    
    if len(filtered) > 0 and 'rating' in filtered.columns:
        fig = px.histogram(filtered, x='rating', title='Rating Distribution', color_discrete_sequence=['#1a237e'])
        st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(filtered, use_container_width=True)

# Main app logic
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page()
else:
    main_dashboard()
