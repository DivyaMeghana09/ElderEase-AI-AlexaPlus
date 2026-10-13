
import streamlit as st
from datetime import datetime

from mood_engine import (
    detect_mood,
    detect_safety_concern,
    generate_support_response,
    SAFETY_RESPONSE,
)
from activity_engine import get_activity

st.set_page_config(
    page_title="ElderEase | Alexa+ Experience",
    page_icon="💙",
    layout="centered",
)

st.title("💙 ElderEase AI")
st.subheader("Alexa+ Companion Experience")
st.caption("A gentle conversational wellbeing companion for older adults.")

st.info(
    "Hackathon prototype: this simulates an Alexa+ experience "
    "and is not connected to a live Alexa device."
)

# Session state
if "alexa_chat" not in st.session_state:
    st.session_state.alexa_chat = []
if "care_reminders" not in st.session_state:
    st.session_state.care_reminders = []
if "awaiting_followup" not in st.session_state:
    st.session_state.awaiting_followup = False
if "last_mood" not in st.session_state:
    st.session_state.last_mood = "Okay"
if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""

FOLLOWUP_QUESTIONS = {
    "Lonely": "Would you like to tell me what you've been missing most today?",
    "Sad": "Would you like to share what has been making today difficult?",
    "Anxious": "Would it help to talk about what's worrying you most?",
    "Tired": "Have you had a chance to rest today?",
    "Happy": "What made you happy today?",
    "Okay": "What might make today a little better?",
}

st.divider()
st.markdown("## 💬 Talk to ElderEase")

# Keep the conversation immediately above its input.
chat_area = st.container()

with chat_area:
    if not st.session_state.alexa_chat:
        st.write(
            "Hello! 💙 Tell me how you're feeling. "
            "I'm here to listen."
        )

    for message in st.session_state.alexa_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Use a regular form input so the input appears directly below the chat.
with st.form("alexa_chat_form", clear_on_submit=True):
    user_message = st.text_input(
        "Your message",
        placeholder="Tell ElderEase how you are feeling...",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Send 💙", use_container_width=True)

if submitted and user_message.strip():
    user_message = user_message.strip()
    st.session_state.alexa_chat.append(
        {"role": "user", "content": user_message}
    )

    if detect_safety_concern(user_message):
        response = SAFETY_RESPONSE
        st.session_state.awaiting_followup = False

    elif st.session_state.awaiting_followup:
        previous_mood = st.session_state.last_mood
        previous_topic = st.session_state.last_topic

        response = (
            "Thank you for sharing that with me. 💙 "
            "It sounds like this matters to you."
        )
        response += f"\n\nI hear you saying: “{user_message}”"

        if previous_topic:
            response += (
                f"\n\nEarlier, you mentioned: “{previous_topic}”"
            )

        response += (
            "\n\nWould you like to continue talking, "
            "or try a small activity?"
        )
        response += f"\n\n🌿 A gentle suggestion: {get_activity(previous_mood)}"

        st.session_state.last_topic = user_message
        st.session_state.awaiting_followup = False

    else:
        mood = detect_mood(user_message)
        response = generate_support_response(mood, user_message)
        response += "\n\n" + FOLLOWUP_QUESTIONS.get(
            mood, FOLLOWUP_QUESTIONS["Okay"]
        )
        response += f"\n\n🌿 If you'd like, try: {get_activity(mood)}"

        st.session_state.last_mood = mood
        st.session_state.last_topic = user_message
        st.session_state.awaiting_followup = True

    st.session_state.alexa_chat.append(
        {"role": "assistant", "content": response}
    )
    st.rerun()

st.divider()
st.markdown("## 🌿 Everyday Care")

with st.form("reminder_form", clear_on_submit=True):
    reminder_text = st.text_input(
        "What would you like to remember?",
        placeholder="For example, call my daughter this evening",
    )
    reminder_submitted = st.form_submit_button("🔔 Save reminder")

if reminder_submitted:
    if reminder_text.strip():
        st.session_state.care_reminders.append({
            "task": reminder_text.strip(),
            "created": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        })
        st.success("Reminder saved for this session.")
    else:
        st.warning("Please enter a reminder.")

for reminder in st.session_state.care_reminders:
    st.write(f"🔔 {reminder['task']} — {reminder['created']}")

if st.button("Clear conversation"):
    st.session_state.alexa_chat = []
    st.session_state.awaiting_followup = False
    st.session_state.last_mood = "Okay"
    st.session_state.last_topic = ""
    st.rerun()

st.divider()
st.caption(
    "ElderEase provides non-medical emotional support. "
    "It does not replace professional care or emergency services."
)
