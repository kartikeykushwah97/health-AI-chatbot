import streamlit as st
import google.generativeai as genai

# --- Configuration and Initialization ---

# Set the page configuration for a better layout
st.set_page_config(
    page_title="🩺 SPARK's — AI Health Chatbot",
    page_icon="🩺",
    layout="centered"
)

# Set up the main title and a separator
st.markdown("<h1 style='text-align:center;'>🩺 SPARK's — AI Health Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# --- Recommended API Key Configuration using Streamlit Secrets ---
# This is the most secure way to manage secrets in Streamlit.
# It reads the key from a file named `secrets.toml` in a `.streamlit` folder.
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    if not api_key:
        st.error("🚨 **Configuration Error:** The `GOOGLE_API_KEY` is empty. Please provide a valid API key in your Streamlit secrets.", icon="🚨")
        st.info("Add a `GOOGLE_API_KEY = 'YOUR_KEY_HERE'` to your `.streamlit/secrets.toml` file and refresh the page.")
        st.stop()
    genai.configure(api_key=api_key)
except KeyError:
    st.error("🚨 **Configuration Error:** Could not find the Google API key. Please make sure it's set up correctly in your Streamlit secrets.", icon="🚨")
    st.info("Add a `GOOGLE_API_KEY = 'YOUR_KEY_HERE'` to your `.streamlit/secrets.toml` file and refresh the page.")
    st.stop()
except Exception as e:
    st.error(f"🚨 **Configuration Error:** Failed to configure the Google API key. Error: {e}", icon="🚨")
    st.stop()


# Function to initialize the Gemini model and chat session
def initialize_chat():
    """Initializes the Gemini model and starts a chat session."""
    system_instruction = (
        "You are a helpful and friendly AI assistant focused on health and wellness. "
        "Your name is SPARK. Provide informative and safe answers to health-related questions. "
        "IMPORTANT: You are not a medical professional. Always end your responses by strongly "
        "advising the user to consult with a qualified doctor for any medical advice or concerns."
    )
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    return model.start_chat(history=[])

# Initialize session state variables if they don't exist
if "chat" not in st.session_state:
    st.session_state.chat = initialize_chat()
if "history" not in st.session_state:
    st.session_state.history = []
if "user_name" not in st.session_state:
    st.session_state.user_name = "Guest"

# --- Sidebar for Settings ---

with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state.user_name = st.text_input("Your Name", value=st.session_state.user_name)

    if st.button("🗑️ Clear Chat History"):
        # Reset the chat history and re-initialize the chat model
        st.session_state.history = []
        st.session_state.chat = initialize_chat()
        st.rerun()

# --- Chat Interface ---

# Display previous messages from history
for message in st.session_state.history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role, avatar="👤" if role == "user" else "🩺"):
        st.markdown(f"**{st.session_state.user_name if role == 'user' else 'SPARK'}:** {message['text']}")

# Get user input from the chat interface
user_query = st.chat_input("Ask about health, vaccination, or outbreaks...")

if user_query:
    # Add user's message to history and display it
    st.session_state.history.append({"role": "user", "text": user_query})
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"**{st.session_state.user_name}:** {user_query}")

    # Get AI response and display it
    with st.chat_message("assistant", avatar="🩺"):
        with st.spinner("SPARK is thinking..."):
            try:
                # Send the message to the Gemini model
                response = st.session_state.chat.send_message(user_query)
                bot_response = response.text.strip()
                st.session_state.history.append({"role": "assistant", "text": bot_response})
                st.markdown(f"**SPARK:** {bot_response}")
            except Exception as e:
                error_message = f"⚠️ **AI Error:** Could not get a response. Please check your API key, network connection, and library versions. \n\n**Error Details:** {e}"
                st.session_state.history.append({"role": "assistant", "text": error_message})
                st.error(error_message)

