import streamlit as st

api_key = st.secrets["GROQ_API_KEY"]

import gradio as gr
from groq import Groq
import os
from datetime import datetime

# Simple user database (in production, use a proper database)
USER_DATABASE = {}

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

def signup_user(username, password, confirm_password, email):
    """Handle user signup"""
    if not username or not password or not email:
        return "❌ All fields are required!", gr.update(visible=True), gr.update(visible=False)
    
    if len(username) < 3:
        return "❌ Username must be at least 3 characters long!", gr.update(visible=True), gr.update(visible=False)
    
    if len(password) < 6:
        return "❌ Password must be at least 6 characters long!", gr.update(visible=True), gr.update(visible=False)
    
    if password != confirm_password:
        return "❌ Passwords do not match!", gr.update(visible=True), gr.update(visible=False)
    
    if username in USER_DATABASE:
        return "❌ Username already exists! Please choose another one.", gr.update(visible=True), gr.update(visible=False)
    
    # Store user (in production, hash the password!)
    USER_DATABASE[username] = {
        "password": password,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "chat_history": []
    }
    
    return f"✅ Account created successfully! Welcome, {username}! Please login below.", gr.update(visible=True), gr.update(visible=False)

def login_user(username, password):
    """Handle user login"""
    if not username or not password:
        return "❌ Please enter both username and password!", gr.update(visible=True), gr.update(visible=False), None
    
    if username not in USER_DATABASE:
        return "❌ Username not found! Please sign up first.", gr.update(visible=True), gr.update(visible=False), None
    
    if USER_DATABASE[username]["password"] != password:
        return "❌ Incorrect password! Please try again.", gr.update(visible=True), gr.update(visible=False), None
    
    return f"✅ Welcome back, {username}!", gr.update(visible=False), gr.update(visible=True), username

def logout_user():
    """Handle user logout"""
    return gr.update(visible=True), gr.update(visible=False), None, []

def chat_with_geoadvisor(message, history, current_user, model_name, temperature, max_tokens):
    """Main chat function for GeoAdvisor"""
    
    # Initialize history if None
    if history is None:
        history = []
    
    if not message or message.strip() == "":
        return history
    
    if not current_user:
        # Return history with new error message in list format
        return history + [[message, "⚠️ Please login to use GeoAdvisor."]]
    
    # Check if API key is configured
    if not GROQ_API_KEY or GROQ_API_KEY == "":
        return history + [[message, "⚠️ **API Key Not Configured!**\n\nPlease add your Groq API key at the top of the code."]]
    
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Build conversation history for Groq
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add previous conversation - handle list format [user_msg, assistant_msg]
        for chat_pair in history:
            if isinstance(chat_pair, (list, tuple)) and len(chat_pair) >= 2:
                user_msg = chat_pair[0]
                assistant_msg = chat_pair[1]
                
                if user_msg and str(user_msg).strip():
                    messages.append({"role": "user", "content": str(user_msg)})
                if assistant_msg and str(assistant_msg).strip():
                    messages.append({"role": "assistant", "content": str(assistant_msg)})
        
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
        
        # Save to user's chat history
        if current_user in USER_DATABASE:
            USER_DATABASE[current_user]["chat_history"].append({
                "user": message,
                "assistant": assistant_message,
                "timestamp": datetime.now().isoformat()
            })
        
        # Return updated history with new messages as list
        return history + [[message, assistant_message]]
    
    except Exception as e:
        error_message = f"❌ **Error:** {str(e)}\n\nPlease check your API key and try again."
        return history + [[message, error_message]]

def clear_chat():
    """Clear the chat history"""
    return []

