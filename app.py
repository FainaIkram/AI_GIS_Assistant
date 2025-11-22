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

# Custom CSS for both light and dark themes
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
    }
    
    /* Chat message styling - works in both themes */
    .chat-message {
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        border-left: 4px solid;
    }
    
    /* Light theme colors */
    @media (prefers-color-scheme: light) {
        .user-message {
            background-color: #e3f2fd;
            border-left-color: #2196f3;
            color: #1565c0;
        }
        .assistant-message {
            background-color: #f1f8e9;
            border-left-color: #4caf50;
            color: #2e7d32;
        }
    }
    
    /* Dark theme colors */
    @media (prefers-color-scheme: dark) {
        .user-message {
            background-color: rgba(33, 150, 243, 0.15);
            border-left-color: #42a5f5;
            color: #90caf9;
        }
        .assistant-message {
            background-color: rgba(76, 175, 80, 0.15);
            border-left-color: #66bb6a;
            color: #a5d6a7;
        }
    }
    
    /* Example questions styling */
    .example-btn {
        background-color: transparent;
        border: 2px solid;
        border-radius: 8px;
        padding: 10px 16px;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        font-weight: 500;
    }
    
    /* Light theme example buttons */
    @media (prefers-color-scheme: light) {
        .example-btn {
            border-color: #2196f3;
            color: #1976d2;
        }
        .example-btn:hover {
            background-color: #e3f2fd;
            transform: translateY(-2px);
        }
    }
    
    /* Dark theme example buttons */
    @media (prefers-color-scheme: dark) {
        .example-btn {
            border-color: #42a5f5;
            color: #90caf9;
        }
        .example-btn:hover {
            background-color: rgba(33, 150, 243, 0.15);
            transform: translateY(-2px);
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
    
    # Store user (in production, hash the password!)
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
        
        # Build conversation history for Groq
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add previous conversation
        for chat_msg in st.session_state.chat_history:
            messages.append({"role": "user", "content": chat_msg["user"]})
            messages.append({"role": "assistant", "content": chat_msg["assistant"]})
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Get response from Groq
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        assistant_message = response.choices[0].message.content
        
        # Save to chat history
        st.session_state.chat_history.append({
            "user": message,
            "assistant": assistant_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save to user's database
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
    st.title("🌍 GeoAdvisor: AI GIS Text Assistant")
    st.markdown("### Your intelligent companion for Geographic Information Systems")
    
    # Authentication Page
    if st.session_state.page == 'auth':
        st.markdown("## 🔐 Welcome to GeoAdvisor")
        st.markdown("Please login or create an account to get started")
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Login to Your Account")
            login_username = st.text_input("Username", key="login_username")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login 🚀", key="login_btn"):
                success, message = login_user(login_username, login_password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        with tab2:
            st.subheader("Create New Account")
            signup_username = st.text_input("Username (min 3 characters)", key="signup_username")
            signup_email = st.text_input("Email", key="signup_email")
            signup_password = st.text_input("Password (min 6 characters)", type="password", key="signup_password")
            signup_confirm = st.text_input("Confirm Password", type="password", key="signup_confirm")
            
            if st.button("Create Account ✨", key="signup_btn"):
                success, message = signup_user(signup_username, signup_password, signup_confirm, signup_email)
                if success:
                    st.success(message)
                    st.info("Please switch to the Login tab to sign in.")
                else:
                    st.error(message)
    
    # Chat Page
    elif st.session_state.page == 'chat':
        # Sidebar
        with st.sidebar:
            st.markdown(f"### 👤 User: **{st.session_state.current_user}**")
            
            if st.button("Logout 🚪"):
                logout_user()
                st.rerun()
            
            st.markdown("---")
            st.markdown("### ⚙️ Model Settings")
            
            model_name = st.selectbox(
                "Model",
                [
                    "llama-3.3-70b-versatile",
                    "llama-3.1-70b-versatile",
                    "llama-3.1-8b-instant",
                    "mixtral-8x7b-32768",
                    "gemma2-9b-it"
                ],
                index=0
            )
            
            temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1)
            max_tokens = st.slider("Max Tokens", 256, 8192, 2048, 256)
            
            st.markdown("---")
            st.markdown("""
            ### 📚 GIS Topics
            - Spatial Analysis
            - Remote Sensing
            - Cartography
            - Geodatabases
            - Python GIS
            - Coordinate Systems
            - GPS Services
            - Projections
            - Statistics
            """)
            
            if st.button("Clear Chat 🗑️"):
                st.session_state.chat_history = []
                st.rerun()
        
        # Main chat area
        st.markdown("Ask questions about GIS concepts, spatial analysis, geospatial programming, cartography, and more!")
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history:
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {chat["user"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="chat-message assistant-message"><strong>GeoAdvisor:</strong> {chat["assistant"]}</div>', unsafe_allow_html=True)
        
        # Example questions
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
        
        with col1:
            for example in examples[::2]:  # Odd indexed examples
                if st.markdown(f'<div class="example-btn" onclick="navigator.clipboard.writeText(\'{example}\')">{example}</div>', unsafe_allow_html=True):
                    pass
                if st.button(example, key=f"ex_{examples.index(example)}", use_container_width=True):
                    st.session_state.example_question = example
                    st.rerun()
        
        with col2:
            for example in examples[1::2]:  # Even indexed examples
                if st.markdown(f'<div class="example-btn" onclick="navigator.clipboard.writeText(\'{example}\')">{example}</div>', unsafe_allow_html=True):
                    pass
                if st.button(example, key=f"ex_{examples.index(example)}", use_container_width=True):
                    st.session_state.example_question = example
                    st.rerun()
        
        # Chat input
        user_input = st.text_area(
            "Your Question",
            placeholder="Ask me anything about GIS, spatial analysis, or geospatial data...",
            key="user_input",
            value=st.session_state.get('example_question', ''),
            height=100
        )
        
        if 'example_question' in st.session_state:
            del st.session_state.example_question
        
        if st.button("Send 🚀", type="primary"):
            if user_input:
                chat_with_geoadvisor(user_input, model_name, temperature, max_tokens)
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <center>
    <small>Powered by Groq AI | Built with Streamlit | GIS Specialized</small>
    </center>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
