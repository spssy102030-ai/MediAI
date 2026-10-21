
import streamlit as st
from google import genai

# --------------------------------------------------
# MediAI 2.0 — Created by Yash Raj Singh
# --------------------------------------------------

st.set_page_config(
    page_title="MediAI | Health Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are MediAI, an educational health-information assistant.

YOUR PURPOSE
Explain health conditions, diseases, symptoms, injuries,
prevention, nutrition, general first aid and medical terms
in simple, friendly English.

FOR HEALTH CONDITIONS, ORGANIZE ANSWERS AS APPROPRIATE:
1. What it is
2. Common causes and risk factors
3. Common symptoms
4. Important warning signs
5. Food, hydration and nutrition guidance
6. What to do and what to avoid
7. Prevention
8. When to seek medical care
9. Trustworthy references for further reading

ACCURACY
- Be honest about uncertainty and limitations.
- Never invent facts, statistics, citations or cures.
- Similar symptoms can have different causes.
- Never claim to diagnose a person through chat.
- Never claim to know every disease or medical fact.
- Distinguish established evidence from uncertain claims.
- Do not claim to have searched the web or a database
  unless a search tool was actually used.

FOOD AND NUTRITION
- Give balanced, practical, evidence-informed guidance.
- No food should be described as a guaranteed cure.
- Do not recommend extreme diets or unnecessary restriction.
- Food advice can depend on allergies and medical conditions.
- Recommend individualized professional advice when needed.

MEDICINES
- Do not prescribe medicines or individualized doses.
- Do not tell users to start, stop or change medication.
- Explain treatments generally and recommend a qualified
  healthcare professional for personal treatment decisions.

FIRST AID AND EMERGENCIES
- Prioritize emergency care over a long explanation.
- For severe breathing difficulty, unconsciousness,
  severe bleeding, suspected poisoning or other emergencies,
  tell the user to get immediate emergency help.
- In India, call 112 for emergency assistance where available.
- Encourage children to get help from a trusted adult.
- For suspected fractures, serious burns and head injuries,
  recommend prompt professional assessment.
- Never suggest dangerous home remedies.

PRIVACY
- Do not request names, addresses or other unnecessary
  identifying information.
- Remind users not to share private medical information.

STYLE
- Use clear headings and bullet points.
- Explain difficult terms in easy language.
- Be calm, respectful and practical.
- State when professional assessment is necessary.

IMPORTANT
MediAI provides educational information only.
It is not a doctor, cannot reliably diagnose conditions,
and cannot replace professional medical care.
"""

# --------------------------------------------------
# Page styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.25);
        padding: 14px;
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# API connection
# --------------------------------------------------

api_key = st.secrets.get("GEMINI_API_KEY", "")

if api_key:
    client = genai.Client(api_key=api_key)
else:
    client = None

# --------------------------------------------------
# AI helper
# --------------------------------------------------

def ask_ai(question, history=None):
    """Ask Gemini for educational health information."""
    if client is None:
        return (
            "The AI is not connected yet. Add your "
            "GEMINI_API_KEY to .streamlit/secrets.toml "
            "and restart the app."
        )

    conversation = []

    if history:
        for message in history[-8:]:
            role = message.get("role", "")
            content = message.get("content", "")
            if role in ("user", "assistant"):
                label = "User" if role == "user" else "MediAI"
                conversation.append(f"{label}: {content}")

    conversation.append(f"User: {question}")

    full_prompt = (
        SYSTEM_PROMPT
        + "\n\nConversation:\n"
        + "\n\n".join(conversation)
        + "\n\nMediAI:"
    )

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=full_prompt,
        )

        answer = response.text

        if not answer:
            return (
                "I couldn't generate an answer this time. "
                "Please try asking in a different way."
            )

        return answer

    except Exception as error:
        # Show a helpful message without exposing API credentials.
        print("MediAI API error:", str(error))
        return (
            "I couldn't connect to the AI service. "
            "Please check your internet connection, API key, "
            "Gemini model availability and API quota, then "
            "try again. If it continues, check the terminal "
            "for the technical error."
        )


# --------------------------------------------------
# Emergency warning check
# --------------------------------------------------

EMERGENCY_PHRASES = [
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "severe bleeding",
    "unconscious",
    "passed out",
    "poisoning",
    "overdose",
    "severe chest pain",
    "not breathing",
]

def may_be_emergency(text):
    text = text.lower()
    return any(phrase in text for phrase in EMERGENCY_PHRASES)


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🩺 MediAI")
st.subheader("Your friendly AI health-information assistant")

st.write(
    "Explore health topics, learn basic first aid, "
    "and understand general nutrition guidance."
)

st.info(
    "Medical safety notice: MediAI provides educational "
    "information, not a diagnosis or personal treatment plan. "
    "For medical concerns, contact a qualified healthcare "
    "professional. For emergencies, seek immediate help."
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------

with st.sidebar:
    st.title("🩺 MediAI")
    st.caption("Health knowledge, explained simply")

    st.divider()

    st.markdown("### ✨ Features")
    st.write("💬 AI health chat")
    st.write("🔎 Disease and condition explorer")
    st.write("🥗 Food and nutrition guide")
    st.write("🩹 First-aid information")
    st.write("📚 Trusted health references")

    st.divider()

    st.markdown("### 📚 Trusted references")
    st.markdown(
        "[MedlinePlus — Health Topics]"
        "(https://medlineplus.gov/healthtopics.html)"
    )
    st.markdown(
        "[WHO — Fact Sheets]"
        "(https://www.who.int/news-room/fact-sheets)"
    )
    st.markdown(
        "[NHS — Health A to Z]"
        "(https://www.nhs.uk/conditions/)"
    )

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Created by Yash Raj Singh")

# --------------------------------------------------
# Tabs
# --------------------------------------------------

chat_tab, disease_tab, food_tab, first_aid_tab, resources_tab = (
    st.tabs(
        [
            "💬 Ask MediAI",
            "🔎 Disease Explorer",
            "🥗 Food Guide",
            "🩹 First Aid",
            "📚 Resources",
        ]
    )
)

# --------------------------------------------------
# TAB 1 — AI CHAT
# --------------------------------------------------

with chat_tab:
    st.header("Ask MediAI")
    st.write(
        "Ask a general question about health, diseases, "
        "injuries, prevention or medical terms."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not client:
        st.warning(
            "AI connection missing. Check your API key "
            "in .streamlit/secrets.toml."
        )

    # Quick questions
    st.markdown("**Try a question:**")

    quick_col1, quick_col2 = st.columns(2)

    with quick_col1:
        if st.button(
            "What is dengue?",
            use_container_width=True,
        ):
            st.session_state.quick_question = (
                "Explain dengue, its symptoms, prevention "
                "and warning signs."
            )

        if st.button(
            "Explain diabetes",
            use_container_width=True,
        ):
            st.session_state.quick_question = (
                "Explain diabetes in simple language, "
                "including general food guidance."
            )

    with quick_col2:
        if st.button(
            "Ankle injury first aid",
            use_container_width=True,
        ):
            st.session_state.quick_question = (
                "Explain safe first aid for an ankle injury "
                "and signs that need medical assessment."
            )

        if st.button(
            "Healthy eating basics",
            use_container_width=True,
        ):
            st.session_state.quick_question = (
                "Explain balanced eating and hydration "
                "for general health."
            )

    # Show previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Process a quick question or typed question
    typed_question = st.chat_input(
        "Ask a health-information question..."
    )

    question = typed_question

    if not question and "quick_question" in st.session_state:
        question = st.session_state.pop("quick_question")

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        if may_be_emergency(question):
            st.error(
                "⚠️ This may involve an emergency. Get help "
                "from a trusted adult and contact emergency "
                "services immediately. In India, call 112 "
                "where available. Do not wait for a chatbot "
                "response."
            )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("MediAI is preparing an answer..."):
                answer = ask_ai(
                    question,
                    history=st.session_state.messages[:-1],
                )
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

# --------------------------------------------------
# TAB 2 — DISEASE EXPLORER
# --------------------------------------------------

with disease_tab:
    st.header("🔎 Disease and Condition Explorer")
    st.write(
        "Enter a disease, health condition or injury "
        "to learn general information."
    )

    with st.form("disease_form"):
        disease_name = st.text_input(
            "Disease, condition or injury",
            placeholder="Example: asthma, dengue, sprained ankle",
        )

        disease_submit = st.form_submit_button(
            "Explore topic",
            use_container_width=True,
        )

    if disease_submit:
        if not disease_name.strip():
            st.warning("Please enter a topic first.")
        else:
            disease_question = f"""
Explain the following health topic for educational purposes:
{disease_name}

Include, when relevant:
- What it is
- Common causes
- Common symptoms and warning signs
- Prevention
- General food and hydration guidance
- Safe general self-care or first aid
- What to avoid
- When professional or emergency help is needed
- Trusted references for further reading

Do not diagnose anyone or prescribe treatment.
"""
            with st.spinner("Exploring the health topic..."):
                result = ask_ai(disease_question)

            st.markdown("### Results")
            st.markdown(result)

            st.caption(
                "This is AI-generated educational information, "
                "not a confirmed diagnosis or medical record."
            )

# --------------------------------------------------
# TAB 3 — FOOD AND NUTRITION
# --------------------------------------------------

with food_tab:
    st.header("🥗 Food and Nutrition Guide")
    st.write(
        "Learn about general nutrition and food guidance "
        "for a health condition."
    )

    with st.form("food_form"):
        food_topic = st.text_input(
            "Health topic or nutrition question",
            placeholder="Example: iron deficiency, diabetes, hydration",
        )

        food_submit = st.form_submit_button(
            "Get food guidance",
            use_container_width=True,
        )

    if food_submit:
        if not food_topic.strip():
            st.warning("Please enter a topic first.")
        else:
            food_question = f"""
Give balanced, evidence-informed general food guidance
about this topic: {food_topic}

Explain:
- General foods to consider and why
- Foods or drinks to limit only when there is a sound reason
- Hydration guidance when relevant
- Important allergies or dietary cautions
- When an individualized dietitian or clinician is needed

Do not promise cures, prescribe a restrictive diet,
or suggest changing a medically prescribed diet.
Use simple language.
"""
            with st.spinner("Preparing nutrition guidance..."):
                result = ask_ai(food_question)

            st.markdown("### Nutrition information")
            st.markdown(result)

            st.caption(
                "Food guidance varies by person. Food alone "
                "does not replace medical treatment."
            )

# --------------------------------------------------
# TAB 4 — FIRST AID
# --------------------------------------------------

with first_aid_tab:
    st.header("🩹 Basic First-Aid Guide")

    st.error(
        "For a life-threatening emergency, get immediate "
        "emergency assistance. In India, call 112 where "
        "available. Do not delay help to use MediAI."
    )

    st.write(
        "Choose a topic to learn about general first aid. "
        "Serious injuries need professional assessment."
    )

    first_aid_topics = {
        "Minor cuts and scrapes":
            "Give basic first aid for minor cuts and scrapes, "
            "including cleaning, covering and warning signs.",
        "Minor burns":
            "Explain safe immediate first aid for a minor burn, "
            "what not to apply, and when urgent care is needed.",
        "Sprains":
            "Explain general first aid for a possible sprain, "
            "what to avoid and when to seek medical assessment.",
        "Nosebleeds":
            "Explain safe first aid for a nosebleed and "
            "when emergency medical help is needed.",
        "Suspected fracture":
            "Explain safe first aid for a suspected fracture. "
            "Do not suggest trying to straighten the bone. "
            "Explain how to avoid further injury and get help.",
        "Head injury":
            "Explain warning signs after a head injury and "
            "when emergency help is required. Do not diagnose."
    }

    selected_first_aid = st.selectbox(
        "Choose a first-aid topic",
        list(first_aid_topics.keys()),
    )

    if st.button(
        "Show first-aid guidance",
        use_container_width=True,
    ):
        with st.spinner("Preparing first-aid information..."):
            result = ask_ai(
                first_aid_topics[selected_first_aid]
            )

        st.markdown("### General guidance")
        st.markdown(result)

        st.caption(
            "This guide cannot assess the severity of an injury."
        )

# --------------------------------------------------
# TAB 5 — TRUSTED RESOURCES
# --------------------------------------------------

with resources_tab:
    st.header("📚 Trusted Health Resources")

    st.write(
        "Use these established medical information websites "
        "to read more about health conditions."
    )

    st.markdown("### MedlinePlus")
    st.write(
        "Health information from the US National Library "
        "of Medicine."
    )
    st.link_button(
        "Explore health topics",
        "https://medlineplus.gov/healthtopics.html",
        use_container_width=True,
    )

    st.divider()

    st.markdown("### World Health Organization (WHO)")
    st.write(
        "Fact sheets about diseases, public health and prevention."
    )
    st.link_button(
        "Read WHO fact sheets",
        "https://www.who.int/news-room/fact-sheets",
        use_container_width=True,
    )

    st.divider()

    st.markdown("### NHS Health A to Z")
    st.write(
        "Information about common conditions, symptoms "
        "and health concerns."
    )
    st.link_button(
        "Explore NHS health topics",
        "https://www.nhs.uk/conditions/",
        use_container_width=True,
    )

    st.warning(
        "These links open external websites. MediAI does not "
        "automatically retrieve or verify their latest content "
        "inside its AI answers."
    )

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()

st.caption(
    "MediAI 2.0 • Created by Yash Raj Singh • "
    "Educational health information only"
)
