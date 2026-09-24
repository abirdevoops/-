import io
import time
import streamlit as st
from PIL import Image

from auth import (
    init_db, register_user, authenticate_user, get_user,
    is_admin, get_stats, get_recent_users, get_recent_scans,
    save_scan, delete_user, set_user_admin
)
from detector import TruthLensDetector, analyze_metadata, build_explanation

init_db()

st.set_page_config(
    page_title="TruthLens AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Premium UI ----------
st.markdown("""
<style>
.stApp {
 background:
 radial-gradient(circle at 8% 0%, rgba(32,217,255,.14), transparent 27%),
 radial-gradient(circle at 92% 5%, rgba(110,88,255,.16), transparent 30%),
 linear-gradient(135deg,#04101f 0%,#071b32 52%,#04101f 100%);
 color:#edf6ff;
}
.block-container{max-width:1250px;padding-top:1.4rem}
.tl-hero{
 padding:30px 32px;border-radius:26px;
 background:linear-gradient(135deg,rgba(11,43,76,.95),rgba(7,20,39,.88));
 border:1px solid rgba(72,207,255,.24);
 box-shadow:0 25px 70px rgba(0,0,0,.32);
}
.title{font-size:48px;font-weight:850;letter-spacing:-1.5px;margin:0}
.gradient{background:linear-gradient(90deg,#20d9ff,#79a7ff,#b48cff);
 -webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{font-size:17px;color:#b7c9df;margin-top:8px;line-height:1.6}
.badge{display:inline-block;padding:6px 12px;border-radius:999px;
background:rgba(32,217,255,.1);border:1px solid rgba(32,217,255,.3);
color:#6eeaff;font-weight:700;font-size:12px}
.card{padding:21px;border-radius:19px;background:rgba(8,29,52,.76);
border:1px solid rgba(180,205,235,.13);margin:10px 0}
.metric{padding:17px;border-radius:16px;background:rgba(255,255,255,.035);
border:1px solid rgba(255,255,255,.08);text-align:center}
.metric .v{font-size:28px;font-weight:850}.metric .l{color:#9fb2c9;font-size:12px}
.success{border-left:5px solid #17c964}.danger{border-left:5px solid #f04438}
.review{border-left:5px solid #ffb020}
.small{color:#9fb2c9;font-size:13px}
.footer{text-align:center;color:#6f829a;padding:30px 0 5px;font-size:12px}
div[data-testid="stFileUploader"]{border:1px dashed rgba(32,217,255,.38);
border-radius:18px;padding:8px;background:rgba(7,27,48,.55)}
</style>
""", unsafe_allow_html=True)

# ---------- Language ----------
TEXT = {
    "en": {
        "tag":"AI FOR DIGITAL TRUST",
        "sub":"A friendly AI assistant that screens images for signs of AI generation or manipulation.",
        "login":"Login","register":"Create account","logout":"Logout",
        "email":"Email","password":"Password","name":"Full name",
        "login_btn":"Sign in","register_btn":"Register",
        "upload":"Upload image","analyze":"🔎 Analyze with TruthLens",
        "waiting":"Upload a clear image to start.",
        "result":"TruthLens Assessment","ai":"LIKELY AI-GENERATED",
        "real":"LIKELY REAL","review":"NEEDS HUMAN REVIEW",
        "ai_signal":"AI-generation signal","real_signal":"Natural-image signal",
        "confidence":"Decision confidence","time":"Analysis time",
        "evidence":"Evidence","why":"Why this result?",
        "next":"Recommended next step","history":"My scan history",
        "admin":"Admin Control Center","users":"Users","scans":"Scans",
        "language":"Language","welcome":"Welcome",
    },
    "bn": {
        "tag":"ডিজিটাল ট্রাস্টের জন্য AI",
        "sub":"একটি সহজ AI সহকারী, যা ছবিতে AI-generated বা manipulation-এর সম্ভাব্য সংকেত খুঁজে দেখে।",
        "login":"লগইন","register":"অ্যাকাউন্ট তৈরি","logout":"লগআউট",
        "email":"ইমেইল","password":"পাসওয়ার্ড","name":"পূর্ণ নাম",
        "login_btn":"সাইন ইন","register_btn":"নিবন্ধন করুন",
        "upload":"ছবি আপলোড করুন","analyze":"🔎 TruthLens দিয়ে বিশ্লেষণ",
        "waiting":"বিশ্লেষণ শুরু করতে একটি পরিষ্কার ছবি আপলোড করুন।",
        "result":"TruthLens মূল্যায়ন","ai":"সম্ভবত AI-GENERATED",
        "real":"সম্ভবত REAL","review":"HUMAN REVIEW প্রয়োজন",
        "ai_signal":"AI-generation signal","real_signal":"Natural-image signal",
        "confidence":"Decision confidence","time":"Analysis time",
        "evidence":"প্রমাণ/সংকেত","why":"এই ফলাফল কেন?",
        "next":"পরবর্তী করণীয়","history":"আমার স্ক্যান ইতিহাস",
        "admin":"Admin Control Center","users":"Users","scans":"Scans",
        "language":"ভাষা","welcome":"স্বাগতম",
    }
}

if "lang" not in st.session_state:
    st.session_state.lang = "bn"
if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------- Header ----------
st.markdown("""
<div class="tl-hero">
<span class="badge">AI FOR DIGITAL TRUST • BANGLADESH</span>
<div class="title">Truth<span class="gradient">Lens</span> AI 🛡️</div>
<div class="subtitle">Digital Authenticity Assistant • AI-generated image screening • বাংলা + English</div>
</div>
""", unsafe_allow_html=True)

top1, top2, top3 = st.columns([1,1,1])
with top1:
    lang = st.selectbox("Language / ভাষা", ["বাংলা", "English"], index=0 if st.session_state.lang=="bn" else 1)
    st.session_state.lang = "bn" if lang=="বাংলা" else "en"
T = TEXT[st.session_state.lang]
with top3:
    if st.session_state.user_id:
        user = get_user(st.session_state.user_id)
        st.write(f"👤 **{user['name']}**")
        if st.button(T["logout"], use_container_width=True):
            st.session_state.user_id = None
            st.rerun()

# ---------- Authentication ----------
if not st.session_state.user_id:
    a, b = st.columns(2)
    with a:
        st.markdown(f"### 🔐 {T['login']}")
        email = st.text_input(T["email"], key="login_email")
        pw = st.text_input(T["password"], type="password", key="login_pw")
        if st.button(T["login_btn"], type="primary", use_container_width=True):
            user = authenticate_user(email, pw)
            if user:
                st.session_state.user_id = user["id"]
                st.success("Login successful.")
                st.rerun()
            else:
                st.error("Invalid email or password.")
    with b:
        st.markdown(f"### ✨ {T['register']}")
        name = st.text_input(T["name"], key="reg_name")
        email2 = st.text_input(T["email"], key="reg_email")
        pw2 = st.text_input(T["password"], type="password", key="reg_pw")
        pw3 = st.text_input("Confirm password", type="password", key="reg_pw2")
        if st.button(T["register_btn"], use_container_width=True):
            if pw2 != pw3:
                st.error("Passwords do not match.")
            elif len(pw2) < 6:
                st.error("Password must contain at least 6 characters.")
            else:
                ok, msg = register_user(name, email2, pw2)
                (st.success if ok else st.error)(msg)
    st.info("Create your own account. Your scan history is stored separately from other users.")
    st.stop()

# ---------- Load detector only after login ----------
@st.cache_resource(show_spinner=False)
def load_detector():
    return TruthLensDetector()

detector = load_detector()

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🛡️ TruthLens AI")
    st.caption("Digital Authenticity Assistant")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("**01** Upload → **02** Visual AI → **03** Metadata → **04** Evidence fusion → **05** Explainable result")
    st.markdown("---")
    st.warning("A detector score is not absolute proof. Verify important claims using the original source, date and context.")
    if is_admin(st.session_state.user_id):
        st.success("Admin access enabled.")

# ---------- Admin ----------
if is_admin(st.session_state.user_id):
    with st.expander("⚙️ " + T["admin"], expanded=False):
        stats = get_stats()
        s1,s2,s3 = st.columns(3)
        s1.metric(T["users"], stats["users"])
        s2.metric(T["scans"], stats["scans"])
        s3.metric("AI flagged", stats["ai_flagged"])
        st.markdown("#### Recent users")
        st.dataframe(get_recent_users(), use_container_width=True, hide_index=True)
        st.markdown("#### Recent scans")
        st.dataframe(get_recent_scans(), use_container_width=True, hide_index=True)
        st.caption("Admin database controls are intentionally kept inside the app. Passwords are stored as salted hashes, not plain text.")

# ---------- Main scanner ----------
st.markdown(f"### {T['welcome']} 👋")
left,right = st.columns([1.06,1], gap="large")

with left:
    st.markdown(f"### 📤 {T['upload']}")
    uploaded = st.file_uploader("JPG / JPEG / PNG / WEBP", type=["jpg","jpeg","png","webp"], label_visibility="collapsed")
    if uploaded:
        image_bytes = uploaded.getvalue()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        st.image(image, caption=f"{uploaded.name} • {image.width}×{image.height}", use_container_width=True)
        analyze = st.button(T["analyze"], type="primary", use_container_width=True)
    else:
        st.info(T["waiting"])
        analyze = False

with right:
    st.markdown("### 🧠 Multi-signal engine")
    st.markdown("""
    <div class="card">
    <b>Visual AI classifier</b><br><span class="small">Looks for learned patterns associated with synthetic/deepfake imagery.</span>
    </div>
    <div class="card">
    <b>Metadata inspection</b><br><span class="small">Reads available EXIF/file information without treating missing metadata as proof of fakery.</span>
    </div>
    <div class="card">
    <b>Conservative decision layer</b><br><span class="small">Strong signal → likely result. Uncertain signal → human review.</span>
    </div>
    """, unsafe_allow_html=True)

if uploaded and analyze:
    progress = st.progress(0, text="Preparing image…")
    start = time.time()
    progress.progress(20, text="Running visual AI analysis…")
    result = detector.predict(image)
    progress.progress(72, text="Checking metadata and file signals…")
    metadata = analyze_metadata(image, image_bytes, uploaded.name)
    progress.progress(100, text="Building explainable result…")
    explanation = build_explanation(result, metadata)
    elapsed = time.time() - start
    progress.empty()

    save_scan(st.session_state.user_id, uploaded.name, explanation["status"], explanation["confidence"], result["fake_probability"])

    st.markdown("---")
    st.markdown(f"## {T['result']}")

    if explanation["status"] == "LIKELY AI-GENERATED":
        cls, icon, label = "danger","⚠️",T["ai"]
    elif explanation["status"] == "LIKELY REAL":
        cls, icon, label = "success","✅",T["real"]
    else:
        cls, icon, label = "review","🟡",T["review"]

    st.markdown(f'<div class="card {cls}"><div style="font-size:30px;font-weight:850">{icon} {label}</div><div class="small">{explanation["headline"]}</div></div>', unsafe_allow_html=True)

    c1,c2,c3,c4 = st.columns(4)
    c1.markdown(f'<div class="metric"><div class="v">{result["fake_probability"]:.1f}%</div><div class="l">{T["ai_signal"]}</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="metric"><div class="v">{result["real_probability"]:.1f}%</div><div class="l">{T["real_signal"]}</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="metric"><div class="v">{explanation["confidence"]}%</div><div class="l">{T["confidence"]}</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="metric"><div class="v">{elapsed:.1f}s</div><div class="l">{T["time"]}</div></div>', unsafe_allow_html=True)

    st.markdown(f"### {T['evidence']}")
    e1,e2 = st.columns(2)
    with e1:
        st.markdown("**Visual AI signal**")
        st.progress(min(result["fake_probability"]/100,1.0), text=f"AI-generation: {result['fake_probability']:.1f}%")
        st.caption(result["model_note"])
    with e2:
        st.markdown("**Metadata / EXIF**")
        if metadata["has_exif"]:
            st.success(f"EXIF found • {metadata['exif_count']} fields")
        else:
            st.info("No readable EXIF found. This alone does not mean the image is fake.")
        st.caption(metadata["note"])

    st.markdown(f"### 💡 {T['why']}")
    for reason in explanation["reasons"]:
        st.markdown(f"- {reason}")

    st.markdown(f"### 🧭 {T['next']}")
    st.info(explanation["action"])

    with st.expander("Technical details"):
        st.json({"model":result["model_name"],"raw_label":result["raw_label"],
                 "fake_probability":round(result["fake_probability"],4),
                 "real_probability":round(result["real_probability"],4),
                 "metadata":metadata})

# ---------- Personal history ----------
st.markdown("---")
with st.expander(f"📚 {T['history']}"):
    st.dataframe(get_recent_scans(user_id=st.session_state.user_id, limit=30), use_container_width=True, hide_index=True)

st.markdown("""
<div class="card">
<b>🔐 Privacy by design</b><br>
<span class="small">This demo stores account information and scan summaries in SQLite. Images are analysed in memory and are not written to the database by this prototype.</span>
</div>
<div class="footer">TruthLens AI • Bangladesh-focused bilingual competition demo • Responsible AI prototype</div>
""", unsafe_allow_html=True)
