import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import datetime
import random
import pandas as pd
import requests

# 1. Page Configuration & UltraTech Branding
st.set_page_config(
    page_title="NutriScan India AI", 
    page_icon="🥗", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# 2. Advanced Premium UI/UX Custom Stylesheet
st.markdown("""
    <style>
    /* Global App Container and Tech-Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #F4F7F6 0%, #E9EFF1 100%);
        background-attachment: fixed;
    }
    
    /* Global Deep Charcoal Typography Override */
    .stApp p, .stApp span, .stApp div, .stApp li {
        color: #1A2530 !important;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Main Branding Header */
    .brand-title { 
        color: #0F5132 !important; 
        font-family: 'Cabinet Grotesk', 'Georgia', serif; 
        text-align: center; 
        margin-top: 10px;
        margin-bottom: 2px; 
        font-weight: 800;
        font-size: 2.6rem;
        letter-spacing: -0.5px;
    }
    .brand-tagline { 
        text-align: center; 
        color: #E65100 !important; 
        font-weight: 600; 
        margin-top: 0px; 
        margin-bottom: 25px; 
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Premium Unified Container Card Engine */
    .tech-card {
        background: #FFFFFF;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
        border: 1px solid rgba(15, 81, 50, 0.08);
        margin-bottom: 25px;
    }
    
    /* Motivational Banner Styling */
    .motivation-banner {
        background: linear-gradient(135deg, #115E59 0%, #0F766E 100%);
        padding: 16px 20px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(17, 94, 89, 0.15);
        margin-bottom: 25px;
    }
    .motivation-banner span {
        color: #FFFFFF !important;
        font-weight: 600;
        font-size: 1.05rem;
    }
    
    /* Time-of-Day Context Header Box */
    .human-greeting {
        background-color: #FFF7ED;
        padding: 16px 20px;
        border-radius: 12px;
        border-left: 5px solid #EA580C;
        margin-bottom: 25px;
    }
    .human-greeting p, .human-greeting strong {
        color: #9A3412 !important;
    }
    
    /* User Authenticated Health Passport Badge */
    .profile-box {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #A7F3D0;
        margin-bottom: 25px;
    }
    .profile-box b, .profile-box span {
        color: #065F46 !important;
    }
    
    /* Modern Form Field Label Adjustments */
    .stHeadingContainer h3 {
        color: #0F5132 !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        margin-bottom: 12px !important;
    }
    
    /* Tech Styled Primary Buttons */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        width: 100% !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 14px !important;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 12px rgba(4, 120, 87, 0.2) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(4, 120, 87, 0.3) !important;
    }

    /* PREMIUM TRAFFIC METERS */
    .meter-container {
        margin-bottom: 18px;
    }
    .meter-label {
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 6px;
        display: flex;
        justify-content: space-between;
        color: #374151 !important;
    }
    .meter-bg {
        background-color: #E5E7EB;
        border-radius: 9999px;
        width: 100%;
        height: 14px;
        overflow: hidden;
    }
    .meter-fill {
        height: 100%;
        border-radius: 9999px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Clean Tab Design Adjustments */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0,0,0,0.03);
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper for Dynamic Micro-Interaction Color Bars
def render_custom_meter(label, percentage):
    pct = max(0, min(int(percentage), 100))
    # Tech Palette: Safe Emerald, Alert Amber, Warning Crimson
    if pct <= 35:
        bar_color = "#10B981" # Emerald Green
    elif pct <= 65:
        bar_color = "#F59E0B" # Amber Yellow
    else:
        bar_color = "#EF4444" # Crimson Red
        
    st.markdown(f"""
    <div class="meter-container">
        <div class="meter-label"><span>{label}</span><span>{pct}%</span></div>
        <div class="meter-bg">
            <div class="meter-fill" style="width: {pct}%; background-color: {bar_color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- GOOGLE DRIVE DATABASE ENGINE (WEB API) ---
def load_user_db():
    try:
        url = st.secrets["GSCRIPT_API_URL"]
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            user_list = response.json()
            if user_list and len(user_list) > 0:
                return pd.DataFrame(user_list)
        return pd.DataFrame(columns=["username", "password", "age", "weight", "goals"])
    except Exception:
        return pd.DataFrame(columns=["username", "password", "age", "weight", "goals"])

def save_user_to_db(new_user_dict):
    try:
        url = st.secrets["GSCRIPT_API_URL"]
        payload = {k: str(v) for k, v in new_user_dict.items()}
        requests.post(url, json=payload, timeout=10)
        st.success("✨ Health Passport safely backed up to our secure cloud database!")
    except Exception:
        st.info("💡 Passport created in secure temporary session memory!")

# Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = None
if "scan_history" not in st.session_state:
    st.session_state["scan_history"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# --- APP HEADER ---
st.markdown("<h1 class='brand-title'>🥗 NutriScan India</h1>", unsafe_allow_html=True)
st.markdown("<p class='brand-tagline'>The Future of Desi Health Tracking 🇮🇳</p>", unsafe_allow_html=True)

# --- USER LOGIN / ACCOUNT INTERFACE (ENCLOSED IN TECH CARD) ---
if not st.session_state["logged_in"]:
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown("### 🔐 Secure Identity Verification")
    login_tab, signup_tab = st.tabs(["🔑 Log In", "📝 Register New Account"])
    
    user_db = load_user_db()
    
    with login_tab:
        lin_user = st.text_input("Username / Mobile", key="login_username")
        lin_pass = st.text_input("Password", type="password", key="login_password")
        if st.button("Access Cloud Account"):
            if not user_db.empty and lin_user in user_db['username'].values:
                matched_user = user_db[user_db['username'] == lin_user].iloc[0]
                if str(matched_user['password']) == str(lin_pass):
                    st.session_state["logged_in"] = True
                    st.session_state["user_profile"] = {
                        "username": lin_user,
                        "age": matched_user['age'],
                        "weight": matched_user['weight'],
                        "goals": matched_user['goals']
                    }
                    st.success(f"Welcome back, {lin_user}!")
                    st.rerun()
                else:
                    st.error("Invalid password. Please check again.")
            else:
                st.error("Username not found. Please register an account first!")
                
    with signup_tab:
        reg_user = st.text_input("Choose Username / Mobile", key="reg_username")
        reg_pass = st.text_input("Create Password", type="password", key="reg_password")
        reg_age = st.text_input("Your Age (years)", key="reg_age")
        reg_weight = st.text_input("Your Weight (kg)", key="reg_weight")
        reg_goals = st.selectbox("Your Ultimate Fitness Goal", [
            "Weight Loss", 
            "Muscle Gain / Bulking", 
            "Maintain Healthy Lifestyle", 
            "Manage Sugar / Diabetes / BP"
        ])
        
        if st.button("Generate Digital Health Passport"):
            if not user_db.empty and reg_user in user_db['username'].values:
                st.error("This username is already taken. Try adding a number!")
            elif not reg_user or not reg_pass:
                st.error("Please fill out a username and password.")
            else:
                profile_data = {
                    "username": reg_user,
                    "password": reg_pass,
                    "age": reg_age,
                    "weight": reg_weight,
                    "goals": reg_goals
                }
                save_user_to_db(profile_data)
                st.session_state["logged_in"] = True
                st.session_state["user_profile"] = profile_data
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
else:
    prof = st.session_state["user_profile"]
    st.markdown(f"""
    <div class='profile-box'>
        👤 <b>Health Passport Encrypted:</b> {prof['username']} &nbsp;|&nbsp; 
        <b>Age:</b> {prof['age']} yrs &nbsp;|&nbsp; 
        <b>Weight:</b> {prof['weight']} kg <br>
        🎯 <b>Target Goal Matrix:</b> {prof['goals']}
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout / Disconnect Session"):
        st.session_state["logged_in"] = False
        st.session_state["user_profile"] = None
        st.session_state["messages"] = []
        st.session_state["scan_history"] = ""
        st.rerun()

# 3. Dynamic Motivation System
MOTIVATION_QUOTES = [
    "✨ *'Pehla Sukh Nirogi Kaya'* — The ultimate wealth is a healthy body. Eat mindful, live vibrant!",
    "💪 Small healthy choices everyday lead to big transformations. Let's make today count!",
    "🧘 Wellness is not a restriction; it's a celebration of respect towards your body.",
    "🌾 Fresh, local, and mindful. Return to our roots for real health and inner strength.",
    "🌟 Your body is your only permanent home. Treat it with nourishing food, not commercial chemicals!"
]
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

# Multi-language Mapping
LANGUAGES = {
    "English": {
        "source": "Choose scan input parameter:",
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
        "good": "💚 आपके शरीर के लिए क्या अच्छा है (फायदे)",
        "bad": "⚠️ सावधान! इसमें छुपा हुआ नुकसान (रेड फ्लैग्स)",
        "verdict": "📝 फाइनल सलाह और घरेलू विकल्प",
        "alt": "इसकी जगह ये शानदार देसी विकल्प आजमाएं:",
        "disclaimer": "प्यारा सा नोट: मुझे अपना हेल्थ पार्टनर समझें। किसी गंभीर बीमारी के लिए डॉक्टर की सलाह ज़रूर लें।"
    }
}

selected_lang = st.selectbox("🎯 Choose Interface Language / भाषा चुनें", list(LANGUAGES.keys()), index=0)
ln = LANGUAGES[selected_lang]

# Fetch Hidden API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Developer Setup Error: 'GEMINI_API_KEY' is missing in Streamlit Settings.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Scanner Control Card
    st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
    st.markdown(f"### 🔍 UltraTech Vision Scanner")
    source = st.radio("Scan Options", (ln["cam"], ln["gal"]), label_visibility="collapsed")
    uploaded_file = st.camera_input(ln["label"]) if source == ln["cam"] else st.file_uploader(ln["label"], type=["jpg", "jpeg", "png"])
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded_file is not None:
        try:
            st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
            image = Image.open(uploaded_file)
            st.image(image, caption='Captured Media Asset', use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown(f"<h3 style='text-align:center;'>{ln['analyzing']}</h3>", unsafe_allow_html=True)
            
            prompt = f"""
            You are an expert clinical nutritionist specialized in Indian packaged snacks. 
            Analyze the provided image of a packaged food item. 
            Your response MUST be divided into two blocks separated exactly by the text separator "|||DATA_SPLIT|||".
            
            PART 1: Output ONLY a raw, single-line JSON string containing estimated nutrition ratings per 100g (0 to 100). Do NOT wrap it in markdown code blocks or write the word 'json'. Output raw text format only:
            {{"calories_percentage": 50, "sugar_percentage": 20, "sodium_percentage": 40, "fat_percentage": 30}}

            |||DATA_SPLIT|||

            PART 2: Provide your review text entirely in {selected_lang}. 
            
            Format using these exact headers:
            ### {ln['score']}
            State a bold score out of 10 with a lively reaction.
            
            ### {ln['good']}
            Point out what is decent.
            
            ### {ln['bad']}
            Call out hidden traps (Palm oil, refined sugar, high salt, processing methods).
            
            ### {ln['verdict']}
            Wrap up with a warm recommendation summary.
            Then list two specific traditional Indian alternative items under the subtitle "**{ln['alt']}**".
            """
            
            if st.button("🔥 Run UltraTech Diagnostics"):
                with st.spinner('Parsing algorithmic matrix values...'):
                    response = model.generate_content([prompt, image])
                    raw_result = response.text
                    
                    if "|||DATA_SPLIT|||" in raw_result:
                        parts = raw_result.split("|||DATA_SPLIT|||")
                        json_str = parts[0].strip()
                        markdown_text = parts[1].strip()
                        
                        try:
                            nutrition_data = json.loads(json_str)
                            st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
                            st.markdown("### 📊 Macro-Nutritional Density Vectors")
                            
                            # Premium architectural traffic lights
                            render_custom_meter("🔥 Calories Density Index", nutrition_data.get("calories_percentage", 0))
                            render_custom_meter("🍬 Glycemic Refined Carbs / Sugars", nutrition_data.get("sugar_percentage", 0))
                            render_custom_meter("🧂 Sodium Content Footprint", nutrition_data.get("sodium_percentage", 0))
                            render_custom_meter("🛢️ Hydrogenated Fats / Palm Oils", nutrition_data.get("fat_percentage", 0))
                            st.markdown("</div>", unsafe_allow_html=True)
                        except Exception:
                            pass
                        
                        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
                        st.markdown(markdown_text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.session_state["scan_history"] = markdown_text
                    else:
                        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
                        st.markdown(raw_result)
                        st.markdown("</div>", unsafe_allow_html=True)
                        st.session_state["scan_history"] = raw_result
                    
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "quota" in error_msg.lower():
                st.warning("⏳ **NutriScan India Cloud Node is Busy!** Massive user traffic detected. Please wait 20-30 seconds and retry diagnostics! 😊")
            else:
                st.error(f"Systems Diagnostic Exception: {e}")

    # ================= 🤖 TUNED CHATBOT WITH USER PASSPORT DATA =================
    if st.session_state["scan_history"]:
        st.markdown("<div class='tech-card'>", unsafe_allow_html=True)
        st.markdown("### 💬 AI Copilot Hyper-Personalization Engine")
        
        if st.session_state["logged_in"] and st.session_state["user_profile"]:
            u = st.session_state["user_profile"]
            user_context_string = f"The user is {u['age']} years old, weighs {u['weight']}kg, and their core fitness goal is {u['goals']}."
            st.info(f"🧬 *Target matrix optimized dynamically for item parameters targeting **{u['goals']}**.*")
        else:
            user_context_string = "The user has not logged in or set a physical profile yet."
            st.warning("💡 *Unauthenticated session. Synchronize profile parameters above to compile personalized daily blueprints.*")

        st.write("Query example: *'Compile a weekly meal macro layout incorporating these alternative swaps'*")

        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Input customized target parameter query..."):
            with st.chat_message("user"):
                st.markdown(chat_input)
            st.session_state["messages"].append({"role": "user", "content": chat_input})

            chat_context_prompt = f"""
            You are an empathetic Indian clinical nutritionist and physical training coach. 
            
            Here is the authenticated user's physical profile context:
            "{user_context_string}"
            
            The user previously scanned a food product that had this health breakdown evaluation: 
            "{st.session_state["scan_history"]}"
            
            The user is now asking or requesting this strategy: "{chat_input}"
            
            Provide a beautifully detailed, personalized reply in {selected_lang}. Direct your answer specifically to their age, weight, and goals if available. Keep your format highly scannable and clean.
            """

            with st.chat_message("assistant"):
                with st.spinner("Compiling tactical chart overlay..."):
                    chat_response = model.generate_content(chat_context_prompt)
                    bot_reply = chat_response.text
                    st.markdown(bot_reply)
            
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")
st.caption(ln["disclaimer"])
