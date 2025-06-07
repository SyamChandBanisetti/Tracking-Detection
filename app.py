import streamlit as st
from pathlib import Path
import PIL.Image
import settings
import helper

# App Configuration
st.set_page_config(
    page_title="🧠 YOLOv8 Object Detection & Tracking",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🔍 Real-Time Object Detection & Tracking using YOLOv8")

# Sidebar – Model Selection
st.sidebar.header("⚙️ Model Settings")
task = st.sidebar.radio("Select Task", ['Detection', 'Segmentation'])
confidence = float(st.sidebar.slider("Model Confidence (%)", 25, 100, 40)) / 100

# Select Model
model_path = Path(settings.DETECTION_MODEL if task == 'Detection' else settings.SEGMENTATION_MODEL)

# Load YOLOv8 Model
try:
    model = helper.load_model(model_path)
except Exception as e:
    st.error(f"❌ Model loading failed: {model_path}")
    st.exception(e)

# Sidebar – Source Selection
st.sidebar.header("📷 Input Source")
source = st.sidebar.radio("Select Input Type", settings.SOURCES_LIST)

if source == settings.IMAGE:
    source_img = st.sidebar.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    col1, col2 = st.columns(2)

    with col1:
        if source_img is None:
            default_img = PIL.Image.open(settings.DEFAULT_IMAGE)
            st.image(default_img, caption="📎 Default Image", use_column_width=True)
        else:
            uploaded_img = PIL.Image.open(source_img)
            st.image(uploaded_img, caption="📎 Uploaded Image", use_column_width=True)

    with col2:
        if st.sidebar.button("🚀 Detect Objects"):
            try:
                img_to_use = uploaded_img if source_img else default_img
                results = model.predict(img_to_use, conf=confidence)
                output_img = results[0].plot()[:, :, ::-1]
                st.image(output_img, caption="✅ Detection Output", use_column_width=True)

                with st.expander("📋 Detection Details"):
                    for box in results[0].boxes:
                        st.write(box.data)
            except Exception as e:
                st.error("⚠️ Detection failed.")
                st.exception(e)

elif source == settings.VIDEO:
    helper.play_stored_video(confidence, model)

elif source == settings.WEBCAM:
    helper.play_webcam(confidence, model)

elif source == settings.RTSP:
    helper.play_rtsp_stream(confidence, model)

elif source == settings.YOUTUBE:
    helper.play_youtube_video(confidence, model)

else:
    st.error("🚫 Invalid source type selected.")
