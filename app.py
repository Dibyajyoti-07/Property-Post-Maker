import streamlit as st
import streamlit.components.v1 as components

import branding
from generator_template import build_component_html, encode_logo

st.set_page_config(page_title="Property Post Maker", page_icon="\U0001F3E1")
st.title("Property Post Maker")
st.caption(branding.APPLICANT_CREDIT)

with st.form("post_form"):
    property_type = st.text_input("Property & Type", placeholder="4 BHK Luxury Villa, Ansal Golf City")
    location = st.text_input("Location", placeholder="Sushant Golf City, Lucknow")
    price = st.text_input("Price", placeholder="₹2.5 Cr onwards")
    highlights = st.text_area("Highlights", placeholder="3000 sq.ft · Corner plot · Ready to move")
    submitted = st.form_submit_button("Continue")

if submitted:
    fields = {
        "property_type": property_type.strip(),
        "location": location.strip(),
        "price": price.strip(),
        "highlights": highlights.strip(),
    }
    missing = [label for label, val in [
        ("Property & Type", fields["property_type"]),
        ("Location", fields["location"]),
        ("Price", fields["price"]),
        ("Highlights", fields["highlights"]),
    ] if not val]
    if missing:
        for label in missing:
            st.error(f"{label} is required.")
    else:
        st.session_state["fields"] = fields

if "fields" in st.session_state:
    branding_data = {
        "company_name": branding.COMPANY_NAME,
        "address": branding.ADDRESS,
        "manager_name": branding.MANAGER_NAME,
        "phone": branding.PHONE,
        "applicant_credit": branding.APPLICANT_CREDIT,
        "logo_data_uri": encode_logo(branding.LOGO_PATH),
    }
    html = build_component_html(st.session_state["fields"], branding_data)
    components.html(html, height=1700, scrolling=True)
