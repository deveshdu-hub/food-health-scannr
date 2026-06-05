import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# 1. Page Configuration (Indian/Mobile First Layout)
st.set_page_config(
    page_title="NutriScan India AI", 
    page_icon="🇮🇳", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Desi Styling
st.markdown("""
    <style>
    .main .block-container { padding-top: 1.5rem; }
    h1 { color: #138808; font-family: 'Source Sans Pro', sans-serif; text-align: center; margin-bottom: 0px; }
    h5 { text-align: center; color: #FF9933; margin-top: 0px; margin-bottom: 2rem; }
    div.stButton > button:first-child {
        background-color: #138808;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥗 NutriScan India AI")
st.markdown("<h5>🇮🇳 Swasth Raho, Mast Raho! Scan snacks instantly.</h5>", unsafe_allow_html=True)

# 2. Setup Multi-language Dictionary
LANGUAGES = {
    "English": {
        "source": "Select scan method:",
        "cam": "📸 Take Live Photo (Camera)",
        "gal": "📁 Upload from Gallery",
        "label": "Point at the front pack or the nutritional table at the back",
        "analyzing": "🇮🇳 Checking with Desi Nutrition AI Guide...",
        "score": "📊 Health Score",
        "good": "✅ The Good (Faayde)",
        "bad": "⚠️ The Bad (Nuksan / Red Flags)",
        "verdict": "💡 Swasthya Verdict & Desi Alternatives",
        "alt": "Better Alternatives:",
        "disclaimer": "Note: This is an AI guide for general awareness. Check FSSAI labels for medical conditions."
    },
    "हिन्दी (Hindi)": {
        "source": "स्कैन करने का तरीका चुनें:",
        "cam": "📸 लाइव फोटो लें (कैमरा)",
        "gal": "📁 गैलरी से अपलोड करें",
        "label": "पैकेट के सामने का हिस्सा या पीछे की न्यूट्रिशन टेबल दिखाएं",
        "analyzing": "🇮🇳 देसी न्यूट्रिशन एআই गाइड जांच कर रहा है...",
        "score": "📊 हेल्प स्कोर",
        "good": "✅ फायदे (The Good)",
        "bad": "⚠️ नुकसान / रेड फ्लैग्स (The Bad)",
        "verdict": "💡 स्वास्थ्य वर्डिक्ट और विकल्प",
        "alt": "बेहतर और स्वस्थ विकल्प:",
        "disclaimer": "नोट: यह सामान्य जागरूकता के लिए एक एआई गाइड है। चिकित्सीय स्थितियों के लिए FSSAI लेबल की जांच करें।"
    },
    "தமிழ் (Tamil)": {
        "source": "ஸ்கேன் முறையைத் தேர்ந்தெடுக்கவும்:",
        "cam": "📸 லைவ் போட்டோ எடுக்கவும் (கேமரா)",
        "gal": "📁 கேலரியில் இருந்து பதிவேற்றவும்",
        "label": "பாக்கெட்டின் முன்பக்கம் அல்லது பின்புற ஊட்டச்சத்து அட்டவணையைக் காட்டவும்",
        "analyzing": "🇮🇳 தேசி நியூட்ரிஷன் AI ஆய்வு செய்கிறது...",
        "score": "📊 ஆரோக்கிய மதிப்பெண்",
        "good": "✅ நன்மைகள் (The Good)",
        "bad": "⚠️ தீமைகள் / எச்சரிக்கைகள் (The Bad)",
        "verdict": "💡 ஆரோக்கிய தீர்ப்பு & மாற்று வழிகள்",
        "alt": "சிறந்த ஆரோக்கியமான தேசி மாற்று உணவுகள்:",
        "disclaimer": "குறிப்பு: இது பொதுவான விдвижи உணவுக்கான AI வழிகாட்டி மட்டுமே."
    },
    "বাংলা (Bengali)": {
        "source": "স্ক্যান করার পদ্ধতি বেছে নিন:",
        "cam": "📸 লাইভ ছবি তুলুন (কলোরা)",
        "gal": "📁 গ্যালারি থেকে আপলোড করুন",
        "label": "প্যাকেটের সামনের অংশ বা পেছনের পুষ্টির টেবিলটি দেখান",
        "analyzing": "🇮🇳 পুষ্টি এআই গাইড পরীক্ষা করছে...",
        "score": "📊 হেলথ স্কোর",
        "good": "✅ ভালো দিক (The Good)",
        "bad": "⚠️ ক্ষতিকর দিক / রেড ফ্ল্যাগ (The Bad)",
        "verdict": "💡 স্বাস্থ্য রায় এবং দেশি বিকল্প",
        "alt": "সেরা স্বাস্থ্যকর বিকল্প খাবার:",
        "disclaimer": "দ্রষ্টব্য: এটি সাধারণ সচেতনতার জন্য একটি এআই গাইড।"
    }
}

# Language Select Box
selected_lang = st.selectbox("", list(LANGUAGES.keys()), index=0)
ln = LANGUAGES[selected_lang]

# Fetch Hidden API Key
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Developer Configuration Error: 'GEMINI_API_KEY' is missing.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    source = st.radio(ln["source"], (ln["cam"], ln["gal"]))
    uploaded_file = st.camera_input(ln["label"]) if source == ln["cam"] else st.file_uploader(ln["label"], type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Scanned Item', use_container_width=True)
            
            st.write("---")
            st.subheader(ln["analyzing"])
            
            prompt = f"""
            You are an expert clinical nutritionist specialized in Indian packaged snacks. 
            Analyze this product image. Your response MUST be provided in two parts, split exactly by "|||DATA_SPLIT|||".
            
            PART 1: Output a raw JSON object containing estimated nutrition values per 100g:
            {{
              "calories_percentage": (integer 0-100),
              "sugar_percentage": (integer 0-100),
              "sodium_percentage": (integer 0-100),
              "fat_percentage": (integer 0-100)
            }}

            |||DATA_SPLIT|||

            PART 2: Provide a consumer-friendly health assessment written completely in {selected_lang}.
            
            Format using these exact headers:
            ### {ln['score']}
            Give a score out of 10.
            
            ### {ln['good']}
            List points.
            
            ### {ln['bad']}
            List points.
            
            ### {ln['verdict']}
            * **Verdict:** 2 sentence advice.
            * **{ln['alt']}** Recommend 2 healthy Indian snack alternatives.
            """
            
            with st.spinner('Processing...'):
                response = model.generate_content([prompt, image])
                raw_result = response.text
                
                if "|||DATA_SPLIT|||" in raw_result:
                    parts = raw_result.split("|||DATA_SPLIT|||")
                    json_str = parts[0].strip()
                    markdown_text = parts[1].strip()
                    
                    # Clean up markdown code wrapper lines using a safe string approach
                    if json_str.startswith("```"):
                        lines = json_str.split("\n")
                        # Remove the first line (```json) and last line (```)
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines[-1].startswith("```"):
                            lines = lines[:-1]
                        json_str = "\n".join(lines).strip()
                    
                    try:
                        nutrition_data = json.loads(json_str)
                        
                        st.success("Analysis Complete!")
                        st.subheader("📊 Estimated Nutrients Level (Per 100g)")
                        
                        st.write("🔥 **Calories / Energy Density**")
                        st.progress(min(max(int(nutrition_data.get("calories_percentage", 0)) / 100.0, 0.0), 1.0))
                        
                        st.write("🍬 **Added Sugar / Refined Carbs**")
                        st.progress(min(max(int(nutrition_data.get("sugar_percentage", 0)) / 100.0, 0.0), 1.0))
                        
                        st.write("🧂 **Sodium (Salt Content)**")
                        st.progress(min(max(int(nutrition_data.get("sodium_percentage", 0)) / 100.0, 0.0), 1.0))
                        
                        st.write("🛢️ **Total Fat (Palm Oil / Saturated Fats)**")
                        st.progress(min(max(int(nutrition_data.get("fat_percentage", 0)) / 100.0, 0.0), 1.0))
                        st.write("---")
                    except Exception as json_err:
                        pass
                    
                    st.markdown(markdown_text)
                else:
                    st.markdown(raw_result)
                
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("---")
st.caption(ln["disclaimer"])
