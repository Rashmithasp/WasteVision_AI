from datetime import datetime
from html import escape
from io import BytesIO
from pathlib import Path

import streamlit as st
from PIL import Image, UnidentifiedImageError

from src.classifier import CATEGORIES, MODEL_ID, predict
from src.guidance import GUIDANCE

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
SAMPLE_IMAGE_DIR = Path(__file__).parent / "sample_images"
SAMPLE_IMAGES = sorted(
    path for path in SAMPLE_IMAGE_DIR.glob("*") if path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
)
CATEGORY_ICONS = {
    "plastic": "◈",
    "paper": "▤",
    "glass": "◇",
    "metal": "⬡",
    "organic": "✿",
    "electronic": "⌁",
    "mixed": "◌",
}

st.set_page_config(
    page_title="WasteVision | AI for a Cleaner Future",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
    :root { --forest: #10251d; --emerald: #27d69a; --mint: #a9f3d5; --ink: #101b17; --muted: #9baea4; }
    html, body, [data-testid="stAppViewContainer"] { background: #07120e; color: #f2f7f4; font-family: 'DM Sans', sans-serif; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stSidebar"] { background: #0c1b14; border-right: 1px solid #1b3528; }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #b9c9c0; }
    [data-testid="stMainBlockContainer"] { max-width: 1440px; padding-top: 2rem; padding-bottom: 4rem; }
    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: 0; color: #f4faf6; }
    .brand-lockup { display:flex; align-items:center; gap:12px; padding: 4px 0 26px; }
    .brand-mark { width:42px; height:42px; display:grid; place-items:center; border-radius:13px; background:#153c2b; color:#65e6b1; font-size:23px; }
    .brand-name { font:800 19px 'Manrope',sans-serif; color:#f2f7f4; }
    .brand-tag { color:#91a69a; font-size:11px; letter-spacing:1.1px; text-transform:uppercase; }
    .hero { position:relative; overflow:hidden; border:1px solid #244333; border-radius:18px; padding:34px 38px; margin:0 0 22px; background:linear-gradient(115deg,#10251d 0%,#123725 54%,#0c2319 100%); }
    .hero:after { content:'♻'; position:absolute; right:5%; top:-48px; font-size:220px; line-height:1; color:rgba(128,235,188,.055); transform:rotate(-18deg); }
    .eyebrow { color:#75e8b5; font-size:11px; font-weight:700; letter-spacing:1.8px; text-transform:uppercase; }
    .hero h1 { font-size:40px; line-height:1.12; margin:10px 0 9px; }
    .hero p { color:#bdd0c5; font-size:15px; max-width:650px; margin:0; }
    .section-label { color:#85a294; font-size:11px; font-weight:700; letter-spacing:1.4px; text-transform:uppercase; margin:6px 0 12px; }
    .metric-card { min-height:112px; padding:17px 19px; border:1px solid #1c382a; border-radius:12px; background:#0d1c15; }
    .metric-label { color:#9db0a5; font-size:12px; }
    .metric-value { color:#f4faf6; font:800 27px 'Manrope',sans-serif; margin-top:7px; }
    .metric-note { color:#6fe2ae; font-size:11px; margin-top:1px; }
    .result-title { color:#f5faf7; font:700 21px 'Manrope',sans-serif; margin:2px 0 3px; }
    .result-score { color:#6fe2ae; font:800 30px 'Manrope',sans-serif; }
    .result-meta { color:#93a99c; font-size:12px; }
    .mini-row { display:flex; justify-content:space-between; gap:12px; padding:11px 0; border-bottom:1px solid #20362b; font-size:13px; }
    .mini-row:last-child { border-bottom:0; }
    .empty-state { text-align:center; padding:35px 15px; color:#9aafa2; }
    .empty-icon { font-size:34px; color:#4ad49a; margin-bottom:8px; }
    .callout { border-left:3px solid #42d89c; background:#10251b; color:#c3d4ca; padding:13px 15px; border-radius:0 8px 8px 0; font-size:13px; }
    div.stButton > button[kind="primary"] { background:#36d69a; border:0; color:#062016; font-weight:700; border-radius:9px; min-height:44px; }
    div.stButton > button[kind="primary"]:hover { background:#75eabb; color:#062016; border:0; }
    [data-testid="stFileUploader"] { border-radius:10px; }
    [data-testid="stFileUploader"] section { background:#0c1b14; border:1px dashed #345342; border-radius:10px; }
    [data-testid="stMetric"] { background:#0d1c15; border:1px solid #1c382a; border-radius:12px; padding:14px 16px; }
    [data-testid="stMetricLabel"] p { color:#9db0a5; }
    [data-testid="stMetricValue"] { color:#f4faf6; }
    [data-testid="stExpander"] { border-color:#1c382a; background:#0c1b14; }
    hr { border-color:#1c382a; }
    @media (max-width: 700px) { [data-testid="stMainBlockContainer"] { padding:1rem 1rem 3rem; } .hero { padding:25px 21px; } .hero h1 { font-size:30px; } .hero:after { right:-30px; font-size:150px; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def initialize_session() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("last_result", None)


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            '<div class="brand-lockup"><div class="brand-mark">♻</div><div><div class="brand-name">WasteVision</div><div class="brand-tag">Cleaner choices, clearer future</div></div></div>',
            unsafe_allow_html=True,
        )
        section = st.radio("Workspace", ["Dashboard", "Sorting guide"], label_visibility="collapsed")
        st.divider()
        st.markdown("**AI engine**")
        st.caption("CLIP zero-shot image classification")
        st.caption(f"Model: `{MODEL_ID}`")
        st.divider()
        st.caption("Your scan history stays in this browser session and is cleared when the session ends.")
    return section


def render_hero() -> None:
    st.markdown(
        '<section class="hero"><div class="eyebrow">AI-assisted waste sorting</div><h1>Small choices.<br>Cleaner future.</h1><p>Turn a photo into a practical next step. Identify a likely material, understand its disposal options, and make your next move count.</p></section>',
        unsafe_allow_html=True,
    )


def open_uploaded_image(uploaded_file) -> Image.Image:
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise ValueError("This image is larger than 10 MB. Choose a smaller file and try again.")
    try:
        image = Image.open(BytesIO(uploaded_file.getvalue()))
        image.verify()
        image = Image.open(BytesIO(uploaded_file.getvalue()))
        image.load()
        return image.convert("RGB")
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("That file could not be read as a valid image. Try a JPG, PNG, or WEBP image.") from exc


def make_distribution_chart(history: list[dict]) -> dict[str, int]:
    counts = {key: 0 for key in CATEGORIES}
    for scan in history:
        counts[scan["label"]] += 1
    return {CATEGORIES[key]["name"]: value for key, value in counts.items()}


def render_result(result: dict | None) -> None:
    st.markdown('<div class="section-label">Latest identification</div>', unsafe_allow_html=True)
    with st.container(border=True):
        if result is None:
            st.markdown('<div class="empty-state"><div class="empty-icon">◉</div><strong>No scan yet</strong><br>Upload a photo and run an analysis to see category insights here.</div>', unsafe_allow_html=True)
            return

        top = result["predictions"][0]
        icon = CATEGORY_ICONS[top["label"]]
        st.markdown(f'<div class="eyebrow">Most likely category</div><div class="result-title">{icon} &nbsp;{top["name"]}</div><div class="result-score">{top["score"] * 100:.1f}%</div><div class="result-meta">Relative CLIP score, not a calibrated probability</div>', unsafe_allow_html=True)
        st.progress(top["score"])
        st.markdown("**Other likely matches**")
        for prediction in result["predictions"][1:3]:
            st.markdown(
                f'<div class="mini-row"><span>{CATEGORY_ICONS[prediction["label"]]} &nbsp;{prediction["name"]}</span><strong>{prediction["score"] * 100:.1f}%</strong></div>',
                unsafe_allow_html=True,
            )
        guidance = GUIDANCE[top["label"]]
        st.markdown(f'**{guidance["status"]}**')
        st.write(guidance["steps"])
        if top["label"] == "electronic":
            st.warning("Battery and e-waste safety: use an authorized collection point. Never place batteries in household recycling or general waste.")
        st.caption("Collection rules differ by location. Confirm requirements with your local waste authority.")


def render_dashboard() -> None:
    render_hero()
    history = st.session_state.history
    total = len(history)
    counts = {key: sum(scan["label"] == key for scan in history) for key in CATEGORIES}
    leading = max(counts, key=counts.get) if total else None

    metric_columns = st.columns(3)
    metric_data = [
        ("TOTAL SCANS", str(total), "This session"),
        ("MOST SEEN", CATEGORIES[leading]["name"] if leading else "Awaiting scans", f"{counts[leading]} scans" if leading else "Your first scan starts here"),
        ("CATEGORIES", f"{sum(value > 0 for value in counts.values())} / 7", "Materials identified"),
    ]
    for column, (label, value, note) in zip(metric_columns, metric_data):
        with column:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>', unsafe_allow_html=True)

    st.write("")
    upload_column, result_column = st.columns([0.92, 1.08], gap="large")
    with upload_column:
        st.markdown('<div class="section-label">01 / Add a photo</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### Identify an item")
            st.write("Use a clear photo with one main item in view for the most useful estimate.")
            uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")
            st.caption("JPG, PNG, or WEBP · maximum 10 MB")
            image = None
            if uploaded_file:
                try:
                    image = open_uploaded_image(uploaded_file)
                    st.image(image, caption=uploaded_file.name, use_container_width=True)
                except ValueError as exc:
                    st.error(str(exc))
            elif SAMPLE_IMAGES:
                selected_sample = st.selectbox("Or try a local demo image", SAMPLE_IMAGES, format_func=lambda path: path.name)
                try:
                    image = Image.open(selected_sample).convert("RGB")
                    st.image(image, caption=f"Demo image · {selected_sample.name}", use_container_width=True)
                except (OSError, Image.DecompressionBombError) as exc:
                    st.error(f"The local demo image could not be opened: {exc}")

            analyze = st.button("Analyze this item", type="primary", use_container_width=True, disabled=image is None)
            if analyze and image is not None:
                with st.spinner("Loading CLIP and comparing material categories. The first run may download model files..."):
                    try:
                        predictions = predict(image)
                        scan = {
                            "label": predictions[0]["label"],
                            "name": predictions[0]["name"],
                            "score": predictions[0]["score"],
                            "predictions": predictions[:3],
                            "filename": uploaded_file.name if uploaded_file else selected_sample.name,
                            "time": datetime.now().strftime("%H:%M"),
                        }
                        st.session_state.history.insert(0, scan)
                        st.session_state.last_result = scan
                        st.rerun()
                    except Exception as exc:
                        st.error("The image could not be analyzed. Check your connection for the initial model download and confirm the installed dependencies.")
                        st.caption(f"Details: {exc}")

    with result_column:
        render_result(st.session_state.last_result)

    st.write("")
    chart_column, history_column = st.columns([1, 1], gap="large")
    with chart_column:
        st.markdown('<div class="section-label">Session overview</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### Category distribution")
            if history:
                st.bar_chart(make_distribution_chart(history), height=290)
            else:
                st.markdown('<div class="empty-state"><div class="empty-icon">▥</div>Category counts will appear after your first scan.</div>', unsafe_allow_html=True)
    with history_column:
        st.markdown('<div class="section-label">Recent activity</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### Scan history")
            if history:
                for scan in history[:6]:
                    filename = escape(scan["filename"])
                    st.markdown(
                        f'<div class="mini-row"><span>{CATEGORY_ICONS[scan["label"]]} &nbsp;<strong>{scan["name"]}</strong><br><span class="result-meta">{filename} · {scan["time"]}</span></span><strong>{scan["score"] * 100:.1f}%</strong></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<div class="empty-state"><div class="empty-icon">◷</div>Your scans will be collected here for this session.</div>', unsafe_allow_html=True)


def render_guide() -> None:
    render_hero()
    st.markdown("## Sort with confidence, not guesswork")
    st.write("A material estimate is a useful starting point. Cleanliness, local facilities, and product construction all affect what can actually be recycled or composted.")
    columns = st.columns(2, gap="large")
    for index, (category, details) in enumerate(GUIDANCE.items()):
        with columns[index % 2]:
            with st.container(border=True):
                st.markdown(f"### {CATEGORY_ICONS[category]} &nbsp;{CATEGORIES[category]['name']}")
                st.markdown(f"**{details['status']}**")
                st.write(details["steps"])
                if category == "electronic":
                    st.warning("Keep batteries and electronics out of household bins. Look for an authorized e-waste collection point.")
    st.markdown(
        '<div class="callout"><strong>Why segregation matters</strong><br>Keeping materials separate can help recycling and composting programs handle them correctly, reduce contamination, and recover useful materials. Always check your local collection rules because accepted items vary.</div>',
        unsafe_allow_html=True,
    )


initialize_session()
page = render_sidebar()
if page == "Dashboard":
    render_dashboard()
else:
    render_guide()

st.markdown("---")
st.caption("WasteVision is an educational assistant. CLIP scores are relative model scores, not calibrated probabilities or disposal guarantees. Local regulations and accepted materials vary.")
