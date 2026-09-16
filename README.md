# DocuChat AI

A Streamlit app that lets you upload a PDF and ask Gemini questions about its contents.

## Run locally

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Enter your Gemini API key in the app sidebar.

## Deploy with Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open [share.streamlit.io](https://share.streamlit.io/) and select the repository.
3. Set the main file to `app.py`.
4. Add the secret `GEMINI_API_KEY` if you later configure the app to read it from Streamlit secrets.

The current app accepts the API key through the sidebar and does not store it in the repository.
