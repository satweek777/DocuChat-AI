import os
import io
import time
import streamlit as st
from pypdf import PdfReader
from google import genai

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="DocuChat AI",
    page_icon="📄",
    layout="wide"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------

st.markdown("""
<style>
    .main {
        background-color: #f7f8fc;
    }

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .chat-user {
        background: #e8f0fe;
        padding: 14px 18px;
        border-radius: 15px;
        margin: 10px 0;
    }

    .chat-ai {
        background: white;
        padding: 18px;
        border-radius: 15px;
        border: 1px solid #e5e5e5;
        margin: 10px 0 20px 0;
    }

    .source {
        background: #f1f3f4;
        padding: 10px;
        border-radius: 10px;
        font-size: 13px;
        color: #555;
    }

    .stButton button {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# API KEY
# ---------------------------------------------------------

api_key = st.sidebar.text_input(
    "🔑 Gemini API Key",
    type="password",
    help="Enter your Gemini API key"
)

if not api_key:
    st.markdown('<div class="title">📄 DocuChat AI</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Upload a PDF and ask questions about it</div>',
        unsafe_allow_html=True
    )

    st.info(
        "👈 Enter your Gemini API key in the sidebar to start."
    )

    st.stop()

# Create Gemini client
client = genai.Client(api_key=api_key)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""

if "page_texts" not in st.session_state:
    st.session_state.page_texts = []

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="title">📄 DocuChat AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Your intelligent PDF Question-Answer Assistant</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:

    st.header("📚 PDF Manager")

    uploaded_file = st.file_uploader(
        "Upload your PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:

        # Process only when a new PDF is uploaded
        if uploaded_file.name != st.session_state.pdf_name:

            try:
                pdf_bytes = uploaded_file.read()

                document = PdfReader(io.BytesIO(pdf_bytes))

                all_text = []
                page_texts = []

                for page_number, page in enumerate(document.pages):

                    text = page.extract_text() or ""

                    page_texts.append({
                        "page": page_number + 1,
                        "text": text
                    })

                    all_text.append(
                        f"\n--- PAGE {page_number + 1} ---\n{text}"
                    )

                st.session_state.pdf_text = "\n".join(all_text)
                st.session_state.page_texts = page_texts
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.messages = []

                st.success(
                    f"✅ {uploaded_file.name} loaded!"
                )

            except Exception as e:
                st.error(f"Error reading PDF: {e}")

    if st.session_state.pdf_name:

        st.divider()

        st.write("📄 **Current PDF**")
        st.write(st.session_state.pdf_name)

        total_pages = len(st.session_state.page_texts)

        st.write(f"📑 Pages: **{total_pages}**")

        if st.button("🗑️ Clear PDF", use_container_width=True):

            st.session_state.pdf_text = ""
            st.session_state.pdf_name = ""
            st.session_state.page_texts = []
            st.session_state.messages = []

            st.rerun()

    st.divider()

    st.header("⚙️ Options")

    model_name = st.selectbox(
        "AI Model",
        [
            "gemini-2.5-flash",
            "gemini-2.5-pro"
        ]
    )

    st.caption(
        "The chatbot answers questions using the uploaded PDF."
    )

# ---------------------------------------------------------
# PDF CHECK
# ---------------------------------------------------------

if not st.session_state.pdf_text:

    st.markdown("""
    <div style="
        text-align:center;
        padding:80px 20px;
        background:white;
        border-radius:20px;
        border:1px solid #eee;
    ">
        <h1>📄 Upload a PDF</h1>
        <p style="font-size:18px;color:#666;">
            Upload your document from the sidebar and start asking questions.
        </p>

        <p>
            Examples:
        </p>

        <p>
            💬 "What is this document about?"<br>
            💬 "Summarize chapter 2"<br>
            💬 "What are the main points?"<br>
            💬 "Explain this topic in simple words"
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# PDF INFORMATION
# ---------------------------------------------------------

st.success(
    f"📄 Currently chatting with: **{st.session_state.pdf_name}**"
)

# ---------------------------------------------------------
# QUICK QUESTIONS
# ---------------------------------------------------------

st.subheader("💡 Quick Questions")

col1, col2, col3, col4 = st.columns(4)

quick_question = None

with col1:
    if st.button("📖 Summarize PDF", use_container_width=True):
        quick_question = "Give me a clear summary of this PDF."

with col2:
    if st.button("🎯 Main Points", use_container_width=True):
        quick_question = "What are the most important points in this PDF?"

with col3:
    if st.button("📚 Topics", use_container_width=True):
        quick_question = "List the major topics covered in this PDF."

with col4:
    if st.button("🧠 Simple Explanation", use_container_width=True):
        quick_question = "Explain the main content of this PDF in very simple language."

# ---------------------------------------------------------
# CHAT HISTORY
# ---------------------------------------------------------

for message in st.session_state.messages:

    if message["role"] == "user":

        st.markdown(
            f"""
            <div class="chat-user">
                <b>👤 You</b><br><br>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            f"""
            <div class="chat-ai">
                <b>🤖 DocuChat AI</b><br><br>
                {message["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------------------------------------------------
# USER INPUT
# ---------------------------------------------------------

user_question = st.chat_input(
    "Ask a question about your PDF..."
)

# Use quick question if clicked
if quick_question:
    user_question = quick_question

# ---------------------------------------------------------
# ASK AI
# ---------------------------------------------------------

if user_question:

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    # Display user message immediately
    st.markdown(
        f"""
        <div class="chat-user">
            <b>👤 You</b><br><br>
            {user_question}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # CREATE PROMPT
    # -----------------------------------------------------

    prompt = f"""
You are DocuChat AI, a helpful PDF question-answer assistant.

Your job is to answer the user's question using the uploaded PDF.

IMPORTANT RULES:

1. Use the PDF content as your primary source.
2. Do not invent information.
3. If the answer cannot be found in the PDF, clearly say:
   "I couldn't find this information in the uploaded PDF."
4. Explain difficult concepts in simple language when appropriate.
5. For summaries, organize the answer with headings and bullet points.
6. If possible, mention the relevant page number.
7. Do not claim information is in the PDF if it is not there.

---------------------------------------------------------
UPLOADED PDF
---------------------------------------------------------

PDF NAME:
{st.session_state.pdf_name}

PDF CONTENT:
{st.session_state.pdf_text}

---------------------------------------------------------
USER QUESTION
---------------------------------------------------------

{user_question}

---------------------------------------------------------

Answer the user's question now.
"""

    # -----------------------------------------------------
    # GENERATE RESPONSE
    # -----------------------------------------------------

    with st.spinner("🤖 Reading the PDF and generating answer..."):

        answer = None
        last_error = None
        models_to_try = [model_name]

        if model_name != "gemini-2.5-flash":
            models_to_try.append("gemini-2.5-flash")

        for model_to_try in models_to_try:
            for attempt in range(2):
                try:
                    response = client.models.generate_content(
                        model=model_to_try,
                        contents=prompt
                    )

                    answer = response.text
                    break

                except Exception as error:
                    last_error = error
                    error_text = str(error)
                    is_unavailable = "503" in error_text or "UNAVAILABLE" in error_text

                    if not is_unavailable:
                        break

                    if attempt == 0:
                        time.sleep(2)

            if answer is not None:
                break

        if answer is None:
            answer = f"❌ Gemini is temporarily unavailable. Please try again in a moment. Details: {last_error}"

    # -----------------------------------------------------
    # SAVE RESPONSE
    # -----------------------------------------------------

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    # -----------------------------------------------------
    # DISPLAY RESPONSE
    # -----------------------------------------------------

    st.markdown(
        f"""
        <div class="chat-ai">
            <b>🤖 DocuChat AI</b><br><br>
            {answer}
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#888;">
        📄 DocuChat AI • PDF Question-Answer Assistant
    </div>
    """,
    unsafe_allow_html=True
)
