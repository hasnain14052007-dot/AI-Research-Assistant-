# 🔎 AI Research Agent

A beginner-friendly single-agent AI research tool. You give it a topic,
it searches the web for free using DuckDuckGo, and writes a structured
Markdown report — powered by [CrewAI](https://docs.crewai.com), the
`openai/gpt-oss-120b` model on [Groq](https://groq.com) (free & fast),
and a [Streamlit](https://streamlit.io) UI.

This project is set up to be uploaded straight to GitHub and deployed
on **Streamlit Community Cloud** — no local setup required. The app
reads your Groq API key from **Streamlit Secrets**.

## How it works

- **`research_agent.py`** — the CrewAI "brain": one `Agent` (a Researcher)
  with one `Task` (write a report), using a custom DuckDuckGo search tool
  and Groq as the LLM.
- **`app.py`** — the Streamlit web UI: a text box, a button, and a place
  to show/download the report.

## Project structure

```
ai-research-agent/
├── app.py                       # Streamlit UI
├── research_agent.py            # CrewAI agent, task, tool, crew
├── requirements.txt             # Python dependencies
├── .gitignore                   # Keeps secrets out of GitHub
├── .streamlit/
│   └── secrets.toml.example     # Reference only — not used on Cloud
└── README.md
```

## Step 1 — Get a free Groq API key

1. Go to https://console.groq.com/keys
2. Sign up (it's free) and click **Create API Key**.
3. Copy the key — you'll paste it into Streamlit in Step 3.

## Step 2 — Upload this project to GitHub

1. Create a new repository on GitHub (public or private both work).
2. Upload all the files in this project to that repository — either by
   dragging them into the GitHub web UI ("Add file" → "Upload files"),
   or with git:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI research agent"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

`.streamlit/secrets.toml.example` is just a template for reference — it
has no real key in it, so it's safe to upload. **Never** create and
upload a real `.streamlit/secrets.toml` file; it's already excluded by
`.gitignore` in case you create one locally.

## Step 3 — Deploy on Streamlit Cloud

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **Create app** → **From an existing repo**.
3. Pick your repository, branch (`main`), and set the main file path
   to `app.py`.
4. Before clicking Deploy, open **Advanced settings → Secrets** (or,
   after deploying, go to your app's **Settings → Secrets**) and paste:
   ```toml
   GROQ_API_KEY = "your_real_groq_api_key"
   ```
5. Click **Save**, then **Deploy** (or **Reboot app** if it's already
   deployed). Streamlit Cloud installs everything from
   `requirements.txt` automatically.

Your app will be live at a URL like
`https://<your-app-name>.streamlit.app`.

## Step 4 — Use it

Open the app URL, type a topic, click **Generate Report**, and wait
~30-60 seconds. You can download the finished report as a `.md` file.

## Customizing

- **Change the model:** edit the `model="openai/gpt-oss-120b"` line in
  `research_agent.py`. Any model ID from your Groq console works —
  just keep `custom_openai=True` and the Groq `base_url`.
- **Change report length/style:** edit the `description` and
  `expected_output` text inside the `Task(...)` in `research_agent.py`.
- **Add a second agent** (e.g. an "Editor" that polishes the report):
  create another `Agent`, a second `Task` that depends on the first
  (`context=[report_task]`), and add both to the `Crew`'s `tasks` list.

## Troubleshooting

| Problem | Likely fix |
|---|---|
| `No Groq API key found in Streamlit secrets` | Go to your app's **Settings → Secrets** on Streamlit Cloud and confirm `GROQ_API_KEY = "..."` is saved, then reboot the app. |
| App is slow | Normal — the agent may run several searches before writing. Free Groq tiers also have rate limits. |
| Deploy fails on `requirements.txt` | Check the "Manage app" logs on Streamlit Cloud for the exact package error, and confirm the repo has all files at the root (not nested in a subfolder), unless you set that as the app's root. |
| Search returns no results | DuckDuckGo occasionally rate-limits free requests; wait a moment and try again. |

## Tech stack

- [CrewAI](https://docs.crewai.com) — agent orchestration
- [Groq](https://groq.com) — free, fast LLM inference (`openai/gpt-oss-120b`)
- [ddgs](https://pypi.org/project/ddgs/) — free DuckDuckGo search (no API key needed)
- [Streamlit](https://streamlit.io) — web UI
