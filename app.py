import streamlit as st
from groq import Groq
from datetime import datetime
import json

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

# Initialize session state
if 'user_database' not in st.session_state:
    st.session_state.user_database = {}

if 'current_user' not in st.session_state:
    st.session_state.current_user = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'page' not in st.session_state:
    st.session_state.page = 'auth'

# Page configuration
st.set_page_config(
    page_title="GeoAdvisor - AI GIS Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Main container styling */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Text inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    /* Hero section */
    .hero-section {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        border-radius: 15px;
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%);
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2196F3 0%, #4CAF50 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        opacity: 0.8;
        margin-top: 0;
    }
    
    /* Auth cards */
    .auth-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 2rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 4px solid;
        animation: slideIn 0.3s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .message-role {
        font-weight: 700;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .message-content {
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Light theme */
    @media (prefers-color-scheme: light) {
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
    }
    
    /* Dark theme */
    @media (prefers-color-scheme: dark) {
        .user-message {
            background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(33, 150, 243, 0.1) 100%);
            border-left-color: #42A5F5;
        }
        .user-message .message-role {
            color: #90CAF9;
        }
        .user-message .message-content {
            color: #BBDEFB;
        }
        .assistant-message {
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%);
            border-left-color: #66BB6A;
        }
        .assistant-message .message-role {
            color: #A5D6A7;
        }
        .assistant-message .message-content {
            color: #C8E6C9;
        }
    }
    
    /* Example questions */
    .example-question {
        background: rgba(33, 150, 243, 0.08);
        border: 2px solid rgba(33, 150, 243, 0.3);
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: left;
        font-size: 0.95rem;
    }
    
    .example-question:hover {
        background: rgba(33, 150, 243, 0.15);
        border-color: rgba(33, 150, 243, 0.6);
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(33, 150, 243, 0.05) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(33, 150, 243, 0.1);
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Stats card */
    .stats-card {
        background: linear-gradient(135deg, rgba(33, 150, 243, 0.1) 0%, rgba(76, 175, 80, 0.1) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 800;
        color: #2196F3;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.7;
        text-transform: uppercase;
        letter-spacing: 1px;
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
    
    return True, f"✅ Account created successfully! Welcome, {username}!"

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
        
    except Exception as e:
        st.error(f"❌ **Error:** {str(e)}\n\nPlease check your API key and try again.")

# Main app
def main():
    
    # Authentication Page
    if st.session_state.page == 'auth':
        
        # Hero Section
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">🌍 GeoAdvisor</h1>
            <p class="hero-subtitle">Your Intelligent AI Assistant for Geographic Information Systems</p>
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
                    success, message = login_user(login_username, login_password)
                    if success:
                        st.success(message)
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
                    success, message = signup_user(signup_username, signup_password, signup_confirm, signup_email)
                    if success:
                        st.success(message)
                        st.info("👈 Please switch to the Login tab to sign in.")
                    else:
                        st.error(message)
        
        # Features section
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("### ✨ What Can GeoAdvisor Help You With?")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="stats-card">
                <div style="font-size: 2.5rem;">🗺️</div>
                <div class="stats-label">Spatial Analysis</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stats-card">
                <div style="font-size: 2.5rem;">🛰️</div>
                <div class="stats-label">Remote Sensing</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stats-card">
                <div style="font-size: 2.5rem;">🐍</div>
                <div class="stats-label">Python GIS</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="stats-card">
                <div style="font-size: 2.5rem;">📊</div>
                <div class="stats-label">Geostatistics</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Chat Page
    elif st.session_state.page == 'chat':
        
        # Sidebar
        with st.sidebar:
            st.markdown("### 👤 Account")
            st.markdown(f"""
            <div class="info-box">
                <strong>Logged in as:</strong><br>
                <span style="font-size: 1.2rem; color: #2196F3;">@{st.session_state.current_user}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
            
            st.markdown("---")
            
            # Chat stats
            st.markdown("### 📊 Session Stats")
            st.markdown(f"""
            <div class="stats-card">
                <div class="stats-number">{len(st.session_state.chat_history)}</div>
                <div class="stats-label">Messages</div>
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
            
            temperature = st.slider("🌡️ Temperature", 0.0, 2.0, 0.7, 0.1)
            max_tokens = st.slider("📏 Max Tokens", 256, 8192, 2048, 256)
            
            st.markdown("---")
            st.markdown("### 📚 GIS Topics")
            st.markdown("""
            - 🗺️ Spatial Analysis
            - 🛰️ Remote Sensing
            - 🎨 Cartography
            - 💾 Geodatabases
            - 🐍 Python GIS
            - 🌐 Coordinate Systems
            - 📍 GPS Services
            - 📐 Projections
            - 📊 Statistics
            """)
            
            st.markdown("---")
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        # Main chat area
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="margin: 0;">🌍 GeoAdvisor Chat</h1>
            <p style="opacity: 0.7; margin-top: 0.5rem;">Ask anything about GIS, spatial analysis, or geospatial programming</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat container
        chat_container = st.container()
        with chat_container:
            if len(st.session_state.chat_history) == 0:
                st.info("👋 Welcome! Start by asking a question or click an example below.")
            else:
                for chat in st.session_state.chat_history:
                    st.markdown(f"""
                    <div class="chat-message user-message">
                        <div class="message-role">👤 You</div>
                        <div class="message-content">{chat["user"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <div class="message-role">🤖 GeoAdvisor</div>
                        <div class="message-content">{chat["assistant"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Example questions
        st.markdown("---")
        st.markdown("### 💡 Example Questions")
        
        examples = [
            "What is the difference between raster and vector data in GIS?",
            "How do I calculate the area of polygons using GeoPandas?",
            "Explain coordinate reference systems (CRS) in simple terms",
            "What are the best practices for creating effective maps?",
            "How can I perform spatial joins in Python?",
            "What is the Haversine formula and when should I use it?"
        ]
        
        col1, col2 = st.columns(2)
        
        for idx, example in enumerate(examples):
            with col1 if idx % 2 == 0 else col2:
                if st.button(f"💬 {example}", key=f"ex_{idx}", use_container_width=True):
                    st.session_state.example_question = example
                    st.rerun()
        
        st.markdown("---")
        
        # Chat input
        user_input = st.text_area(
            "✍️ Your Question",
            placeholder="Type your question here... (e.g., How do I perform a buffer analysis in QGIS?)",
            key="user_input",
            value=st.session_state.get('example_question', ''),
            height=100
        )
        
        if 'example_question' in st.session_state:
            del st.session_state.example_question
        
        if st.button("🚀 Send Message", type="primary", use_container_width=True):
            if user_input:
                with st.spinner("🤔 GeoAdvisor is thinking..."):
                    chat_with_geoadvisor(user_input, model_name, temperature, max_tokens)
                st.rerun()
            else:
                st.warning("⚠️ Please enter a question first!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.6; padding: 1rem;">
        <p>Powered by <strong>Groq AI</strong> | Built with <strong>Streamlit</strong> | Specialized in <strong>GIS</strong></p>
        <p style="font-size: 0.85rem;">© 2024 GeoAdvisor - Your Intelligent Geospatial Assistant</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
