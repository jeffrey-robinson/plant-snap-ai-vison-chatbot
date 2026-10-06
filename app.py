import streamlit as st
from plantsnap.ai import create_chat, create_gemini_client, send_message
from plantsnap.whatsapp import send_whatsapp
from prompts import SUMMARY_REQUEST_PROMPT, WELCOME_MESSAGE_TEMPLATE


@st.cache_resource
def get_gemini_client(api_key):
    return create_gemini_client(api_key)


gemini_client = get_gemini_client(st.secrets["GEMINI_API_KEY"])

if "onboarded" not in st.session_state:
    st.title("PlantSnap 🌱")
    st.caption("Your instant plant identification and care buddy.")
    with st.form("onboarding_form"):
        name = st.text_input("Your name")
        whatsapp_number = st.text_input(
            "WhatsApp number (with country code)",
            placeholder="+91XXXXXXXXXX",
        )
        submitted = st.form_submit_button("Let's go 🚀")
    if submitted:
        if not name.strip() or not whatsapp_number.strip():
            st.warning("Please fill in both your name and WhatsApp number.")
        else:
            st.session_state.name = name.strip()
            st.session_state.whatsapp_number = whatsapp_number.strip()
            st.session_state.chat = create_chat(gemini_client)
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": WELCOME_MESSAGE_TEMPLATE.format(name=name.strip()),
                }
            ]
            st.session_state.onboarded = True
            st.rerun()
    st.stop()

header_col, button_col = st.columns([5, 2], vertical_alignment="center")

with header_col:
    st.title("PlantSnap")
    st.caption("Your instant plant identification and care buddy.")

with button_col:
    send_disabled = len(st.session_state.messages) <= 2
    if st.button(
        "Send details to WhatsApp",
        disabled=send_disabled,
        use_container_width=True,
    ):
        with st.spinner("Summarizing your plants..."):
            summary, chat, summary_error = send_message(
                gemini_client,
                st.session_state.chat,
                [SUMMARY_REQUEST_PROMPT],
            )
            st.session_state.chat = chat

        if summary_error:
            st.warning(summary_error)
        else:
            success, info = send_whatsapp(
                st.secrets,
                st.session_state.whatsapp_number,
                st.session_state.name,
                summary,
            )
            if success:
                st.success("Sent! Check your WhatsApp.")
            else:
                st.error(info)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Describe your plant or its symptoms"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, chat, answer_error = send_message(
                gemini_client,
                st.session_state.chat,
                prompt,
            )
            st.session_state.chat = chat
        if answer_error:
            st.warning(answer_error)
        else:
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
