import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import datetime
import random

# 1. Page Configuration
st.set_page_config(
    page_title="NutriScan India AI", 
    page_icon="🥗", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Dark Text Formatting CSS Overlay (Ensures text visibility on mobile)
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.90)), 
        url("[https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80](https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80)");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Force ALL standard text, subheaders, and markdown to deep charcoal dark text */
    .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp span, .stApp div, .stApp li {
        color: #111111 !important;
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    h1 { color: #138808 !important; font-family: 'Georgia', serif; text-align: center; margin-bottom: 0px; font-weight: bold; }
    .tagline { text-align: center; color: #E65100 !important; font-weight: bold; margin-top: 0px; margin-bottom: 1rem; font-size: 1.1rem; }
    
    .motivation-banner {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .motivation-banner * {
        color: #ffffff !important;
        font-weight: bold;
    }
    
    .human-greeting {
        background-color: rgba(255, 224, 178, 0.95);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #E65100;
        margin-bottom: 20px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    
    div.stButton > button:first-child {
        background-color: #138808 !important;
        color: white !important;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
        padding: 12px;
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Motivation System (Indian Health Wisdom)
MOTIVATION_QUOTES = [
    "✨ *'Pehla Sukh Nirogi Kaya'* — The ultimate wealth is a healthy body. Eat mindful, live vibrant!",
    "💪 Small healthy choices everyday lead to big transformations. Let's make today count!",
    "🧘 Wellness is not a restriction; it's a celebration of respect towards your body.",
    "🌾 Fresh, local, and mindful. Return to our roots for real health and inner strength.",
    "🌟 Your body is your only permanent home. Treat it with nourishing food, not commercial chemicals!"
]

st.title("🥗 NutriScan India")
st.markdown("<p class='tagline'>Your Trusted Desi Health Companion 🇮🇳</p>", unsafe_allow_html=True)

st.markdown(f"<div class='motivation-banner'><span>{random.choice(MOTIVATION_QUOTES)}</span></div>", unsafe_allow_html=True)

# Time-of-Day Indian Greeting
now = datetime.datetime.now()
current_hour = now.hour

if 5 <= current_hour < 12:
    greeting_text = "🌅 **Good Morning!** Shuruaat acchi toh din accha! What breakfast snack or drink are we reviewing today?"
elif 12 <= current_hour < 16:
    greeting_text = "☀️ **Good Afternoon!** Lunch time cravings kicking in? Let's check that food pack real quick!"
elif 16 <= current_hour < 20:
    greeting_text = "☕ **Good Evening!** Chai time companion choice? Let's scan your namkeen or biscuits right now."
else:
    greeting_text = "🌙 **Hey there!** Late-night hunger pangs? Let's check if this midnight munchie is safe for your health goals!"

st.markdown(f"<div class='human-greeting'>{greeting_text}</div>", unsafe_allow_html=True)

# 4. Multi-language Dictionary
LANGUAGES = {
    "English": {
        "source": "Choose how to show me the pack:",
        "cam": "📸 Take Live Photo (Camera)",
        "gal": "📁 Choose from Phone Gallery",
        "label": "Show me the front design or the nutrition table at the back",
        "analyzing": "🧐 Looking closely at this label... Ek minute haan...",
        "score": "My Expert Health Score",
        "good": "💚 Why Your Body Will Thank You (Faayde)",
        "bad": "⚠️ Quick Warning / Red Flags (Nuksan)",
        "verdict": "📝 Final Verdict & Healthy Swaps",
        "alt": "Try these comforting Indian alternatives instead:",
        "disclaimer": "Friendly Note: Think of me as your fitness buddy. For serious medical conditions, consult your doctor."
    },
    "हिन्दी (Hindi)": {
        "source": "फोटो कैसे लेना चाहेंगे:",
        "cam": "📸 कैमरे से लाइव फोटो खींचें",
        "gal": "📁 गैलरी से फोटो चुनें",
        "label": "पैकेट के सामने का हिस्सा या पीछे की सामग्री लिस्ट दिखाएं",
        "analyzing": "🧐 रुकिए, मैं ध्यान से पढ़ती हूँ... एक मिनट दीजिए...",
        "score": "मेरा न्यूट्रिशन स्कोर",
        "good": "💚 आपके शरीर के लिए क्या अच्छा है (فायदे)",
        "bad": "⚠️ सावधान! इसमें छुपा हुआ नुकसान (रेड फ्लैग्स)",
        "verdict": "📝 फाइनल सलाह और घरेलू विकल्प",
        "alt": "इसकी जगह ये शानदार देसी विकल्प आजमाएं:",
        "disclaimer": "प्यारा सा नोट: मुझे अपना हेल्थ पार्टनर समझें। किसी गंभीर बीमारी के लिए डॉक्टर की सलाह ज़रूर लें।"
    }
}

selected_lang = st.selectbox("🎯 Choose Language / भाषा चुनें", list(LANGUAGES.keys()), index=0)
ln = LANGUAGES[selected_lang]

# Fetch Hidden API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Developer Setup Error: 'GEMINI_API_KEY' is missing in Streamlit Settings.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    source = st.radio("Scan Options", (ln["cam"], ln
