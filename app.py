from __future__ import annotations

import csv
import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import streamlit as st
from google import genai

BASE_DIR = Path(__file__).resolve().parent
FAQ_PATH = BASE_DIR / "clinic_faq.json"
REQUESTS_PATH = BASE_DIR / "data" / "appointment_requests.csv"
MODEL_NAME = "gemini-3.5-flash-lite"

st.set_page_config(
    page_title="ClinicAssist | Clinic Enquiry Assistant",
    page_icon="🏥",
    layout="centered",
)


def load_clinic_data() -> dict[str, Any]:
    """Load the fictional clinic information used to ground chatbot answers."""
    with FAQ_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_api_key() -> str | None:
    """Read the Gemini key from Streamlit secrets or an environment variable."""
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("GEMINI_API_KEY")
    except Exception:
        return None


def classify_question(question: str) -> str:
    """A transparent, keyword-based demo classifier for common enquiry types."""
    text = question.lower()
    categories = {
        "Appointments": ["appointment", "book", "booking", "schedule", "reschedule"],
        "Opening hours": ["timing", "time", "open", "close", "hours", "sunday"],
        "Fees": ["fee", "fees", "cost", "price", "charge", "payment"],
        "Services": ["service", "services", "check-up", "checkup", "vaccination"],
        "Location": ["where", "location", "address", "reach", "directions"],
        "Contact": ["contact", "phone", "email", "call"],
    }
    for category, keywords in categories.items():
        if any(keyword in text for keyword in keywords):
            return category
    return "General enquiry"


def build_prompt(
    clinic_data: dict[str, Any],
    previous_messages: list[dict[str, str]],
    question: str,
) -> str:
    """Build a prompt that limits answers to the supplied fictional clinic data."""
    clinic_context = json.dumps(clinic_data, ensure_ascii=False, indent=2)
    history_lines = []
    for message in previous_messages[-8:]:
        role = "Visitor" if message["role"] == "user" else "ClinicAssist"
        history_lines.append(f"{role}: {message['content']}")
    history = "\n".join(history_lines) if history_lines else "No previous messages."

    return f"""You are ClinicAssist, a friendly administrative enquiry assistant for a fictional demonstration clinic.

STRICT RULES:
1. Answer clinic questions using ONLY the clinic information provided below.
2. Never invent or guess clinic hours, fees, services, addresses, contact details, or appointment availability.
3. If the answer is not in the information, say that you do not have that information and suggest contacting the clinic directly.
4. You are not a doctor. Do not diagnose, interpret symptoms, recommend medicines, or suggest treatments.
5. If a visitor asks for medical advice, explain politely that this assistant handles administrative questions only and they should speak with a qualified healthcare professional.
6. If someone describes an immediate emergency, tell them to contact local emergency services or go to the nearest emergency department.
7. Do not say an appointment is confirmed. The form only records a demo request.
8. Keep replies warm, clear, concise, and professional.

FICTIONAL CLINIC INFORMATION:
{clinic_context}

CONVERSATION SO FAR:
{history}

NEW VISITOR QUESTION:
{question}

Write the best safe and accurate reply:"""


def ask_gemini(
    question: str,
    previous_messages: list[dict[str, str]],
    clinic_data: dict[str, Any],
    api_key: str,
) -> str:
    client = genai.Client(api_key=api_key)
    prompt = build_prompt(clinic_data, previous_messages, question)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )
    answer = getattr(response, "text", None)
    if not answer:
        raise RuntimeError("The AI service returned an empty response. Please try again.")
    return answer.strip()


def save_appointment_request(
    name: str,
    email: str,
    service: str,
    preferred_date: date,
    preferred_time: str,
) -> None:
    REQUESTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = REQUESTS_PATH.exists()
    fieldnames = [
        "submitted_at",
        "name",
        "email",
        "service",
        "preferred_date",
        "preferred_time",
    ]
    with REQUESTS_PATH.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "submitted_at": datetime.now().isoformat(timespec="seconds"),
                "name": name.strip(),
                "email": email.strip(),
                "service": service,
                "preferred_date": preferred_date.isoformat(),
                "preferred_time": preferred_time,
            }
        )


try:
    clinic_data = load_clinic_data()
except (OSError, json.JSONDecodeError) as exc:
    st.error(f"Could not load clinic_faq.json: {exc}")
    st.stop()

st.title("🏥 ClinicAssist")
st.subheader("Your clinic enquiry assistant")
st.caption("A student-built AI demo for answering general clinic and appointment enquiries.")
st.warning(
    "DEMO ONLY: This is a fictional clinic. Do not enter real patient information. "
    "ClinicAssist does not provide medical advice or confirm appointments."
)

