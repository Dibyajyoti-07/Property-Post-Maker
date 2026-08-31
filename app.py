import streamlit as st
import streamlit.components.v1 as components

import branding
from generator_template import build_component_html, encode_logo

st.set_page_config(page_title="Property Post Maker", page_icon="\U0001F3E1", layout="centered")

branding_data = {
    "company_name": branding.COMPANY_NAME,
    "address": branding.ADDRESS,
    "manager_name": branding.MANAGER_NAME,
    "phone": branding.PHONE,
    "applicant_credit": branding.APPLICANT_CREDIT,
    "logo_data_uri": encode_logo(branding.LOGO_PATH),
}
components.html(build_component_html(branding_data), height=900, scrolling=True)
