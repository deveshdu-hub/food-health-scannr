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

# 2. Premium Desi Layout Styling with Custom Background Asset
# Note: Using an abstract unspalsh layout optimized for text legibility over dark/light modes.
st.markdown("""
    <style>
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)), 
        url("https://images.unsplash.com/photo-1498837167922-ddd27525d352?auto=format&fit=crop&w=1200&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main .block-container { padding-top: 1.5rem; }
    h1 { color: #138808; font-family: 'Georgia', serif; text-align: center; margin-bottom: 0px; text-shadow: 1px 1px 2px #fff; }
    .tagline { text-align: center; color: #FF9933; font-weight: bold; margin-top: 0px; margin-bottom: 1rem; font-size: 1.1rem; }
    
    .motivation-banner {
        background: linear-gradient(135deg, #FF9933 0%, #138808 100%);
        color: white;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 1.05rem;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    
    .human-greeting {
        background-color: rgba(255, 243, 224, 0.95);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #E65100;
        margin-bottom: 20px;
        font-style: italic;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    
    div.stButton > button:first-child {
        background-color: #138808;
        color: white;
        border-radius: 8px;
        width: 100%;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Dynamic Motivation System (Indian Health Wisdom)
MOTIVATION_QUOTES = [
    "✨ *'Pehla Sukh Nirogi Kaya'* — The ultimate wealth is a healthy body. Eat mindful, live vibrant!",
    "💪 Small healthy choices everyday lead to big transformations. Let's make today count!",
    "🧘 Wellness is not a restriction; it's a celebration of respect towards your body.",
    "🌾 Fresh, local, and mindful. Return to our roots for real health and inner strength.",
    "🌟 Your body is your only permanent home. Treat it with nourishing food, not commercial chemicals!"
]

st.title("🥗 NutriScan India")
st.markdown("<p class='tagline'>Your Trusted Desi Health Companion 🇮🇳</p>", unsafe_allow_html=True)

# Render Motivation Line
st.markdown(f"<div class='motivation-banner'>{random.choice(MOTIVATION_QUOTES)}</div>", unsafe_allow_html=True)

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
        "score": "📊 My Expert Health Score",
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
        "score": "📊 मेरा न्यूट्रिशन स्कोर",
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

    source = st.radio(ln["source"], (ln["cam"], ln["gal"]))
    uploaded_file = st.camera_input(ln["label"]) if source == ln["cam"] else st.file_uploader(ln["label"], type=["jpg", "jpeg", "png"])

    # Maintain running context in Session Memory for the persistent chatbot feature
    if "scan_history" not in st.session_state:
        st.session_state["scan_history"] = ""
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Scanned Food Pack', use_container_width=True)
            
            st.write("---")
            st.subheader(ln["analyzing"])
            
            prompt = f"""
            You are a warm, traditional yet medically smart Indian clinical nutritionist.
            Analyze the provided image of a packaged food item. 
            Your response MUST be divided into two blocks separated exactly by "|||DATA_SPLIT|||".
            
            PART 1: Output a raw JSON object containing estimated nutrition ratings per 100g (0 to 100):
            {{
              "calories_percentage": (integer),
              "sugar_percentage": (integer),
              "sodium_percentage": (integer),
              "fat_percentage": (integer)
            }}

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
                        
                        if json_str.startswith("```"):
                            lines = json_str.split("\n")
                            if lines[0].startswith("```"): lines = lines[1:]
                            if lines[-1].startswith("```"): lines = lines[:-1]
                            json_str = "\n".join(lines).strip()
                        
                        try:
                            nutrition_data = json.loads(json_str)
                            st.subheader("📊 Nutritional Traffic Meter (Per 100g)")
                            st.write("🔥 **Calories Density**")
                            st.progress(int(nutrition_data.get("calories_percentage", 0)) / 100.0)
                            st.write("🍬 **Refined Sugars / Carbs**")
                            st.progress(int(nutrition_data.get("sugar_percentage", 0)) / 100.0)
                            st.write("🧂 **Salt Content (Sodium)**")
                            st.progress(int(nutrition_data.get("sodium_percentage", 0)) / 100.0)
                            st.write("🛢️ **Palm Oil & Heavy Fats**")
                            st.progress(int(nutrition_data.get("fat_percentage", 0)) / 100.0)
                            st.write("---")
                        except Exception:
                            pass
                        
                        st.markdown(markdown_text)
                        # Save result context to let chat feature read details later
                        st.session_state["scan_history"] = markdown_text
                    else:
                        st.markdown(raw_result)
                        st.session_state["scan_history"] = raw_result
                    
        except Exception as e:
            st.error(f"Something glitched out. Please check image framing. Code detail: {e}")

    # ================= 🤖 UPGRADE: PERSISTENT EXPERT HEALTH CHATBOT =================
    if st.session_state["scan_history"]:
        st.write("---")
        st.subheader("💬 Ask Me for Your Weekly/Monthly Plan!")
        st.info("Tell me your Age, Weight, Goals (Weight Loss/Gain, Muscle), or ask: 'Give me a weekly diet chart incorporating these healthy swaps' or 'Suggest an Indian exercise routine for me!'")

        # Display conversational logs
        for msg in st.session_state["messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Chat interface field input
        if chat_input := st.chat_input("Ask me for a personalized diet or exercise strategy..."):
            with st.chat_message("user"):
                st.markdown(chat_input)
            st.session_state["messages"].append({"role": "user", "content": chat_input})

            # Formulate chat context containing previous item analytics
            chat_context_prompt = f"""
            You are the same empathetic Indian clinical nutritionist and physical training coach. 
            The user previously scanned a food product that had this health breakdown evaluation: 
            "{st.session_state["scan_history"]}"
            
            The user is now following up with this request or profile information: "{chat_input}"
            
            Provide a beautifully detailed, personalized reply in {selected_lang}. If they ask for a weekly/monthly diet plan, layout structural meal rows (Breakfast, Mid-day snack, Lunch, Evening Chai alternative, Dinner) using affordable Indian household choices (like Roti, Sabzi, Dal, Khichdi, Paneer, Curd, Poha). If they ask for exercise, outline simple home/gym schedules (like walking target steps, Yoga, bodyweight squats, Ghar ki koshish workouts). Keep your warm, motivational, human elder-coach tone.
            """

            with st.chat_message("assistant"):
                with st.spinner("Writing your fitness advice card..."):
                    chat_response = model.generate_content(chat_context_prompt)
                    bot_reply = chat_response.text
                    st.markdown(bot_reply)
            
            st.session_state["messages"].append({"role": "assistant", "content": bot_reply})

st.markdown("---")
st.caption(ln["disclaimer"])
