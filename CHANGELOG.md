# Changelog — ElderEase AI

All notable changes to this project are documented here.

## [Amazon Hackathon Edition] — October 2026

This edition builds on the original ElderEase AI wellbeing companion with a separate simulated Alexa+ conversational experience.

### Added
- **Alexa+ Companion Experience:** Added a dedicated Streamlit page at `pages/2_Alexa_Plus.py`.
- **Contextual follow-up conversations:** The experience acknowledges the user's latest message and refers to earlier conversation context.
- **Everyday Care reminders:** Added a reminder form to save and display reminders during the current session.
- **Conversation management:** Added a control to clear the current conversation.
- **Prototype disclosure:** Clearly states that the Alexa+ experience is simulated and is not connected to a live Alexa device.
- **README screenshots:** Added screenshots showing the Alexa+ conversation and Everyday Care reminder interface.

### Safety and usability
- Preserved the existing mood detection, supportive response, activity suggestion, and safety-response functionality.
- Tested a loneliness-related conversation with a contextual follow-up.
- Tested saving and displaying an everyday reminder.
- Tested a configured safety-concern phrase to verify that the safety response is triggered.

### Known limitations
- The Alexa+ experience is a simulation, not a live Alexa integration.
- Mood and safety detection rely on configured rules and may not recognise every expression.
- Everyday Care reminders are stored for the current session and do not trigger real notifications.
- Conversation and reminder state may be lost when the session resets.

### Verification
- Manual checks: the scenarios listed above were tested in the Amazon project copy.
- Automated tests: results should be recorded after running the test suite in this copy.

---

