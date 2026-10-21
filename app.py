
import streamlit as st
from google import genai
from google.genai import types

# =========================================================
# MediAI 3.0 | Created by Yash Raj Singh
# Educational health information, not medical diagnosis.
# =========================================================

st.set_page_config(
    page_title="MediAI | Health Intelligence",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "gemini-3.8-flash"
MAX_QUESTION_LENGTH = 3000

SYSTEM_PROMPT = """
You are MediAI 3.0, a careful, friendly educational
health-information assistant created by Yash Raj Singh.

PURPOSE
Explain a broad range of diseases, health conditions,
symptoms, sports injuries, prevention, nutrition,
medical terminology and basic first aid.

ANSWER FORMAT
When relevant, explain:
1. What the condition is
2. Common causes and risk factors
3. Common symptoms
4. Warning signs
5. General food and hydration guidance
6. Safe self-care or first aid
7. What to avoid
8. When to seek medical care
9. Prevention
10. Trustworthy references for further reading

ACCURACY
- Never pretend to diagnose a person.
- Similar symptoms can have different causes.
- Never invent medical facts, statistics, citations or cures.
- Be honest about uncertainty and knowledge limitations.
- Do not claim to have checked a live medical database
  or website unless a real search was performed.
- Do not claim that every disease is covered.
- Explain technical terms in simple language.

NUTRITION
- Offer balanced, practical, evidence-informed guidance.
- Never claim that food alone cures a disease.
- Do not recommend extreme diets or unnecessary restriction.
- Mention that allergies and individual conditions matter.
- Recommend professional dietary advice when appropriate.

MEDICINES
- Do not prescribe medicines or individualized doses.
- Do not tell users to start, stop or change medication.
- Explain treatments only in general educational terms.

FIRST AID
- Prioritize emergency services over a long explanation.
- For severe bleeding, breathing difficulty, unconsciousness,
  poisoning or other possible emergencies, tell the user
  to get immediate emergency assistance.
- In India, call 112 for emergency assistance where available.
- Encourage children to get help from a trusted adult.
- Suspected fractures, serious burns and head injuries
  require appropriate professional assessment.
- Never recommend dangerous home remedies.

PRIVACY
- Do not ask for names, addresses or unnecessary personal data.
- Remind users not to share private medical information.

LANGUAGE
- Follow the user's selected language.
- Use clear English, Hindi or natural Hinglish as requested.
- Use headings and bullet points where helpful.

IMPORTANT
MediAI provides educational information only. It is not a
doctor, cannot reliably diagnose conditions and cannot
replace professional medical care.
"""

# ----------------------- STYLING --------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    .hero {
        padding: 1.4rem;
        border: 1px solid rgba(128,128,128,0.3);
        border-radius: 18px;
        margin-bottom: 1rem;
    }
    .small-note {
        font-size: 0.88rem;
        opacity: 0.8;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------- API CONFIGURATION -------------------

api_key = st.secrets.get("GEMINI_API_KEY", "")

@st.cache_resource
def get_client(key):
    return genai.Client(api_key=key)

client = get_client(api_key) if api_key else None

# ----------------------- HELPERS -------------------------

LANGUAGES = {
    "English": "English",
    "Hindi (हिन्दी)": "Hindi",
    "Hinglish": "natural Hinglish using Roman script",
}

EMERGENCY_PHRASES = [
    "can't breathe",
    "cannot breathe",
    "difficulty breathing",
    "severe bleeding",
    "unconscious",
    "passed out",
    "not breathing",
    "severe chest pain",
    "poisoning",
    "overdose",
    "suicidal",
    "want to kill myself",
]

def may_be_emergency(text):
    lowered = text.lower()
    return any(term in lowered for term in EMERGENCY_PHRASES)


def ask_ai(question, history=None, language="English"):
    if not client:
        return (
            "The AI service is not configured yet. Add "
            "GEMINI_API_KEY in Streamlit Cloud Secrets "
            "and restart the app."
        )

    instruction = (
        SYSTEM_PROMPT
        + "\n\nRespond in "
        + LANGUAGES.get(language, "English")
        + "."
    )

    conversation = []

    for message in (history or [])[-10:]:
        role = message.get("role")
        content = message.get("content", "")
        if role in ("user", "assistant") and content:
            conversation.append({
                "role": "user" if role == "user" else "model",
                "parts": [{"text": content[:MAX_QUESTION_LENGTH]}],
            })

    conversation.append({
        "role": "user",
        "parts": [{"text": question[:MAX_QUESTION_LENGTH]}],
    })

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=conversation,
            config=types.GenerateContentConfig(
                system_instruction=instruction,
            ),
        )

        answer = response.text

        if not answer:
            return (
                "I couldn't generate an answer this time. "
                "Please try again with a clearer question."
            )

        return answer

    except Exception:
        # Never display API credentials or internal errors.
        return (
            "Sorry, I couldn't reach the AI service. Please "
            "check your internet connection, API key, model "
            "availability and API quota. If the problem "
            "continues, check the Streamlit app logs."
        )


