from ultralytics import YOLO
import streamlit as st
import cv2
import yt_dlp
import settings

def load_model(model_name="yolov8n.pt"):
    return YOLO(model_name)  # Downloads from Ultralytics

def display_tracker_options():
    if st.sidebar.radio("Enable Tracker?", ("Yes", "No")) == "Yes":
        tracker = st.sidebar.radio("Tracker Type", ("bytetrack.yaml", "botsort.yaml"))
        return True, tracker
    return False, None

def _display_detected_frames(conf, model, st_frame, frame, track=False, tracker=None):
    frame = cv2.resize(frame, (720, int(720 * (9 / 16))))
    result = model.track(frame, conf=conf, persist=True, tracker=tracker) if track else model.predict(frame, conf=conf)
    output_frame = result[0].plot()
    st_frame.image(output_frame, channels="BGR", use_column_width=True)

def get_youtube_stream_url(url):
    ydl_opts = {'format': 'best[ext=mp4]', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)['url']

def play_youtube_video(conf, model):
    url = st.sidebar.text_input("📺 YouTube URL")
    track, tracker = display_tracker_options()
    if st.sidebar.button("🚀 Start Detection"):
        if not url:
            st.sidebar.warning("⚠️ Enter a YouTube URL")
            return
        try:
            st.sidebar.info("🔄 Loading Stream...")
            stream_url = get_youtube_stream_url(url)
            cap = cv2.VideoCapture(stream_url)
            st_frame = st.empty()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                _display_detected_frames(conf, model, st_frame, frame, track, tracker)
            cap.release()
        except Exception as e:
            st.sidebar.error(f"❌ {str(e)}")

def play_rtsp_stream(conf, model):
    rtsp_url = st.sidebar.text_input("🔌 RTSP Stream URL")
    st.sidebar.caption("E.g., rtsp://admin:123@192.168.1.210:554/Streaming/Channels/101")
    track, tracker = display_tracker_options()
    if st.sidebar.button("🚀 Start Detection"):
        try:
            cap = cv2.VideoCapture(rtsp_url)
            st_frame = st.empty()
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                _display_detected_frames(conf, model, st_frame, frame, track, tracker)
            cap.release()
        except Exception as e:
            st.sidebar.error(f"❌ {str(e)}")

def play_webcam(conf, model):
    track, tracker = display_tracker_options()
    if st.sidebar.button("🚀 Start Webcam"):
        cap = cv2.VideoCapture(settings.WEBCAM_PATH)
        st_frame = st.empty()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            _display_detected_frames(conf, model, st_frame, frame, track, tracker)
        cap.release()

def play_stored_video(conf, model):
    selected = st.sidebar.selectbox("🎞️ Choose a Video", settings.VIDEOS_DICT.keys())
    track, tracker = display_tracker_options()

    with open(settings.VIDEOS_DICT[selected], 'rb') as video_file:
        st.video(video_file.read())

    if st.sidebar.button("🚀 Detect in Video"):
        cap = cv2.VideoCapture(str(settings.VIDEOS_DICT[selected]))
        st_frame = st.empty()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            _display_detected_frames(conf, model, st_frame, frame, track, tracker)
        cap.release()
