
import streamlit as st
from datetime import datetime

from mood_engine import (
    detect_mood,
    detect_safety_concern,
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
if "conversation_turn" not in st.session_state:
    st.session_state.conversation_turn = 0

# First question after the user's initial message
FOLLOWUP_QUESTIONS = {
    "Lonely": "Who have you been missing or wishing you could talk to?",
    "Sad": "Would you like to tell me a little more about what's been difficult?",
    "Anxious": "What is worrying you the most right now?",
    "Tired": "What might help you feel a little more comfortable today?",
    "Happy": "What made you happy today?",
    "Okay": "What might make today a little better for you?",
}

# Questions used to continue the conversation
CONTINUATION_QUESTIONS = {
    "Lonely": [
        "Would talking to that person today feel possible?",
        "What is something you enjoy doing together?",
    ],
    "Sad": [
        "What do you think would help you feel supported right now?",
        "Is there someone you feel comfortable talking to about this?",
    ],
    "Anxious": [
        "Is there one small thing that might make this feel more manageable?",
        "Would you like to talk through what you can do next?",
    ],
    "Tired": [
        "Would a quiet break or a favourite activity feel better?",
        "What usually helps you relax?",
    ],
    "Happy": [
        "What was your favourite part of that experience?",
        "Would you like to make more time for moments like that?",
    ],
    "Okay": [
        "Is there something small you would enjoy doing today?",
        "Would connecting with someone you care about help?",
    ],
}

# Alexa Plus uses its own response style instead of the main app template.
ALEXA_OPENINGS = {
    "Lonely": "I'm glad you came to talk with me. You don't have to put everything into words at once.",
    "Sad": "I'm here to listen. You can share as much or as little as feels comfortable.",
    "Anxious": "Let's take this one step at a time. You don't need to figure everything out at once.",
    "Tired": "It sounds like today may be taking a lot out of you. Let's keep things gentle.",
    "Happy": "I'm glad you shared that with me. It sounds like something worth remembering.",
    "Okay": "Thanks for checking in with me. We can take today one small step at a time.",
}


def shorten(text, limit=180):
    text = text.strip()
    if len(text) > limit:
        return text[:limit].rstrip() + "..."
    return text


st.divider()
st.markdown("## 💬 Talk to ElderEase")

# Conversation appears directly above the input.
with st.container():
    if not st.session_state.alexa_chat:
        st.write(
            "Hello! 💙 How are you feeling today? "
            "I'm here to listen, and we can talk at your pace."
        )

    for message in st.session_state.alexa_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

with st.form("alexa_chat_form", clear_on_submit=True):
    user_message = st.text_input(
        "Your message",
        placeholder="Tell ElderEase what's on your mind...",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button(
        "Send 💙",
        use_container_width=True,
    )

if submitted and user_message.strip():
    user_message = user_message.strip()

    st.session_state.alexa_chat.append(
        {"role": "user", "content": user_message}
    )

    if detect_safety_concern(user_message):
        # Safety handling always takes priority.
        response = SAFETY_RESPONSE
        st.session_state.awaiting_followup = False
        st.session_state.conversation_turn = 0

    elif st.session_state.awaiting_followup:
        mood = st.session_state.last_mood
        previous_topic = st.session_state.last_topic

        # Acknowledge the user's new message and connect it to
        # what they shared earlier.
        response = (
            "Thank you for telling me a little more. 💙 "
            "I'm listening."
        )

        if previous_topic:
            response += (
                f"\n\nEarlier, you mentioned: "
                f"“{shorten(previous_topic, 100)}”"
            )

        response += (
            f"\n\nIt sounds like you're sharing: "
            f"“{shorten(user_message, 140)}”"
        )

        questions = CONTINUATION_QUESTIONS.get(
            mood, CONTINUATION_QUESTIONS["Okay"]
        )

        question_index = (
            st.session_state.conversation_turn % len(questions)
        )
        next_question = questions[question_index]

        response += f"\n\n{next_question}"
        response += (
            f"\n\n🌿 If it feels helpful, you could try: "
            f"{get_activity(mood)}"
        )

        st.session_state.conversation_turn += 1
        st.session_state.last_topic = user_message
        # Keep the conversation open for another reply.
        st.session_state.awaiting_followup = True

    else:
        mood = detect_mood(user_message)

        response = ALEXA_OPENINGS.get(
            mood, ALEXA_OPENINGS["Okay"]
        )

        response += (
            f"\n\nYou mentioned: “{shorten(user_message, 140)}”"
        )

        response += (
            "\n\n" + FOLLOWUP_QUESTIONS.get(
                mood, FOLLOWUP_QUESTIONS["Okay"]
            )
        )

        response += (
            f"\n\n🌿 If you'd like, you could try: "
            f"{get_activity(mood)}"
        )

        st.session_state.last_mood = mood
        st.session_state.last_topic = user_message
        st.session_state.awaiting_followup = True
        st.session_state.conversation_turn = 0

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
    st.session_state.conversation_turn = 0
    st.rerun()

st.divider()
st.caption(
    "ElderEase provides non-medical emotional support. "
    "It does not replace professional care or emergency services."
)