def show_emergency_notice():
    st.error(
        "⚠️ Possible emergency: do not wait for a chatbot. "
        "Contact local emergency services immediately. "
        "In India, call 112 where available. Get help from "
        "a trusted adult if you are a child."
    )


def run_topic(question, language):
    with st.spinner("MediAI is preparing your information..."):
        result = ask_ai(question, language=language)
    st.markdown(result)


# ------------------- SESSION STATE -----------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "topic_result" not in st.session_state:
    st.session_state.topic_result = None

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ----------------------- SIDEBAR -------------------------

with st.sidebar:
    st.title("🩺 MediAI")
    st.caption("Understand health. Make informed choices.")

    language = st.selectbox(
        "Answer language",
        list(LANGUAGES.keys()),
        index=0,
    )

    st.divider()

    st.markdown("### Your health tools")
    st.markdown(
        "- 💬 AI health chat\n"
        "- 🔎 Disease explorer\n"
        "- 🥗 Nutrition guide\n"
        "- 🩹 First-aid guide\n"
        "- 📚 Trusted resources"
    )

    st.divider()

    st.markdown("### Trusted references")
    st.markdown(
        "[MedlinePlus](https://medlineplus.gov/healthtopics.html)"
    )
    st.markdown(
        "[World Health Organization]"
        "(https://www.who.int/news-room/fact-sheets)"
    )
    st.markdown(
        "[NHS Health A to Z](https://www.nhs.uk/conditions/)"
    )

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.caption("Created by Yash Raj Singh")

# ------------------------ HEADER -------------------------

