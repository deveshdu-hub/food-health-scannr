import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import datetime
import random
import pandas as pd
import requests

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
        url("https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80");
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
    
    .profile-box {
        background-color: rgba(224, 242, 241, 0.95);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #004d40;
        margin-bottom: 25px;
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
st.title("🥗 NutriScan India")
st.markdown("<p class='tagline'>Your Trusted Desi Health Companion 🇮🇳</p>", unsafe_allow_html=True)

# --- USER LOGIN / ACCOUNT INTERFACE ---
if not st.session_state["logged_in"]:
    st.markdown("### 🔐 Save Your Progress (Create Profile / Login)")
    login_tab, signup_tab = st.tabs(["🔑 Log In", "📝 Register New Account"])
    
    user_db = load_user_db()
    
    with login_tab:
        lin_user = st.text_input("Username / Mobile", key="login_username")
        lin_pass = st.text_input("Password", type="password", key="login_password")
        if st.button("Access Account"):
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
        
        if st.button("Create My Health Passport"):
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
else:
    prof = st.session_state["user_profile"]
    st.markdown(f"""
    <div class='profile-box'>
        👤 <b>Health Passport Linked:</b> {prof['username']} | 
        <b>Age:</b> {prof['age']} yrs | 
        <b>Weight:</b> {prof['weight']} kg | 
        🎯 <b>Target:</b> {prof['goals']}
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout / Switch Account"):
        st.session_state["logged_in"] = False
        st.session_state["user_profile"] = None
        st.session_state["messages"] = []
        st.session_state["scan_history"] = ""
        st.rerun()

st.write("---")

# 3. Motivation System
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
        "good": "💚 आपके शरीर के लिए क्या अच्छा है (फायदे)",
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

    source = st.radio("Scan Options", (ln["cam"], ln["gal"]), label_visibility="collapsed")
    uploaded_file = st.camera_input(ln["label"]) if source == ln["cam"] else st.file_uploader(ln["label"], type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Scanned Food Pack', use_container_width=True)
            
            st.write("---")
            st.markdown(f"<h3>{ln['analyzing']}</h3>", unsafe_allow_html=True)
            
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
            
            if st.button("🔥 Analyze Food Health Level"):
                with st.spinner('Checking ingredients...'):
                    response = model.generate_content([prompt, image])
                    raw_result = response.text
                    
                    if "|||DATA_SPLIT|||" in raw_result:
                        parts = raw_result.split("|||DATA_SPLIT|||")
                        json_str = parts[0].strip()
                        markdown_text = parts[1].strip()
                        
                        try:
                            nutrition_data = json.loads(json_str)
                            st.markdown("<h3>📊 Nutritional Traffic Meter (Per 100g)</h3>", unsafe_allow_html=True)
                            
                            c_val = int(nutrition_data.get("calories_percentage", 0)) / 100.0
                            su_val = int(nutrition_data.get("sugar_percentage", 0)) / 100.0
                            so_val = int(nutrition_data.get("sodium_percentage", 0)) / 100.0
                            f_val = int(nutrition_data.get("fat_percentage", 0)) / 100.0
                            
                            st.write("🔥 **Calories Density**")
                            st.progress(max(0.0, min(c_val, 1.0)))
                            st.write("🍬 **Refined Sugars / Carbs**")
                            st.progress(max(0.0, min(su_val, 1.0)))
                            st.write("🧂 **Salt Content (Sodium)**")
                            st.progress(max(0.0, min(so_val, 1.0)))
                            st.write("🛢️ **Palm Oil & Heavy Fats**")
                            st.progress(max(0.0, min(f_val, 1.0)))
                            st.write("---")
                        except Exception:
                            pass
                        
                        st.markdown(markdown_text)
                        st.session_state["scan_history"] = markdown_text
                    else:
                        st.markdown(raw_result)
                        st.session_state["scan_history"] = raw_result
                    
        except Exception as e:
            st.error(f"Something glitched out while scanning. Details: {e}")

    # ================= 🤖 TUNED CHATBOT WITH USER PASSPORT DATA =================
    if st.session_state["scan_history"]:
        st.write("---")
        st.markdown("<h3>💬 Ask Me for Your Weekly/Monthly Plan!</h3>", unsafe_allow_html=True)
        
        # Pull profile metadata into the AI's instruction context
        if st.session_state["logged_in"] and st.session_state["user_profile"]:
            u = st.session_state["user_profile"]
            user_context_string = f"The user is {u['age']} years old, weighs {u['weight']}kg, and their core fitness goal is {u['goals']}."
            st.info(f"💡 *The AI Chatbot is actively keeping your target goal (**{u['goals']}**) in mind!*")
        else:
            user_context_string = "The user has not logged in or set a physical profile yet."
            st.warning("💡 *Tip: Create an account or log in above so the AI can customize your routine using your exact weight and fitness goals!*")

        st.write("Tell me more about your routine or ask: 'Give me a weekly diet chart incorporating these healthy swaps' or 'Suggest an Indian exercise routine for me!'")

        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if chat_input := st.chat_input("Ask me for a personalized diet or exercise strategy..."):
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
                with st.spinner("Writing your fitness advice card..."):
                    chat_response = model.generate_content(chat_context_prompt)
                    bot_reply = chat_response.text
                    st.markdown(bot_reply)
            
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

st.markdown("---")
st.caption(ln["disclaimer"])
