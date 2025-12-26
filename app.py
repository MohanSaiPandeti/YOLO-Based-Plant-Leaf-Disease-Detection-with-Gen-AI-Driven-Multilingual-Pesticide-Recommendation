import streamlit as st
from ultralytics import YOLO
from PIL import Image
import tempfile
import os
import google.generativeai as genai

# ======================================================
# GEMINI API CONFIGURATION (2025 STABLE)
# ======================================================

API_KEY = "AIzaSyBq_LWbN2EqPYjhLoWZuuA-nPZibnPWD8A"
genai.configure(api_key=API_KEY)

MODEL_NAME = "gemini-2.5-flash"

try:
    gemini_model = genai.GenerativeModel(model_name=MODEL_NAME)
except Exception as e:
    st.error(f"Error initializing Gemini: {e}")
    st.stop()

# ======================================================
# LANGUAGE CONFIGURATION (UI = Native | Backend = Core)
# ======================================================

LANGUAGE_MAP = {
    "English": "English",
    "తెలుగు": "Telugu",
    "हिन्दी": "Hindi",
    "தமிழ்": "Tamil",
    "ಕನ್ನಡ": "Kannada",
    "മലയാളം": "Malayalam"
}

# ======================================================
# GEMINI PESTICIDE RECOMMENDATION FUNCTION
# ======================================================

def get_pesticide_recommendation(disease_name, language):
    prompt = f"""
You are an agricultural expert.

The detected plant disease is: {disease_name}

IMPORTANT INSTRUCTIONS:
- Respond ONLY in {language}
- Use simple, farmer-friendly language
- Do NOT mix languages

Provide:
1. Recommended pesticide(s)
2. Typical dosage
3. Safety precautions
4. Preventive measures

End with a short disclaimer.
"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating recommendation: {str(e)}"

# ======================================================
# STREAMLIT UI
# ======================================================

st.set_page_config(page_title="Leaf Doctor", layout="centered")

st.title("🌿 Leaf Doctor")
st.write("Upload a plant leaf image to detect disease and receive pesticide recommendations.")

# ---------- Language Selection ----------
st.subheader("🌐 Select Language")


st.markdown(
    """
    <div style="
        font-size:16px;
        font-weight:600;
        line-height:1.9;
        margin-top:10px;
        margin-bottom:14px;
        color: #ffffff;
    ">
        <div>భాషను ఎంచుకోండి</div>
        <div>भाषा चुनें</div>
        <div>மொழியைத் தேர்ந்தெடுக்கவும்</div>
        <div>ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ</div>
        <div>ഭാഷ തിരഞ്ഞെടുക്കുക</div>
    </div>
    """,
    unsafe_allow_html=True
)


selected_language = st.selectbox(
    "Choose your preferred language",
    list(LANGUAGE_MAP.keys())
)

language_for_gemini = LANGUAGE_MAP[selected_language]

# ---------- Load YOLO Model ----------
try:
    model = YOLO("best.pt")
except Exception:
    st.error("Could not load 'best.pt'. Make sure the file is in the same folder.")
    st.stop()

# ---------- Image Upload ----------
uploaded_file = st.file_uploader(
    "Upload a plant leaf image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Save image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name

    # YOLO Prediction
    results = model.predict(source=temp_path, conf=0.25)
    result_img = results[0].plot()
    st.image(result_img, caption="Detection Result", use_column_width=True)

    if len(results[0].boxes) > 0:
        cls_id = int(results[0].boxes.cls[0])
        confidence = float(results[0].boxes.conf[0])
        disease_label = model.names[cls_id]

        st.success(
            f"Detected Disease: **{disease_label}** "
            f"(Confidence: {confidence:.2f})"
        )

        with st.spinner("Generating pesticide recommendation..."):
            recommendation = get_pesticide_recommendation(
                disease_label,
                language_for_gemini
            )

        st.subheader("🌾 Pesticide Recommendation")
        st.write(recommendation)

    else:
        st.warning("No disease detected in the image.")

    os.remove(temp_path)

# ---------- Disclaimer ----------
st.warning("⚠️ Disclaimer: AI-generated recommendations should be verified with an agricultural expert before use.")