with st.sidebar:
    st.header("About this demo")
    st.write(clinic_data.get("clinic_name", "Fictional Clinic"))
    st.write(clinic_data.get("short_description", "A sample clinic for an AI project demo."))
    st.divider()
    st.markdown("**What ClinicAssist can help with**")
    st.write("• Opening hours and location")
    st.write("• Services and consultation fees")
    st.write("• General appointment enquiries")
    st.divider()
    st.caption("AI model: Google Gemini. Enquiry category is identified using simple keyword rules.")

chat_tab, appointment_tab, faq_tab = st.tabs(
    ["💬 Ask ClinicAssist", "📅 Appointment request", "ℹ️ Clinic information"]
)

with chat_tab:
    st.markdown("Ask a question about the demo clinic. Try one of the suggested questions below.")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    examples = [
        "What are your opening hours?",
        "How much is a consultation?",
        "What services do you provide?",
        "How can I request an appointment?",
    ]
    cols = st.columns(2)
    for index, example in enumerate(examples):
        with cols[index % 2]:
            if st.button(example, key=f"example_{index}", use_container_width=True):
                st.session_state.pending_question = example

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input("Type your clinic-related question...")
    if not user_question and st.session_state.get("pending_question"):
        user_question = st.session_state.pop("pending_question")

    if user_question:
        with st.chat_message("user"):
            st.markdown(user_question)

        previous_messages = list(st.session_state.messages)
        st.session_state.messages.append({"role": "user", "content": user_question})
        category = classify_question(user_question)
        st.caption(f"Detected enquiry category: **{category}**")

        with st.chat_message("assistant"):
            api_key = get_api_key()
            if not api_key:
                answer = (
                    "The AI assistant is not connected yet. Add your Gemini API key "
                    "to `.streamlit/secrets.toml` and restart the app."
                )
                st.info(answer)
            else:
                try:
                    with st.spinner("ClinicAssist is preparing a reply..."):
                        answer = ask_gemini(
                            user_question,
                            previous_messages,
                            clinic_data,
                            api_key,
                        )
                    st.markdown(answer)
                except Exception as exc:  # Show a useful message without exposing credentials.
                    answer = (
                        "Sorry, I could not connect to the AI service just now. "
                        "Please check the API key and internet connection, then try again."
                    )
                    st.error(answer)
                    st.caption(f"Technical detail: {type(exc).__name__}: {exc}")

        st.session_state.messages.append({"role": "assistant", "content": answer})

    if st.session_state.messages and st.button("Clear chat", type="secondary"):
        st.session_state.messages = []
        st.rerun()

with appointment_tab:
    st.markdown("### Send a demo appointment request")
    st.write("This form saves a sample request to a local CSV file. It does not contact a real clinic.")
    with st.form("appointment_request_form"):
        name = st.text_input("Demo name")
        email = st.text_input("Demo email address")
        services = clinic_data.get("services", [])
        service_options = [item["name"] for item in services] or ["General consultation"]
        selected_service = st.selectbox("Service", service_options)
        preferred_date = st.date_input("Preferred date", min_value=date.today())
        preferred_time = st.selectbox(
            "Preferred time",
            ["Morning (9 AM–12 PM)", "Afternoon (12 PM–3 PM)", "Evening (3 PM–6 PM)"],
        )
        submitted = st.form_submit_button("Save demo request")

    if submitted:
        if not name.strip() or not email.strip():
            st.error("Please enter a demo name and email address.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter a valid-looking demo email address.")
        else:
            try:
                save_appointment_request(
                    name,
                    email,
                    selected_service,
                    preferred_date,
                    preferred_time,
                )
                st.success(
                    "Demo request saved successfully. This is not a confirmed appointment."
                )
            except OSError:
                st.error("The demo request could not be saved. Please try again.")

with faq_tab:
    st.markdown("### Clinic information (fictional sample data)")
    st.write(clinic_data.get("short_description", ""))
    st.markdown(f"**Opening hours:** {clinic_data.get('opening_hours', 'Not provided')}")
    st.markdown(f"**Location:** {clinic_data.get('location', 'Not provided')}")
    st.markdown(f"**Contact:** {clinic_data.get('contact', 'Not provided')}")
    st.markdown("### Services")
    for service in clinic_data.get("services", []):
        st.markdown(f"**{service['name']}** — {service['description']}")
    st.markdown("### Frequently asked questions")
    for item in clinic_data.get("faqs", []):
        with st.expander(item["question"]):
            st.write(item["answer"])

st.divider()
st.caption("ClinicAssist is an educational prototype, not a production healthcare service.")
