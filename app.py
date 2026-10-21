
import streamlit as st
from google import genai

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="MediAI - Health Assistant",
    page_icon="🩺",
    layout="centered"
)

# ---------------- WEBSITE DESIGN ----------------

st.title("🩺 MediAI")
st.caption("Your AI-powered educational health assistant")

st.info(
    "MediAI provides educational health information. "
    "It cannot diagnose illnesses or prescribe medicines. "
    "For personal medical concerns, consult a qualified "
    "healthcare professional. Do not enter private information."
)

# ---------------- API KEY ----------------

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = ""

if not api_key:
    st.warning(
        "Setup needed: add your Gemini API key to "
        "Streamlit secrets before using the AI."
    )
    st.markdown(
        "See Step 5 below for the exact setup instructions."
    )
    st.stop()

client = genai.Client(api_key=api_key)

# ---------------- HEALTH SAFETY RULES ----------------

SYSTEM_PROMPT = """
You are MediAI, a friendly educational health assistant
created for a school project.

IMPORTANT RULES:
1. Give general, understandable health education.
2. Never claim to be a real doctor or diagnose a person.
3. Never prescribe medicines or give personal medication doses.
4. Never tell users to start, stop, or change medication.
5. Explain that symptoms can have multiple causes.
6. Encourage users to tell a trusted adult and contact
   a qualified healthcare professional for personal concerns.
7. For emergencies such as severe breathing difficulty,
   unconsciousness, severe bleeding, or suspected poisoning,
   tell the user to get emergency medical help immediately.
   In India, call 112 where available.
8. Do not request names, addresses, phone numbers, or
   unnecessary personal medical details.
9. For children, recommend involving a parent, guardian,
   school nurse, or another trusted adult.
10. If unsure, say so instead of guessing.
11. Do not claim to have examined the user or their records.
12. Keep answers kind, clear, and suitable for students.
13. Explain basic first aid only when it is safe and appropriate.
14. For potentially serious symptoms, do not reassure the user
    that everything is fine or delay urgent medical care.
15. If asked about a medical emergency, prioritize urgent
    action over a long educational explanation.

This is an educational chatbot, not a replacement for
professional medical assessment.
"""

# ---------------- EMERGENCY CHECK ----------------

EMERGENCY_TERMS = [
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "severe bleeding",
    "unconscious",
    "passed out",
    "poisoning",
    "overdose",
    "severe chest pain"
]

def emergency_message(question):
    text = question.lower()

    if any(term in text for term in EMERGENCY_TERMS):
        return (
            "⚠️ This could be an emergency. Please tell a "
            "trusted adult immediately and get emergency "
            "medical help now. In India, call 112 where "
            "available. Do not wait for an AI response."
        )

    return None

# ---------------- CHAT MEMORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello! 👋 I'm MediAI. I can explain health "
                "topics, healthy habits, common symptoms, and "
                "basic first aid. What would you like to learn?"
            )
        }
    ]

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ---------------- CHAT INPUT ----------------

question = st.chat_input(
    "Ask an educational health question..."
)

if question:
    # Display and store the user's question
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Check for possible emergencies first
    urgent_reply = emergency_message(question)

    with st.chat_message("assistant"):
        if urgent_reply:
            answer = urgent_reply
            st.error(answer)

        else:
            with st.spinner("MediAI is thinking..."):
                try:
                    # Send recent conversation context to Gemini
                    history = st.session_state.messages[-10:]

                    conversation = "\n".join(
                        f'{m["role"].upper()}: {m["content"]}'
                        for m in history
                    )

                    response = client.models.generate_content(
                        model="gemini-3.6-flash",
                        contents=(
                            SYSTEM_PROMPT
                            + "\n\nConversation:\n"
                            + conversation
                            + "\n\nReply to the latest user message."
                        )
                    )

                    answer = response.text

                    if not answer:
                        answer = (
                            "I couldn't generate an answer. "
                            "Please try again later."
                        )

                    st.markdown(answer)

                except Exception:
                    answer = (
                        "Sorry, I couldn't connect to the AI "
                        "service. Please check the API key, "
                        "internet connection, and API usage "
                        "limits, then try again."
                    )
                    st.error(answer)

    # Save the response for this session
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )

# ---------------- SIDEBAR ----------------

with st.sidebar:
    st.header("About MediAI")
    st.write(
        "MediAI is a school project that demonstrates "
        "how generative AI can explain general health topics."
    )

    st.subheader("Try asking")
    st.write("- What is dehydration?")
    st.write("- Why is sleep important?")
    st.write("- What is first aid?")
    st.write("- How can I prevent tooth decay?")

    if st.button("Clear conversation"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! 👋 I'm MediAI. What health topic "
                    "would you like to learn about?"
                )
            }
        ]
        st.rerun()

    st.caption(
        "Educational use only. Not for diagnosis or treatment."
    )
# Creator credit
st.markdown("---")

st.markdown(
    """
    <div style="text-align: center; padding: 15px;">
        <h3>🩺 MediAI</h3>
        <p>Your AI-powered health assistant</p>
        <p>Created with ❤️ by <b>Yash Raj Singh</b></p>
    </div>
    """,
    unsafe_allow_html=True
)