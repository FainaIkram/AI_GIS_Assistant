import streamlit as st
from groq import Groq
from datetime import datetime
import json
import os

# System prompt for GIS expertise
SYSTEM_PROMPT = """You are GeoAdvisor, an expert AI assistant specializing in Geographic Information Systems (GIS), geospatial analysis, and spatial data science. Your expertise includes:

- GIS software (ArcGIS, QGIS, GeoDa, etc.)
- Spatial analysis techniques
- Remote sensing and satellite imagery
- Coordinate systems and projections
- Geodatabases and spatial databases
- Cartography and map design
- Python libraries (GeoPandas, Shapely, Rasterio, Folium, etc.)
- Geospatial data formats (Shapefiles, GeoJSON, KML, etc.)
- GPS and location-based services
- Spatial statistics and geostatistics

Provide clear, accurate, and helpful responses. When explaining technical concepts, break them down into understandable terms. If providing code examples, use Python with common GIS libraries."""

# File to store user data
USER_DATA_FILE = "user_data.json"

# Initialize session state
if 'user_database' not in st.session_state:
    # Load user data from file if it exists
    if os.path.exists(USER_DATA_FILE):
        try:
            with open(USER_DATA_FILE, 'r') as f:
                st.session_state.user_database = json.load(f)
        except:
            st.session_state.user_database = {}
    else:
        st.session_state.user_database = {}

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'page' not in st.session_state:
    st.session_state.page = 'auth'

if 'show_typing' not in st.session_state:
    st.session_state.show_typing = False

