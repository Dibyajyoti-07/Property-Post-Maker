import streamlit as st
import streamlit.components.v1 as components

import branding
from generator_template import build_component_html, encode_logo

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
}
components.html(build_component_html(branding_data), height=700, scrolling=False)
