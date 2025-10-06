import streamlit as st
import os
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO

# Load environment variables
load_dotenv()

# Import custom modules
from utils.auth import check_authentication
from utils.database import get_connection, test_connection

# Page configuration
st.set_page_config(
    page_title="MIVA Data Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for branding
def load_custom_css():
    st.markdown("""
    <style>
    /* Main header styling */
    .main-header {
        background: linear-gradient(135deg, #000080 0%, #1e3c72 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Logo container */
    .logo-container {
        background-color: #000080;
        padding: 1.5rem;
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    /* Card styling */
    .metric-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #DC143C;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #DC143C;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #B91C3C;
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #F5F5F5;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .stError {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
    }
    
    /* Table styling */
    .dataframe {
        border: 1px solid #dee2e6;
        border-radius: 5px;
    }
    
    /* Headers */
    h1 {
        color: #000080;
        font-weight: 700;
    }
    
    h2, h3 {
        color: #1e3c72;
        font-weight: 600;
    }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F5F5F5;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #000080;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #DC143C !important;
        color: white !important;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

def load_logo():
    """Load and display MIVA logo"""
    try:
        # Try to load from local file first
        if os.path.exists("assets/miva_logo.png"):
            logo = Image.open("assets/miva_logo.png")
        else:
            # Download from URL if not available locally
            response = requests.get("https://miva.edu.ng/wp-content/uploads/2023/05/Miva-Logo-White-Vertical-1.png")
            logo = Image.open(BytesIO(response.content))
            
            # Save for future use
            os.makedirs("assets", exist_ok=True)
            logo.save("assets/miva_logo.png")
        
        # Display logo with navy background
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            st.image(logo, width=300)
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Could not load logo: {e}")

def initialize_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'db_connected' not in st.session_state:
        st.session_state.db_connected = False

def main():
    """Main application"""
    # Initialize session state
    initialize_session_state()
    
    # Load custom CSS
    load_custom_css()
    
    # Check authentication
    if not st.session_state.authenticated:
        # Display logo
        load_logo()
        
        # Login page
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>MIVA Open University</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #F5F5F5;'>Data Monitoring & Evaluation Dashboard</h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Login form
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("login_form"):
                st.markdown("### 🔐 Login")
                username = st.text_input("Username", placeholder="Enter username")
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if check_authentication(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        
                        # Test database connection
                        if test_connection():
                            st.session_state.db_connected = True
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error("⚠️ Login successful but database connection failed. Please check configuration.")
                    else:
                        st.error("❌ Invalid username or password")
    
    else:
        # Main application after login
        # Sidebar
        with st.sidebar:
            # Logo in sidebar
            st.markdown('<div style="background-color: #000080; padding: 1rem; border-radius: 10px;">', unsafe_allow_html=True)
            try:
                if os.path.exists("assets/miva_logo.png"):
                    logo = Image.open("assets/miva_logo.png")
                    st.image(logo, use_column_width=True)
            except:
                pass
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("---")
            
            # User info
            st.markdown(f"### 👤 Welcome, {st.session_state.username}")
            
            # Database connection status
            if st.session_state.db_connected:
                st.success("🟢 Database Connected")
            else:
                st.error("🔴 Database Disconnected")
            
            st.markdown("---")
            
            # Navigation menu
            st.markdown("### 📍 Navigation")
            st.markdown("""
            - **📊 Overview**: Database summary and statistics
            - **🔍 Custom Analysis**: SQL query interface
            - **📈 Advanced Analytics**: Filtered visualizations
            - **📋 Table Views**: Individual table analysis
            """)
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.db_connected = False
                st.rerun()
        
        # Main content area
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: white;'>📊 MIVA Data Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #F5F5F5;'>Monitoring & Evaluation System</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Welcome message and instructions
        st.markdown("## Welcome to MIVA Data Dashboard")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h3>📊 Overview</h3>
                <p>Get a comprehensive view of all database tables and their statistics.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <h3>🔍 Custom Analysis</h3>
                <p>Write custom SQL queries and export results to CSV or Excel.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <h3>📈 Advanced Analytics</h3>
                <p>Filter and analyze data with interactive visualizations.</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick stats (if connected to database)
        if st.session_state.db_connected:
            st.markdown("### 📊 Quick Statistics")
            
            try:
                from utils.database import get_table_stats
                stats = get_table_stats()
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Tables", stats.get('table_count', 0))
                
                with col2:
                    st.metric("Total Columns", stats.get('total_columns', 0))
                
                with col3:
                    st.metric("Total Records", f"{stats.get('total_records', 0):,}")
                
                with col4:
                    st.metric("Database Size", stats.get('db_size', 'N/A'))
                    
            except Exception as e:
                st.warning(f"Could not load statistics: {e}")
        
        st.markdown("---")
        
        # Instructions
        st.info("""
        **Getting Started:**
        1. Use the sidebar to navigate between different sections
        2. **Overview** - View summary statistics and metadata for all tables
        3. **Custom Analysis** - Write and execute custom SQL queries
        4. **Advanced Analytics** - Use filters to generate specific visualizations
        5. **Table Views** - Access dedicated visualization pages for each table
        
        Select a page from the sidebar to begin your analysis.
        """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>© 2024 MIVA Open University. All rights reserved.</p>
            <p>Data Monitoring & Evaluation Dashboard v1.0</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
