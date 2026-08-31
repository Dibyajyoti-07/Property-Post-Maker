import os

import streamlit as st
import streamlit.components.v1 as components

import branding
from generator_template import build_component_html, encode_logo


def _load_env(path=".env"):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


_load_env()


def _secret(name, default=""):
    # Streamlit Cloud's secrets.toml doesn't always land in os.environ, so check
    # st.secrets first; local dev has no secrets.toml, so that lookup is skipped.
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.environ.get(name, default)

st.set_page_config(page_title="Property Post Maker", page_icon="\U0001F3E1", layout="wide")
st.markdown(
    "<style>"
    ".stApp{background:#0d0d0f}"
    ".block-container{padding:0;max-width:100%}"
    "header[data-testid='stHeader']{background:transparent}"
    "iframe{display:block}"
    "</style>",
    unsafe_allow_html=True,
)

branding_data = {
    "company_name": branding.COMPANY_NAME,
    "address": branding.ADDRESS,
    "manager_name": branding.MANAGER_NAME,
    "phone": branding.PHONE,
    "applicant_credit": branding.APPLICANT_CREDIT,
    "logo_data_uri": encode_logo(branding.LOGO_PATH),
    "groq_api_key": _secret("GROQ_API_KEY"),
    "groq_model": _secret("GROQ_MODEL", "openai/gpt-oss-120b"),
}
if not branding_data["groq_api_key"]:
    st.error("GROQ_API_KEY is not set (add it to .env locally, or as a secret on the deploy host).")
    st.stop()
components.html(build_component_html(branding_data), height=700, scrolling=False)
