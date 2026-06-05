import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Page Configuration (Makes the app look like a native mobile app on phones)
st.set_page_config(
    page_title="NutriScan AI", 
    page_icon="🥗", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS to style the app clean and modern
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; }
    h1 { color: #2E7D32; font-family: 'Source Sans Pro', sans-serif; }
    div.stButton > button:first-child {
        background-color: #2E7D32;
        color: white;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥗 NutriScan AI")
st.subheader("Instantly scan packaged food or drinks to see how healthy they really are.")

# 2. Fetch the hidden API key securely from Streamlit Cloud Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 Developer Configuration Error: The 'GEMINI_API_KEY' is missing in your Streamlit Advanced Settings Secrets.")
else:
    # 3. Initialize the AI Model (Using gemini-2.5-flash for maximum speed on image tasks)
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # 4. User interface for choosing how to input the image
    source = st.radio("Select how to scan:", ("📸 Use Smartphone Camera", "📁 Upload Image from Gallery"))
    
    uploaded_file = None
    if source == "📸 Use Smartphone Camera":
        # Streamlit automatically handles camera permissions on iOS/Android browsers
        uploaded_file = st.camera_input("Position the food product or its nutrition facts label clearly")
    else:
        uploaded_file = st.file_uploader("Choose a photo...", type=["jpg", "jpeg", "png"])

    # 5. Process the image if it exists
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            
            # Preview the image to the user
            st.image(image, caption='Scanned Item', use_container_width=True)
            
            st.write("---")
            st.subheader("🔍 Running AI Nutritional Analysis...")
            
            # Robust, well-structured system prompt optimized for parsing nutrition labels
            prompt = """
            You are an expert clinical nutritionist and food safety expert. Analyze this image of a packaged food or beverage item. 
            Provide a clear, objective, and consumer-friendly health assessment based on the visible branding, ingredients, or nutrition facts.
            
            Format your final response cleanly with Markdown using the exact headers below:
            
            ### 📊 Health Score
            Provide a definitive score out of 10 (e.g., **6/10**). Briefly state the primary reason for this score in 1 sentence.
            
            ### ✅ The Good
            List 1 to 3 positive nutritional attributes (e.g., high dietary fiber, low glycemic ingredients, contains essential micronutrients, zero trans-fats).
            
            ### ⚠️ The Bad (Red Flags)
            List any concerning attributes or hidden traps (e.g., high hidden sugars, heavy presence of artificial emulsifiers, high sodium levels, ultra-processed nature, high saturated fat).
            
            ### 💡 Smart Verdict & Alternatives
            * **Verdict:** A 2-sentence summary telling the user if this is safe for daily consumption, occasional consumption, or if it should be avoided.
            * **Better Alternatives:** Give 2 specific, healthier alternative snack or beverage ideas that provide similar satisfaction but with a better health profile.
            """
            
            # Execute visual model inference
            with st.spinner('Reading label and evaluating processing levels...'):
                response = model.generate_content([prompt, image])
                
                # Render results using native markdown formatting
                st.success("Analysis Complete!")
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Something went wrong during analysis. Please try again with a clearer image. Error details: {e}")

st.markdown("---")
st.caption("Disclaimer: This app uses generative AI to analyze visual labels for general educational purposes. It does not replace professional medical or dietary advice.")
