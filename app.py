import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib

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
        --miva-red: #DC143C;
        --miva-blue: #1E3A8A;
        --miva-ash: #9CA3AF;
    }
    
    .main-header {
        background: linear-gradient(135deg, var(--miva-blue) 0%, var(--miva-red) 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--miva-red);
    }
    
    .stButton>button {
        background-color: var(--miva-blue);
        color: white;
        border-radius: 5px;
        border: none;
        padding: 0.5rem 2rem;
    }
    
    .stButton>button:hover {
        background-color: var(--miva-red);
    }
    
    .sidebar .sidebar-content {
        background-color: #F3F4F6;
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
        <div class="main-header">
            <h1>🎓 MIVA Open University</h1>
            <h3>Monitoring & Evaluation Dashboard</h3>
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
def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@st.cache_data(ttl=300)
def load_table_data(table_name, limit=None):
    query = f"SELECT * FROM {table_name}"
    if limit:
        query += f" LIMIT {limit}"
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql(query, conn)

@st.cache_data(ttl=300)
def get_feedback_stats():
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql("""
            SELECT 
                feedback_type,
                COUNT(*) as count,
                AVG(rating) as avg_rating
            FROM chat_feedback
            GROUP BY feedback_type
        """, conn)

@st.cache_data(ttl=300)
def get_daily_feedback():
    with psycopg2.connect(**DB_CONFIG) as conn:
        return pd.read_sql("""
            SELECT 
                DATE(created_at) as date,
                COUNT(*) as feedback_count,
                AVG(rating) as avg_rating
            FROM chat_feedback
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 30
        """, conn)

# Main dashboard
def main_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>📊 MIVA Open University</h1>
        <h3>AI Chatbot Monitoring & Evaluation Dashboard</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E3A8A/FFFFFF?text=MIVA", use_container_width=True)
        st.markdown("### Navigation")
        page = st.radio("Select View", 
            ["📈 Overview", "💬 Feedback Analysis", "📊 Detailed Reports", "🔍 Data Explorer"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### Filters")
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # Main content based on selection
    if page == "📈 Overview":
        show_overview()
    elif page == "💬 Feedback Analysis":
        show_feedback_analysis()
    elif page == "📊 Detailed Reports":
        show_detailed_reports()
    else:
        show_data_explorer()

def show_overview():
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    df_feedback = load_table_data("chat_feedback")
    
    with col1:
        st.metric("Total Feedback", len(df_feedback), 
                 delta=f"+{len(df_feedback[df_feedback['created_at'] > (datetime.now() - timedelta(days=7))])}")
    
    with col2:
        avg_rating = df_feedback['rating'].mean() if 'rating' in df_feedback.columns else 0
        st.metric("Average Rating", f"{avg_rating:.2f}/5", 
                 delta=f"{avg_rating - 3:.2f}")
    
    with col3:
        thumbs_up = len(df_feedback[df_feedback['feedback_type'] == 'thumbs_up']) if 'feedback_type' in df_feedback.columns else 0
        st.metric("Positive Feedback", thumbs_up)
    
    with col4:
        thumbs_down = len(df_feedback[df_feedback['feedback_type'] == 'thumbs_down']) if 'feedback_type' in df_feedback.columns else 0
        st.metric("Negative Feedback", thumbs_down)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Feedback Trend Over Time")
        daily_data = get_daily_feedback()
        fig = px.line(daily_data, x='date', y='feedback_count',
                     color_discrete_sequence=['#DC143C'])
        fig.update_layout(xaxis_title="Date", yaxis_title="Feedback Count")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Feedback Distribution")
        stats = get_feedback_stats()
        fig = px.pie(stats, values='count', names='feedback_type',
                    color_discrete_sequence=['#1E3A8A', '#DC143C'])
        st.plotly_chart(fig, use_container_width=True)

def show_feedback_analysis():
    st.header("💬 Feedback Analysis")
    
    df = load_table_data("chat_feedback")
    
    # Rating distribution
    st.subheader("Rating Distribution")
    if 'rating' in df.columns:
        fig = px.histogram(df, x='rating', nbins=5,
                          color_discrete_sequence=['#1E3A8A'])
        fig.update_layout(xaxis_title="Rating", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Comments analysis
    st.subheader("Recent Feedback Comments")
    if 'comment' in df.columns:
        recent_comments = df[df['comment'].notna()].sort_values('created_at', ascending=False).head(10)
        for idx, row in recent_comments.iterrows():
            with st.expander(f"{row['feedback_type']} - Rating: {row['rating']} - {row['created_at']}"):
                st.write(row['comment'])

def show_detailed_reports():
    st.header("📊 Detailed Reports")
    
    tab1, tab2, tab3 = st.tabs(["Chat Sessions", "OTP Analytics", "User Feedback"])
    
    with tab1:
        df_sessions = load_table_data("chat_sessions", limit=100)
        st.dataframe(df_sessions, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sessions", len(df_sessions))
        with col2:
            if 'created_at' in df_sessions.columns:
                df_sessions['created_at'] = pd.to_datetime(df_sessions['created_at'])
                recent = len(df_sessions[df_sessions['created_at'] > (datetime.now() - timedelta(days=7))])
                st.metric("Sessions (Last 7 Days)", recent)
    
    with tab2:
        df_otp = load_table_data("otp_verifications", limit=100)
        st.dataframe(df_otp, use_container_width=True)
    
    with tab3:
        df_user_feedback = load_table_data("user_feedback", limit=100)
        st.dataframe(df_user_feedback, use_container_width=True)

def show_data_explorer():
    st.header("🔍 Data Explorer")
    
    tables = ["chat_feedback", "chat_sessions", "chat_messages", "otp_verifications", "user_feedback"]
    selected_table = st.selectbox("Select Table", tables)
    
    df = load_table_data(selected_table)
    
    st.subheader(f"Table: {selected_table}")
    st.write(f"**Total Records:** {len(df)}")
    st.write(f"**Columns:** {', '.join(df.columns.tolist())}")
    
    st.dataframe(df, use_container_width=True)
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"{selected_table}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Main app logic
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_page()
else:
    main_dashboard()
