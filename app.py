import streamlit as st
import pickle
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
import string

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="SpamShield",
    page_icon="🛡️",
    layout="centered",
)

# ── NLTK downloads ───────────────────────────────────────────────────────────
nltk.download("punkt",     quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("punkt_tab", quiet=True)

# ── Load artefacts ───────────────────────────────────────────────────────────
tfidf = pickle.load(open("vectorizer.pkl", "rb"))
model = pickle.load(open("model.pkl",     "rb"))

ps = PorterStemmer()


def transform_text(text: str) -> str:
    text = text.lower()
    tokens = nltk.word_tokenize(text)
    alphanum = [t for t in tokens if t.isalnum()]
    filtered = [t for t in alphanum
                if t not in stopwords.words("english")
                and t not in string.punctuation]
    stemmed  = [ps.stem(t) for t in filtered]
    return " ".join(stemmed)


# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500&display=swap');

/* ── reset chrome ───────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }

.stApp {
    background: #0C0E16;
    font-family: 'Inter', sans-serif;
}
.block-container {
    padding-top: 3.5rem !important;
    padding-bottom: 3rem   !important;
    max-width: 660px       !important;
}

/* ── header ─────────────────────────────────── */
.spamshield-header {
    text-align: center;
    margin-bottom: 2.8rem;
}
.spamshield-header .logo {
    font-size: 3.2rem;
    display: block;
    margin-bottom: 0.6rem;
    filter: drop-shadow(0 0 22px rgba(129,140,248,.55));
}
.spamshield-header h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.3rem;
    font-weight: 700;
    color: #EEEEF5;
    margin: 0 0 0.4rem;
    letter-spacing: -0.6px;
}
.spamshield-header p {
    color: #6B6E85;
    font-size: 0.92rem;
    margin: 0;
}

/* ── field label ─────────────────────────────── */
.field-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #6B6E85;
    margin-bottom: 0.45rem;
}