st.markdown(
    """
    <div class="hero">
        <h1>🩺 MediAI 3.0</h1>
        <p>
            Your AI-powered educational health companion.
            Explore conditions, understand symptoms and learn
            general prevention and first-aid information.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "MediAI is not a doctor. It cannot confirm a diagnosis "
    "or replace professional care. For emergencies, contact "
    "emergency services instead of waiting for an AI response."
)

if not client:
    st.error(
        "AI connection unavailable. Check that "
        "GEMINI_API_KEY is configured in Streamlit Secrets."
    )

# ------------------------- TABS --------------------------

chat_tab, disease_tab, food_tab, aid_tab, learn_tab = st.tabs(
    [
        "💬 Ask MediAI",
        "🔎 Disease Explorer",
        "🥗 Food Guide",
        "🩹 First Aid",
        "📚 Learn",
    ]
)

# =========================================================
# 1. AI CHAT
# =========================================================

with chat_tab:
    st.subheader("Ask your health question")
    st.caption(
        "Avoid sharing names, addresses, phone numbers or "
        "other private medical information."
    )

    st.markdown("**Quick questions**")

    quick_questions = [
        "Explain dengue and its warning signs",
        "What is asthma?",
        "How can I stay hydrated during sports?",
        "What should I know about a sprained ankle?",
    ]

    cols = st.columns(2)

    for index, question in enumerate(quick_questions):
        with cols[index % 2]:
            if st.button(
                question,
                key=f"quick_{index}",
                use_container_width=True,
            ):
                st.session_state.pending_question = question

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    typed_question = st.chat_input(
        "Ask about a condition, injury or health topic...",
        max_chars=MAX_QUESTION_LENGTH,
    )

    question = typed_question

    if not question and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None

    if question:
        if may_be_emergency(question):
            show_emergency_notice()

        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_ai(
                    question,
                    history=st.session_state.messages[:-1],
                    language=language,
                )
            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

# =========================================================
# 2. DISEASE EXPLORER
# =========================================================

with disease_tab:
    st.subheader("Explore a disease or condition")
    st.write(
        "Learn about common conditions, chronic diseases, "
        "infectious illnesses, rare conditions and injuries."
    )

    with st.form("disease_search"):
        condition = st.text_input(
            "Topic",
            placeholder="Example: migraine, dengue, asthma",
            max_chars=150,
        )

        explore = st.form_submit_button(
            "Explore topic",
            use_container_width=True,
        )

    if explore:
        if not condition.strip():
            st.warning("Enter a topic first.")
        else:
            if may_be_emergency(condition):
                show_emergency_notice()

            prompt = f"""
Explain this health topic for general education: {condition}

Include relevant sections on what it is, causes, common
symptoms, warning signs, prevention, general self-care,
food guidance, what to avoid and when to seek professional
or emergency care. Never diagnose a person or prescribe
medication. State any uncertainty honestly.
"""
            run_topic(prompt, language)

# =========================================================
# 3. FOOD GUIDE
# =========================================================

with food_tab:
    st.subheader("Food and nutrition guide")
    st.write(
        "Learn about balanced nutrition and general dietary "
        "considerations for a health topic."
    )

    with st.form("nutrition_search"):
        nutrition_topic = st.text_input(
            "Condition or nutrition question",
            placeholder="Example: iron-rich foods, diabetes",
            max_chars=150,
        )

        nutrition_submit = st.form_submit_button(
            "Get nutrition information",
            use_container_width=True,
        )

    if nutrition_submit:
        if not nutrition_topic.strip():
            st.warning("Enter a topic first.")
        else:
            prompt = f"""
Provide general, evidence-informed nutrition education
about: {nutrition_topic}

Explain balanced food choices, hydration where relevant,
foods to limit only when medically justified, and important
cautions. Do not promise cures, recommend extreme diets,
or advise stopping prescribed treatment or diets.
Explain when individual professional advice is needed.
"""
            run_topic(prompt, language)

# =========================================================
# 4. FIRST AID
# =========================================================

with aid_tab:
    st.subheader("Basic first-aid information")

    st.error(
        "Serious injuries and life-threatening symptoms need "
        "immediate professional help. Do not delay emergency "
        "care to use this guide."
    )

    aid_topics = {
        "Minor cuts and scrapes":
            "Explain basic first aid for minor cuts and scrapes, "
            "including cleaning, covering and warning signs.",
        "Minor burns":
            "Explain safe first aid for minor burns, what not "
            "to apply and when professional care is needed.",
        "Nosebleeds":
            "Explain safe first aid for a nosebleed and when "
            "urgent medical attention is necessary.",
        "Sprains":
            "Explain general first aid for a possible sprain, "
            "what to avoid and when to get assessed.",
        "Suspected fracture":
            "Explain safe first aid for a suspected fracture. "
            "Do not try to straighten the injured part. Explain "
            "how to avoid further injury and get medical help.",
        "Head injury":
            "Explain warning signs after a head injury and when "
            "urgent assessment is required. Do not diagnose.",
        "Heat exhaustion":
            "Explain safe first aid for possible heat exhaustion, "
            "warning signs and when emergency care is required."
    }

    selected_aid = st.selectbox(
        "Choose a topic",
        list(aid_topics.keys()),
    )

    if st.button("Show first-aid guide", use_container_width=True):
        if selected_aid == "Head injury":
            st.warning(
                "Serious head injuries require urgent assessment. "
                "Call emergency services for severe symptoms."
            )

        run_topic(aid_topics[selected_aid], language)

# =========================================================
# 5. LEARN AND TRUSTED REFERENCES
# =========================================================

with learn_tab:
    st.subheader("Learn from trusted health sources")

    st.markdown("### MedlinePlus")
    st.write(
        "A health-information resource from the US National "
        "Library of Medicine."
    )
    st.link_button(
        "Explore health topics",
        "https://medlineplus.gov/healthtopics.html",
        use_container_width=True,
    )

    st.divider()

    st.markdown("### World Health Organization")
    st.write(
        "Read fact sheets about diseases, prevention and "
        "public health."
    )
    st.link_button(
        "Read WHO fact sheets",
        "https://www.who.int/news-room/fact-sheets",
        use_container_width=True,
    )

    st.divider()

    st.markdown("### NHS Health A to Z")
    st.write(
        "Find general information about conditions and symptoms."
    )
    st.link_button(
        "Explore NHS health topics",
        "https://www.nhs.uk/conditions/",
        use_container_width=True,
    )

    st.info(
        "These are external reference links. This app does not "
        "automatically retrieve or verify their latest content "
        "when generating an AI response."
    )

# ------------------------- FOOTER ------------------------

st.divider()

st.caption(
    "MediAI 3.0 | Created by Yash Raj Singh | "
    "Educational information only — not a medical diagnosis."
)

