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
    
    /* Logo container with Navy background */
    .logo-container {

        padding: 2rem;
        border-radius: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    /* Sidebar logo container */
    .sidebar-logo-container {

        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    
    /* Card styling */
    .metric-card {
        background-color: #000080;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #DC143C;
        margin-bottom: 1rem;
        transition: all 0.3s;
        cursor: pointer;
        text-decoration: none;
        display: block;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .metric-card h3 {
        color: #000080;
        margin: 0 0 0.5rem 0;
    }
    
    .metric-card p {
        color: #666;
        margin: 0;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #DC143C;
        color: #000080;
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
        background-color: #000080;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
    }
    
    .stError {
        background-color: #000080;
        border-color: #000080;
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
        background-color: #000080;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #000080;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #DC143C !important;
        color: #000080 !important;
        border-radius: 5px;
    }
    
    /* Link cards */
    .link-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #DC143C;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s;
        cursor: pointer;
        margin-bottom: 1rem;
    }
    
    .link-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    a {
        text-decoration: none;
    }
    </style>
    """, unsafe_allow_html=True)

def load_logo():
    """Load and display MIVA logo with Navy background"""
    try:
        # Try to load from local file first
        if os.path.exists("assets/miva_logo.png"):
            logo = Image.open("assets/miva_logo.png")
        else:
            # Download from URL if not available locally
            response = requests.get(""https://raw.githubusercontent.com/MivasPrince/Chat_db/refs/heads/main/assets/miva.png"")
            logo = Image.open(BytesIO(response.content))
            
            # Save for future use
            os.makedirs("assets", exist_ok=True)
            logo.save("assets/miva_logo.png")
        
        # Create a navy background for the logo
        # Get logo dimensions
        logo_width, logo_height = logo.size
        
        # Create a new image with navy background
        background_width = logo_width + 100  # Add padding
        background_height = logo_height + 100  # Add padding
        background = Image.new('RGBA', (background_width, background_height), (0, 0, 128, 255))  # Navy blue
        
        # Calculate position to center logo on background
        x = (background_width - logo_width) // 2
        y = (background_height - logo_height) // 2
        
        # Paste logo onto navy background
        background.paste(logo, (x, y), logo if logo.mode == 'RGBA' else None)
        
        # Display the combined image
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(background, width=400)
            
    except Exception as e:
        st.error(f"Could not load logo: {e}")

def display_sidebar_logo():
    """Display logo in sidebar with Navy background"""
    try:
        if os.path.exists("assets/miva_logo.png"):
            logo = Image.open("assets/miva_logo.png")
        else:
            # Try to download if not exists
            response = requests.get(""https://raw.githubusercontent.com/MivasPrince/Chat_db/refs/heads/main/assets/miva.png"")
            logo = Image.open(BytesIO(response.content))
            os.makedirs("assets", exist_ok=True)
            logo.save("assets/miva_logo.png")
        
        # Create a navy background for the logo
        logo_width, logo_height = logo.size
        
        # Create a new image with navy background (smaller padding for sidebar)
        background_width = logo_width + 40  # Less padding for sidebar
        background_height = logo_height + 40
        background = Image.new('RGBA', (background_width, background_height), (0, 0, 128, 255))  # Navy blue
        
        # Calculate position to center logo on background
        x = (background_width - logo_width) // 2
        y = (background_height - logo_height) // 2
        
        # Paste logo onto navy background
        background.paste(logo, (x, y), logo if logo.mode == 'RGBA' else None)
        
        # Display the combined image
        st.image(background, use_column_width=True)
    except:
        pass

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
        st.markdown("<h1 style='text-align: center; color: #000080;'>MIVA Open University</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #000080;'>Data Monitoring & Evaluation Dashboard</h3>", unsafe_allow_html=True)
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
        # Sidebar with logo
        with st.sidebar:
            # Logo with Navy background in sidebar
            display_sidebar_logo()
            
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
            Use the pages below to navigate:
            - **Overview**: Database summary and statistics
            - **Custom Analysis**: SQL query interface
            - **Advanced Analytics**: Filtered visualizations
            - **Table Views**: Individual table analysis
            """)
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.db_connected = False
                st.rerun()
        
        # Main content area
        # Display logo at top with Navy background
        col1, col2, col3 = st.columns([2, 3, 2])
        with col2:
            try:
                if os.path.exists("assets/miva_logo.png"):
                    logo = Image.open("assets/miva_logo.png")
                    st.markdown('<div class="sidebar-logo-container" style="text-align: center;">', unsafe_allow_html=True)
                    st.image(logo, width=200)
                    st.markdown('</div>', unsafe_allow_html=True)
            except:
                pass
        
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #000080;'>📊 MIVA Data Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #000080;'>Monitoring & Evaluation System</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Welcome message and navigation links
        st.markdown("## Welcome to MIVA Data Dashboard")
        
        # Create clickable navigation cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Go to Overview", use_container_width=True, key="nav_overview"):
                st.switch_page("pages/1_Overview.py")
            st.markdown("""
            <div class="link-card">
                <h4 style="color: #000080; margin: 0;">📊 Overview</h4>
                <p style="color: #666; margin-top: 0.5rem;">Get a comprehensive view of all database tables and their statistics.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("🔍 Go to Custom Analysis", use_container_width=True, key="nav_custom"):
                st.switch_page("pages/2_Custom_Analysis.py")
            st.markdown("""
            <div class="link-card">
                <h4 style="color: #000080; margin: 0;">🔍 Custom Analysis</h4>
                <p style="color: #666; margin-top: 0.5rem;">Write custom SQL queries and export results to CSV or Excel.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("📈 Go to Advanced Analytics", use_container_width=True, key="nav_advanced"):
                st.switch_page("pages/3_Advanced_Analytics.py")
            st.markdown("""
            <div class="link-card">
                <h4 style="color: #000080; margin: 0;">📈 Advanced Analytics</h4>
                <p style="color: #666; margin-top: 0.5rem;">Filter and analyze data with interactive visualizations.</p>
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
        1. Click on any of the navigation cards above to access specific features
        2. **Overview** - View summary statistics and metadata for all tables
        3. **Custom Analysis** - Write and execute custom SQL queries
        4. **Advanced Analytics** - Use filters to generate specific visualizations
        5. **Table Views** - Access dedicated visualization pages for each table
        
        You can also use the sidebar to navigate between different sections.
        """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center; color: #666;'>
            <p>© 2025 MIVA Open University. All rights reserved.</p>
            <p>Data Monitoring & Evaluation Dashboard v1.0</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