# Create Gradio interface
with gr.Blocks() as demo:
    
    current_user_state = gr.State(None)
    
    gr.Markdown("""
    # 🌍 GeoAdvisor: AI GIS Text Assistant
    ### Your intelligent companion for Geographic Information Systems
    """)
    
    # Login/Signup Section
    with gr.Column(visible=True) as auth_section:
        gr.Markdown("## 🔐 Welcome to GeoAdvisor")
        gr.Markdown("Please login or create an account to get started")
        
        with gr.Tab("Login"):
            with gr.Column():
                login_username = gr.Textbox(label="Username", placeholder="Enter your username")
                login_password = gr.Textbox(label="Password", placeholder="Enter your password", type="password")
                login_btn = gr.Button("Login 🚀")
                login_status = gr.Markdown("")
        
        with gr.Tab("Sign Up"):
            with gr.Column():
                signup_username = gr.Textbox(label="Username", placeholder="Choose a username (min 3 characters)")
                signup_email = gr.Textbox(label="Email", placeholder="Enter your email")
                signup_password = gr.Textbox(label="Password", placeholder="Choose a password (min 6 characters)", type="password")
                signup_confirm_password = gr.Textbox(label="Confirm Password", placeholder="Re-enter your password", type="password")
                signup_btn = gr.Button("Create Account ✨")
                signup_status = gr.Markdown("")
    
    # Main Application Section (hidden until login)
    with gr.Column(visible=False) as main_section:
        with gr.Row():
            gr.Markdown("## Chat with GeoAdvisor")
            with gr.Column(scale=1):
                user_display = gr.Markdown("")
                logout_btn = gr.Button("Logout 🚪")
        
        gr.Markdown("Ask questions about GIS concepts, spatial analysis, geospatial programming, cartography, and more!")
        
        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.Chatbot(
                    label="Chat with GeoAdvisor", 
                    height=500
                )
                
                msg = gr.Textbox(
                    placeholder="Ask me anything about GIS, spatial analysis, or geospatial data...",
                    label="Your Question",
                    lines=2
                )
                
                with gr.Row():
                    submit_btn = gr.Button("Send 🚀")
                    clear_btn = gr.Button("Clear Chat 🗑️")
                
                gr.Markdown("### 💡 Example Questions - Click to Use")
                with gr.Row():
                    example1 = gr.Button("Raster vs Vector", scale=1)
                    example2 = gr.Button("Polygon Area", scale=1)
                with gr.Row():
                    example3 = gr.Button("CRS Explained", scale=1)
                    example4 = gr.Button("Map Design", scale=1)
                with gr.Row():
                    example5 = gr.Button("Spatial Joins", scale=1)
                    example6 = gr.Button("Haversine", scale=1)
            
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Model Settings")
                
                model_dropdown = gr.Dropdown(
                    choices=[
                        "llama-3.3-70b-versatile",
                        "llama-3.1-70b-versatile",
                        "llama-3.1-8b-instant",
                        "mixtral-8x7b-32768",
                        "gemma2-9b-it"
                    ],
                    value="llama-3.3-70b-versatile",
                    label="Model"
                )
                
                temperature_slider = gr.Slider(
                    minimum=0,
                    maximum=2,
                    value=0.7,
                    step=0.1,
                    label="Temperature"
                )
                
                max_tokens_slider = gr.Slider(
                    minimum=256,
                    maximum=8192,
                    value=2048,
                    step=256,
                    label="Max Tokens"
                )
                
                gr.Markdown("""
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
    
    gr.Markdown("""
    ---
    <center>
    <small>Powered by Groq AI | Built with Gradio | GIS Specialized</small>
    </center>
    """)
    
    # Event handlers for authentication
    signup_btn.click(
        fn=signup_user,
        inputs=[signup_username, signup_password, signup_confirm_password, signup_email],
        outputs=[signup_status, auth_section, main_section]
    )
    
    login_btn.click(
        fn=login_user,
        inputs=[login_username, login_password],
        outputs=[login_status, auth_section, main_section, current_user_state]
    ).then(
        fn=lambda user: f"👤 Logged in as: **{user}**" if user else "",
        inputs=[current_user_state],
        outputs=[user_display]
    )
    
    logout_btn.click(
        fn=logout_user,
        outputs=[auth_section, main_section, current_user_state, chatbot]
    )
    
    # Event handlers for chat
    msg.submit(
        fn=chat_with_geoadvisor,
        inputs=[msg, chatbot, current_user_state, model_dropdown, temperature_slider, max_tokens_slider],
        outputs=chatbot
    ).then(
        lambda: "",
        None,
        msg
    )
    
    submit_btn.click(
        fn=chat_with_geoadvisor,
        inputs=[msg, chatbot, current_user_state, model_dropdown, temperature_slider, max_tokens_slider],
        outputs=chatbot
    ).then(
        lambda: "",
        None,
        msg
    )
    
    clear_btn.click(
        fn=clear_chat,
        outputs=chatbot
    )
    
    # Example button handlers
    example1.click(lambda: "What is the difference between raster and vector data in GIS?", None, msg)
    example2.click(lambda: "How do I calculate the area of polygons using GeoPandas?", None, msg)
    example3.click(lambda: "Explain coordinate reference systems (CRS) in simple terms", None, msg)
    example4.click(lambda: "What are the best practices for creating effective maps?", None, msg)
    example5.click(lambda: "How can I perform spatial joins in Python?", None, msg)
    example6.click(lambda: "What is the Haversine formula and when should I use it?", None, msg)

# Launch the app
if __name__ == "__main__":
    demo.launch()