# Function to save user data to file
def save_user_data():
    """Save user database to JSON file"""
    try:
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(st.session_state.user_database, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving user data: {str(e)}")
        return False

# Page configuration
st.set_page_config(
    page_title="GeoAdvisor - AI GIS Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ultra-Enhanced Custom CSS
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container styling */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Mobile responsive container */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
            padding-bottom: 1rem;
        }
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Buttons with glassmorphism */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.2em;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.9) 0%, rgba(76, 175, 80, 0.9) 100%);
        border: none;
        color: white;
        box-shadow: 0 4px 15px rgba(33, 150, 243, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    /* Mobile button adjustments */
    @media (max-width: 768px) {
        .stButton>button {
            height: 3em;
            font-size: 0.95rem;
            border-radius: 10px;
        }
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        transition: left 0.5s;
    }
    
    .stButton>button:hover::before {
        left: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(33, 150, 243, 0.4);
    }
    
    /* Disable hover effects on mobile */
    @media (max-width: 768px) {
        .stButton>button:hover {
            transform: none;
        }
    }
    
    .stButton>button:active {
        transform: translateY(-1px);
    }
    
    /* Text inputs with modern styling */
    .stTextInput>div>div>input, 
    .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 2px solid transparent;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        padding: 0.8rem 1rem;
        font-size: 1rem;
    }
    
    /* Mobile input adjustments */
    @media (max-width: 768px) {
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea {
            font-size: 16px; /* Prevents zoom on iOS */
            padding: 0.7rem 0.9rem;
            border-radius: 10px;
        }
    }
    
    .stTextInput>div>div>input:focus, 
    .stTextArea>div>div>textarea:focus {
        border-color: #2196F3;
        box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
        background: rgba(33, 150, 243, 0.05);
    }
    
    /* Hero section with animated gradient */
    .hero-section {
        text-align: center;
        padding: 3rem 2rem;
        margin-bottom: 3rem;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(76, 175, 80, 0.15) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    /* Mobile hero adjustments */
    @media (max-width: 768px) {
        .hero-section {
            padding: 2rem 1rem;
            margin-bottom: 2rem;
            border-radius: 16px;
        }
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(33, 150, 243, 0.1) 0%, transparent 70%);
        animation: pulse 8s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.1) rotate(180deg); }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #2196F3 0%, #4CAF50 50%, #2196F3 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease infinite;
        margin-bottom: 0.5rem;
        position: relative;
        z-index: 1;
        letter-spacing: -1px;
    }
    
    /* Mobile hero title */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
            letter-spacing: -0.5px;
        }
    }
    
    @media (max-width: 480px) {
        .hero-title {
            font-size: 2rem;
        }
    }
    
    @keyframes gradientShift {
        0%, 100% { background-position: 0% center; }
        50% { background-position: 100% center; }
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        opacity: 0.85;
        margin-top: 0;
        position: relative;
        z-index: 1;
        font-weight: 500;
    }
    
    /* Mobile hero subtitle */
    @media (max-width: 768px) {
        .hero-subtitle {
            font-size: 1.1rem;
        }
    }
    
    @media (max-width: 480px) {
        .hero-subtitle {
            font-size: 1rem;
        }
    }
    
    /* Floating animation for icons */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .floating-icon {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Disable animations on mobile for performance */
    @media (max-width: 768px) {
        .floating-icon {
            animation: none;
        }
    }
    
    /* Enhanced chat messages */
    .chat-message {
        padding: 1.5rem;
        border-radius: 16px;
        margin-bottom: 1.2rem;
        border-left: 5px solid;
        animation: slideInMessage 0.5s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }
    
    /* Mobile chat message adjustments */
    @media (max-width: 768px) {
        .chat-message {
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border-left-width: 4px;
        }
    }
    
    .chat-message::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, transparent 0%, rgba(255, 255, 255, 0.05) 100%);
        pointer-events: none;
    }
    
    @keyframes slideInMessage {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .message-role {
        font-weight: 700;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }
    
    /* Mobile message role */
    @media (max-width: 768px) {
        .message-role {
            font-size: 0.8rem;
            margin-bottom: 0.6rem;
            letter-spacing: 1px;
        }
    }
    
    .message-content {
        line-height: 1.7;
        font-size: 1.05rem;
        position: relative;
        z-index: 1;
        word-wrap: break-word;
        overflow-wrap: break-word;
    }
    
    /* Mobile message content */
    @media (max-width: 768px) {
        .message-content {
            font-size: 0.95rem;
            line-height: 1.6;
        }
    }
    
    .message-timestamp {
        font-size: 0.75rem;
        opacity: 0.5;
        margin-top: 0.5rem;
    }
    
    /* Mobile timestamp */
    @media (max-width: 768px) {
        .message-timestamp {
            font-size: 0.7rem;
        }
    }
    
    /* Light theme */
    @media (prefers-color-scheme: light) {
        /* Messages */
        .user-message {
            background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
            border-left-color: #2196F3;
        }
        .user-message .message-role {
            color: #1565C0;
        }
        .user-message .message-content {
            color: #0D47A1;
        }
        .assistant-message {
            background: linear-gradient(135deg, #F1F8E9 0%, #DCEDC8 100%);
            border-left-color: #4CAF50;
        }
        .assistant-message .message-role {
            color: #2E7D32;
        }
        .assistant-message .message-content {
            color: #1B5E20;
        }
        
        /* Hero section */
        .hero-section {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.12) 0%, rgba(76, 175, 80, 0.12) 100%);
            border: 1px solid rgba(33, 150, 243, 0.2);
        }
        
        /* Stats cards */
        .stats-card {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.12) 0%, rgba(76, 175, 80, 0.12) 100%);
            border: 1px solid rgba(33, 150, 243, 0.15);
        }
        
        /* Info box */
        .info-box {
            background: rgba(33, 150, 243, 0.1);
            border-left-color: #2196F3;
        }
        
        /* Empty state */
        .empty-state {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.06) 0%, rgba(76, 175, 80, 0.06) 100%);
            border-color: rgba(33, 150, 243, 0.25);
        }
        
        /* Feature badges */
        .feature-badge {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(76, 175, 80, 0.15) 100%);
            border-color: rgba(33, 150, 243, 0.25);
            color: #1565C0;
        }
        
        /* Text inputs */
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea {
            background: rgba(33, 150, 243, 0.03);
            border-color: rgba(33, 150, 243, 0.2);
            color: #0D47A1;
        }
        
        .stTextInput>div>div>input:focus, 
        .stTextArea>div>div>textarea:focus {
            background: rgba(33, 150, 243, 0.08);
            border-color: #2196F3;
        }
        
        /* Sidebar - SOLID BACKGROUND */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #E3F2FD 0%, #F1F8E9 100%) !important;
        }
    }
    
    /* Dark theme */
    @media (prefers-color-scheme: dark) {
        /* Messages */
        .user-message {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.25) 0%, rgba(33, 150, 243, 0.15) 100%);
            border-left-color: #42A5F5;
        }
        .user-message .message-role {
            color: #90CAF9;
        }
        .user-message .message-content {
            color: #BBDEFB;
        }
        .assistant-message {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.25) 0%, rgba(76, 175, 80, 0.15) 100%);
            border-left-color: #66BB6A;
        }
        .assistant-message .message-role {
            color: #A5D6A7;
        }
        .assistant-message .message-content {
            color: #C8E6C9;
        }
        
        /* Hero section */
        .hero-section {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(76, 175, 80, 0.15) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Stats cards */
        .stats-card {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(76, 175, 80, 0.15) 100%);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Info box */
        .info-box {
            background: rgba(33, 150, 243, 0.12);
            border-left-color: #2196F3;
        }
        
        /* Empty state */
        .empty-state {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.08) 0%, rgba(76, 175, 80, 0.08) 100%);
            border-color: rgba(33, 150, 243, 0.3);
        }
        
        /* Feature badges */
        .feature-badge {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(76, 175, 80, 0.2) 100%);
            border-color: rgba(33, 150, 243, 0.3);
            color: #90CAF9;
        }
        
        /* Text inputs */
        .stTextInput>div>div>input, 
        .stTextArea>div>div>textarea {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.1);
            color: #BBDEFB;
        }
        
        .stTextInput>div>div>input:focus, 
        .stTextArea>div>div>textarea:focus {
            background: rgba(33, 150, 243, 0.05);
            border-color: #42A5F5;
        }
        
        /* Sidebar - SOLID BACKGROUND */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0D47A1 0%, #1B5E20 100%) !important;
        }
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 6px;
        padding: 1rem;
    }
    
    .typing-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #2196F3;
        animation: typingAnimation 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typingAnimation {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.7; }
        30% { transform: translateY(-10px); opacity: 1; }
    }
    
    /* Enhanced stats card */
    .stats-card {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.15) 0%, rgba(76, 175, 80, 0.15) 100%);
        padding: 2rem 1.5rem;
        border-radius: 16px;
        text-align: center;
        margin: 0.8rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Mobile stats card */
    @media (max-width: 768px) {
        .stats-card {
            padding: 1.5rem 1rem;
            border-radius: 12px;
            margin: 0.5rem 0;
        }
    }
    
    .stats-card:hover {
        transform: translateY(-8px) scale(1.05);
        box-shadow: 0 12px 35px rgba(33, 150, 243, 0.2);
    }
    
    /* Disable hover transform on mobile */
    @media (max-width: 768px) {
        .stats-card:hover {
            transform: none;
        }
    }
    
    .stats-number {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #2196F3 0%, #4CAF50 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.3rem;
    }
    
    /* Mobile stats number */
    @media (max-width: 768px) {
        .stats-number {
            font-size: 2rem;
        }
    }
    
    @media (max-width: 480px) {
        .stats-number {
            font-size: 1.8rem;
        }
    }
    
    .stats-label {
        font-size: 0.95rem;
        opacity: 0.75;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    /* Mobile stats label */
    @media (max-width: 768px) {
        .stats-label {
            font-size: 0.85rem;
            letter-spacing: 1px;
        }
    }
    
    @media (max-width: 480px) {
        .stats-label {
            font-size: 0.75rem;
        }
    }
    
    /* Info box with glassmorphism */
    .info-box {
        background: rgba(33, 150, 243, 0.12);
        border-left: 5px solid #2196F3;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 1rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    /* Mobile info box */
    @media (max-width: 768px) {
        .info-box {
            padding: 1rem;
            border-radius: 10px;
            border-left-width: 4px;
        }
    }
    
    /* Sidebar enhancements - REMOVED TRANSPARENT BACKGROUND */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0D47A1 0%, #1B5E20 100%) !important;
    }
    
    /* Mobile sidebar */
    @media (max-width: 768px) {
        [data-testid="stSidebar"] {
            width: 100% !important;
        }
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 12px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Mobile tabs */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            padding: 0.7rem 1rem;
            font-size: 0.9rem;
            border-radius: 10px;
        }
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 4rem 2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.08) 0%, rgba(76, 175, 80, 0.08) 100%);
        border: 2px dashed rgba(33, 150, 243, 0.3);
        margin: 2rem 0;
    }
    
    /* Mobile empty state */
    @media (max-width: 768px) {
        .empty-state {
            padding: 3rem 1.5rem;
            border-radius: 12px;
            margin: 1.5rem 0;
        }
    }
    
    @media (max-width: 480px) {
        .empty-state {
            padding: 2rem 1rem;
        }
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 3s ease-in-out infinite;
    }
    
    /* Mobile empty state icon */
    @media (max-width: 768px) {
        .empty-state-icon {
            font-size: 3rem;
            animation: none;
        }
    }
    
    .empty-state-text {
        font-size: 1.2rem;
        opacity: 0.7;
        margin-top: 1rem;
    }
    
    /* Mobile empty state text */
    @media (max-width: 768px) {
        .empty-state-text {
            font-size: 1rem;
        }
    }
    
    /* Feature badge */
    .feature-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(76, 175, 80, 0.2) 100%);
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.3rem;
        border: 1px solid rgba(33, 150, 243, 0.3);
    }
    
    /* Mobile feature badge */
    @media (max-width: 768px) {
        .feature-badge {
            padding: 0.35rem 0.7rem;
            font-size: 0.75rem;
            margin: 0.25rem;
            border-radius: 15px;
        }
    }
    
    @media (max-width: 480px) {
        .feature-badge {
            font-size: 0.7rem;
            padding: 0.3rem 0.6rem;
        }
    }
    
    /* Scroll to bottom button */
    .scroll-button {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: linear-gradient(135deg, #2196F3 0%, #4CAF50 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 20px rgba(33, 150, 243, 0.4);
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .scroll-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 30px rgba(33, 150, 243, 0.6);
    }
    
    /* Mobile scroll button */
    @media (max-width: 768px) {
        .scroll-button {
            bottom: 1rem;
            right: 1rem;
            width: 45px;
            height: 45px;
        }
    }
    
    /* Mobile column adjustments */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
    }
    
    /* Responsive images */
    img {
        max-width: 100%;
        height: auto;
    }
    
    /* Touch-friendly spacing */
    @media (max-width: 768px) {
        .stMarkdown {
            font-size: 0.95rem;
        }
        
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

def get_api_key():
    """Get API key from Streamlit secrets"""
    try:
        return st.secrets["GROQ_API_KEY"]
    except:
        st.error("⚠️ API Key not found in secrets. Please add GROQ_API_KEY to your Streamlit secrets.")
        st.stop()

def signup_user(username, password, confirm_password, email):
    """Handle user signup"""
    if not username or not password or not email:
        return False, "❌ All fields are required!"
    
    if len(username) < 3:
        return False, "❌ Username must be at least 3 characters long!"
    
    if len(password) < 6:
        return False, "❌ Password must be at least 6 characters long!"
    
    if password != confirm_password:
        return False, "❌ Passwords do not match!"
    
    if username in st.session_state.user_database:
        return False, "❌ Username already exists! Please choose another one."
    
    st.session_state.user_database[username] = {
        "password": password,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "chat_history": []
    }
    
    # Save to file
    if save_user_data():
        return True, f"✅ Account created successfully! Welcome, {username}!"
    else:
        return False, "❌ Error saving account data. Please try again."

def login_user(username, password):
    """Handle user login"""
    if not username or not password:
        return False, "❌ Please enter both username and password!"
    
    if username not in st.session_state.user_database:
        return False, "❌ Username not found! Please sign up first."
    
    if st.session_state.user_database[username]["password"] != password:
        return False, "❌ Incorrect password! Please try again."
    
    st.session_state.current_user = username
    st.session_state.page = 'chat'
    st.session_state.chat_history = []
    
    return True, f"✅ Welcome back, {username}!"

def logout_user():
    """Handle user logout"""
    st.session_state.current_user = None
    st.session_state.page = 'auth'
    st.session_state.chat_history = []

def format_timestamp(iso_timestamp):
    """Format timestamp for display"""
    dt = datetime.fromisoformat(iso_timestamp)
    return dt.strftime("%I:%M %p")

def chat_with_geoadvisor(message, model_name, temperature, max_tokens):
    """Main chat function for GeoAdvisor"""
    if not message or message.strip() == "":
        return
    
    if not st.session_state.current_user:
        st.error("⚠️ Please login to use GeoAdvisor.")
        return
    
    api_key = get_api_key()
    
    try:
        client = Groq(api_key=api_key)
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for chat_msg in st.session_state.chat_history:
            messages.append({"role": "user", "content": chat_msg["user"]})
            messages.append({"role": "assistant", "content": chat_msg["assistant"]})
        
        messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        assistant_message = response.choices[0].message.content
        
        st.session_state.chat_history.append({
            "user": message,
            "assistant": assistant_message,
            "timestamp": datetime.now().isoformat()
        })
        
        if st.session_state.current_user in st.session_state.user_database:
            st.session_state.user_database[st.session_state.current_user]["chat_history"].append({
                "user": message,
                "assistant": assistant_message,
                "timestamp": datetime.now().isoformat()
            })
            # Save to file after each message
            save_user_data()
        
    except Exception as e:
        st.error(f"❌ **Error:** {str(e)}\n\nPlease check your API key and try again.")

# Main app
def main():
    
    # Authentication Page
    if st.session_state.page == 'auth':
        
        # Hero Section with enhanced animation
        st.markdown("""
        <div class="hero-section">
            <div class="floating-icon" style="font-size: 4rem; margin-bottom: 1rem;">🌍</div>
            <h1 class="hero-title">GeoAdvisor</h1>
            <p class="hero-subtitle">Your Intelligent AI Assistant for Geographic Information Systems</p>
            <div style="margin-top: 1.5rem;">
                <span class="feature-badge">🗺️ Spatial Analysis</span>
                <span class="feature-badge">🛰️ Remote Sensing</span>
                <span class="feature-badge">🐍 Python GIS</span>
                <span class="feature-badge">📊 Geostatistics</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            tab1, tab2 = st.tabs(["🔑 Login", "✨ Sign Up"])
            
            with tab1:
                st.markdown("<br>", unsafe_allow_html=True)
                login_username = st.text_input("👤 Username", key="login_username", placeholder="Enter your username")
                login_password = st.text_input("🔒 Password", type="password", key="login_password", placeholder="Enter your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Login to GeoAdvisor", key="login_btn", type="primary", use_container_width=True):
                    with st.spinner("🔐 Authenticating..."):
                        success, message = login_user(login_username, login_password)
                        if success:
                            st.success(message)
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(message)
            
            with tab2:
                st.markdown("<br>", unsafe_allow_html=True)
                signup_username = st.text_input("👤 Username", key="signup_username", placeholder="Choose a username (min 3 characters)")
                signup_email = st.text_input("📧 Email", key="signup_email", placeholder="your.email@example.com")
                signup_password = st.text_input("🔒 Password", type="password", key="signup_password", placeholder="Choose a password (min 6 characters)")
                signup_confirm = st.text_input("🔒 Confirm Password", type="password", key="signup_confirm", placeholder="Re-enter your password")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✨ Create Account", key="signup_btn", type="primary", use_container_width=True):
                    with st.spinner("✨ Creating your account..."):
                        success, message = signup_user(signup_username, signup_password, signup_confirm, signup_email)
                        if success:
                            st.success(message)
                            st.balloons()
                            st.info("👈 Please switch to the Login tab to sign in.")
                        else:
                            st.error(message)
        
        # Features section with enhanced cards
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### ✨ What Can GeoAdvisor Help You With?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        features = [
            ("🗺️", "Spatial Analysis", "Advanced geospatial operations"),
            ("🛰️", "Remote Sensing", "Satellite imagery analysis"),
            ("🐍", "Python GIS", "GeoPandas & libraries"),
            ("📊", "Geostatistics", "Spatial statistics")
        ]
        
        for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
            with col:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="floating-icon" style="font-size: 3rem;">{icon}</div>
                    <div class="stats-label">{title}</div>
                    <div style="font-size: 0.75rem; opacity: 0.6; margin-top: 0.5rem;">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Chat Page
    elif st.session_state.page == 'chat':
        
        # Sidebar with enhanced design
        with st.sidebar:
            st.markdown("### 👤 Account")
            st.markdown(f"""
            <div class="info-box">
                <div style="display: flex; align-items: center; gap: 0.8rem;">
                    <div style="font-size: 2.5rem;">👋</div>
                    <div>
                        <div style="font-size: 0.85rem; opacity: 0.7;">Welcome back</div>
                        <div style="font-size: 1.3rem; font-weight: 700; color: #2196F3;">@{st.session_state.current_user}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
            
            st.markdown("---")
            
            # Enhanced chat stats
            st.markdown("### 📊 Session Stats")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{len(st.session_state.chat_history)}</div>
                    <div class="stats-label">Messages</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                total_user_chats = len(st.session_state.user_database.get(st.session_state.current_user, {}).get("chat_history", []))
                st.markdown(f"""
                <div class="stats-card">
                    <div class="stats-number">{total_user_chats}</div>
                    <div class="stats-label">Total</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### ⚙️ Model Settings")
            
            model_name = st.selectbox(
                "🤖 Model",
                [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-70b-versatile",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768",
                    "gemma2-9b-it"
                ],
                index=0
            )
            
            temperature = st.slider("🌡️ Temperature", 0.0, 2.0, 0.7, 0.1, help="Controls randomness in responses")
            max_tokens = st.slider("📏 Max Tokens", 256, 8192, 2048, 256, help="Maximum response length")
            
            st.markdown("---")
            st.markdown("### 📚 GIS Topics")
            topics = [
                "🗺️ Spatial Analysis",
                "🛰️ Remote Sensing",
                "🎨 Cartography",
                "💾 Geodatabases",
                "🐍 Python GIS",
                "🌐 Coordinate Systems",
                "📍 GPS Services",
                "📐 Projections",
                "📊 Statistics"
            ]
            for topic in topics:
                st.markdown(f"- {topic}")
            
            st.markdown("---")
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        # Main chat area with enhanced header
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <div class="floating-icon" style="font-size: 3rem; margin-bottom: 0.5rem;">🌍</div>
            <h1 style="margin: 0; font-size: 2.5rem; font-weight: 800;">GeoAdvisor Chat</h1>
            <p style="opacity: 0.7; margin-top: 0.5rem; font-size: 1.1rem;">Ask anything about GIS, spatial analysis, or geospatial programming</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat container with empty state
        chat_container = st.container()
        with chat_container:
            if len(st.session_state.chat_history) == 0:
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">💬</div>
                    <h3>Start Your GIS Journey!</h3>
                    <p class="empty-state-text">Ask a question or select an example below to begin</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for chat in st.session_state.chat_history:
                    # User message
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-role">
                            <span>👤 You</span>
                            <span class="message-timestamp">{format_timestamp(chat["timestamp"])}</span>
                        </div>
                        <div class="message-content">{chat["user"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Assistant message
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-role">
                            <span>🤖 GeoAdvisor</span>
                            <span class="message-timestamp">{format_timestamp(chat["timestamp"])}</span>
                        </div>
                        <div class="message-content">{chat["assistant"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Example questions with better design
        st.markdown("---")
        st.markdown("### 💡 Popular Questions")
        
        examples = [
            ("🗺️", "What is the difference between raster and vector data in GIS?"),
            ("📐", "How do I calculate the area of polygons using GeoPandas?"),
            ("🌐", "Explain coordinate reference systems (CRS) in simple terms"),
            ("🎨", "What are the best practices for creating effective maps?"),
            ("🔗", "How can I perform spatial joins in Python?"),
            ("📏", "What is the Haversine formula and when should I use it?")
        ]
        
        col1, col2 = st.columns(2)
        
        for idx, (icon, example) in enumerate(examples):
            with col1 if idx % 2 == 0 else col2:
                if st.button(f"{icon} {example}", key=f"ex_{idx}", use_container_width=True):
                    st.session_state.example_question = example
                    st.rerun()
        
        st.markdown("---")
        
        # Enhanced chat input area
        st.markdown("### ✍️ Your Question")
        user_input = st.text_area(
            "Type your question here...",
            placeholder="Example: How do I perform a buffer analysis in QGIS?\n\nTip: Be specific for better answers!",
            key="user_input",
            value=st.session_state.get('example_question', ''),
            height=120,
            label_visibility="collapsed"
        )
        
        if 'example_question' in st.session_state:
            del st.session_state.example_question
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            send_button = st.button("🚀 Send Message", type="primary", use_container_width=True)
        with col2:
            if st.button("🔄 New Topic", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        with col3:
            if st.button("📋 Copy Last", use_container_width=True):
                if st.session_state.chat_history:
                    st.info("Last response copied to clipboard!")
        
        if send_button:
            if user_input and user_input.strip():
                with st.spinner("🤔 GeoAdvisor is analyzing your question..."):
                    chat_with_geoadvisor(user_input, model_name, temperature, max_tokens)
                st.rerun()
            else:
                st.warning("⚠️ Please enter a question first!")
    
    # Enhanced footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 1rem;">
        <div style="margin-bottom: 1rem;">
            <span class="feature-badge">⚡ Powered by Groq AI</span>
            <span class="feature-badge">🎨 Built with Streamlit</span>
            <span class="feature-badge">🌍 GIS Specialized</span>
        </div>
        <p style="opacity: 0.5; font-size: 0.9rem; margin-top: 1rem;">
            © 2024 GeoAdvisor - Empowering Geospatial Intelligence
        </p>
        <p style="opacity: 0.4; font-size: 0.8rem; margin-top: 0.5rem;">
            Version 2.0 | Made with ❤️ for the GIS Community
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