/* ── textarea ────────────────────────────────── */
.stTextArea label          { display: none !important; }
.stTextArea textarea {
    background    : #141720 !important;
    border        : 1.5px solid #232638 !important;
    border-radius : 12px    !important;
    color         : #EEEEF5 !important;
    font-family   : 'Inter', sans-serif !important;
    font-size     : 0.95rem !important;
    line-height   : 1.6     !important;
    padding       : 14px 16px !important;
    caret-color   : #818CF8  !important;
    transition    : border-color .2s, box-shadow .2s !important;
    resize        : vertical !important;
}
.stTextArea textarea:focus {
    border-color : #818CF8 !important;
    box-shadow   : 0 0 0 3px rgba(129,140,248,.14) !important;
    outline      : none !important;
}
.stTextArea textarea::placeholder { color: #3A3D52 !important; }

/* ── button ──────────────────────────────────── */
.stButton > button {
    width         : 100% !important;
    background    : linear-gradient(135deg, #818CF8 0%, #6366F1 100%) !important;
    color         : #fff !important;
    border        : none !important;
    border-radius : 10px !important;
    padding       : 0.78rem 2rem !important;
    font-family   : 'Space Grotesk', sans-serif !important;
    font-size     : 0.95rem !important;
    font-weight   : 600 !important;
    letter-spacing: 0.02em !important;
    margin-top    : 0.8rem !important;
    transition    : transform .18s, box-shadow .18s !important;
}
.stButton > button:hover {
    transform  : translateY(-2px) !important;
    box-shadow : 0 10px 28px rgba(99,102,241,.38) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── warning override ────────────────────────── */
div[data-testid="stAlert"] {
    background    : rgba(255,180,0,.07) !important;
    border        : 1px solid rgba(255,180,0,.22) !important;
    border-radius : 10px !important;
    color         : #FFB400 !important;
    margin-top    : 1rem !important;
}

/* ── result card ─────────────────────────────── */
.result-card {
    border-radius : 16px;
    padding       : 2rem 1.75rem;
    margin-top    : 1.5rem;
    text-align    : center;
    animation     : fadeUp .35s ease forwards;
}
@keyframes fadeUp {
    from { opacity:0; transform:translateY(14px); }
    to   { opacity:1; transform:translateY(0);    }
}

.result-card.spam {
    background : rgba(255,59,71,.07);
    border     : 1.5px solid rgba(255,59,71,.28);
}
.result-card.safe {
    background : rgba(0,200,117,.07);
    border     : 1.5px solid rgba(0,200,117,.28);
}

.result-icon  { font-size:3rem; display:block; margin-bottom:.55rem; }
.result-title {
    font-family : 'Space Grotesk', sans-serif;
    font-size   : 1.55rem;
    font-weight : 700;
    margin      : 0 0 .35rem;
}
.result-card.spam .result-title { color: #FF5D66; }
.result-card.safe .result-title { color: #00C875; }

.result-desc { font-size:.85rem; color:#6B6E85; margin:0; line-height:1.5; }

/* ── stats row ───────────────────────────────── */
.stats-row {
    display   : flex;
    gap       : .85rem;
    margin-top: .85rem;
}
.stat-box {
    flex          : 1;
    background    : #141720;
    border        : 1px solid #232638;
    border-radius : 10px;
    padding       : .9rem .5rem;
    text-align    : center;
}
.stat-val {
    font-family : 'Space Grotesk', sans-serif;
    font-size   : 1.35rem;
    font-weight : 700;
    color       : #EEEEF5;
}
.stat-lbl {
    font-size      : 0.68rem;
    color          : #6B6E85;
    text-transform : uppercase;
    letter-spacing : .07em;
    margin-top     : 3px;
}

/* ── thin divider ─────────────────────────────── */
.thin-div { height:1px; background:#1E2030; margin:2.2rem 0; }
</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="spamshield-header">
    <span class="logo">🛡️</span>
    <h1>SpamShield</h1>
    <p>Paste any SMS and know in an instant — spam or safe.</p>
</div>
""", unsafe_allow_html=True)


# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="field-label">Message</div>', unsafe_allow_html=True)

sms = st.text_area(
    label       = "",
    placeholder = 'e.g. "Congratulations! You\'ve been selected for a FREE £500 gift card. Claim now: bit.ly/…"',
    height      = 140,
    key         = "sms_input",
)


# ── Analyse ───────────────────────────────────────────────────────────────────
if st.button("Analyse Message"):
    if not sms.strip():
        st.warning("Paste or type a message above to analyse it.")
    else:
        transformed  = transform_text(sms)
        vector_input = tfidf.transform([transformed])
        result       = model.predict(vector_input)[0]

        words = len(sms.split())
        chars = len(sms)

        if result == 1:
            risk_html = '<div class="stat-val" style="color:#FF5D66">High</div>'
            card_html = f"""
            <div class="result-card spam">
                <span class="result-icon">🚨</span>
                <p class="result-title">Spam Detected</p>
                <p class="result-desc">
                    This message carries strong markers of spam or phishing.<br>
                    Do not click any links or share personal details.
                </p>
            </div>
            """
        else:
            risk_html = '<div class="stat-val" style="color:#00C875">Low</div>'
            card_html = f"""
            <div class="result-card safe">
                <span class="result-icon">✅</span>
                <p class="result-title">Looks Safe</p>
                <p class="result-desc">
                    No spam patterns detected in this message.
                </p>
            </div>
            """

        st.markdown(card_html, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="stats-row">
            <div class="stat-box">
                <div class="stat-val">{words}</div>
                <div class="stat-lbl">Words</div>
            </div>
            <div class="stat-box">
                <div class="stat-val">{chars}</div>
                <div class="stat-lbl">Characters</div>
            </div>
            <div class="stat-box">
                {risk_html}
                <div class="stat-lbl">Risk Level</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Footer divider ─────────────────────────────────────────────────────────────
st.markdown('<div class="thin-div"></div>', unsafe_allow_html=True)
st.markdown(
    '<p style="text-align:center;color:#3A3D52;font-size:.75rem;">'
    'Powered by TF-IDF + Naive Bayes &nbsp;·&nbsp; SpamShield'
    '</p>',
    unsafe_allow_html=True,
)