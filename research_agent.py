"""
research_agent.py
------------------
This file defines everything CrewAI needs:
  1. A free web search tool (DuckDuckGo, via the `ddgs` package)
  2. A single Agent (the "Researcher")
  3. A single Task (write a report on the given topic)
  4. A Crew that runs that agent + task together

`app.py` (the Streamlit UI) only ever calls the `run_research(topic)`
function at the bottom of this file — it doesn't need to know how
CrewAI works internally.
"""

import os
from ddgs import DDGS
from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool


# ---------------------------------------------------------------------
# 1. THE SEARCH TOOL
# ---------------------------------------------------------------------
# CrewAI tools are just normal Python functions with a @tool decorator.
# The docstring becomes the description the agent reads to decide
# when/how to use the tool, so keep it clear.
@tool("DuckDuckGo Search")
def duckduckgo_search(query: str) -> str:
    """
    Search the web using DuckDuckGo and return the top results.
    Use this whenever you need up-to-date facts, statistics, news,
    or sources for the research topic. Input should be a short,
    focused search query (a few words), not a full sentence.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=6))
    except Exception as exc:  # network hiccups, rate limits, etc.
        return f"Search failed for '{query}': {exc}"

    if not results:
        return f"No results found for '{query}'."

    # Format results into plain text the LLM can read easily.
    formatted = []
    for i, r in enumerate(results, start=1):
        title = r.get("title", "No title")
        link = r.get("href", "")
        snippet = r.get("body", "")
        formatted.append(f"{i}. {title}\n   {snippet}\n   Source: {link}")

    return "\n\n".join(formatted)


# ---------------------------------------------------------------------
# 2. THE LLM (Groq, via an OpenAI-compatible endpoint)
# ---------------------------------------------------------------------
def get_llm(api_key: str) -> LLM:
    """
    Groq exposes an OpenAI-compatible API, so we connect to it with
    CrewAI's native OpenAI client (custom_openai=True) instead of the
    older LiteLLM `groq/...` routing. This keeps the dependency list
    small and avoids LiteLLM version issues.

    IMPORTANT: when custom_openai=True, CrewAI automatically strips a
    *leading* "openai/" from the model string (it treats that prefix as
    a routing hint, not part of the real model ID). Groq's actual model
    ID for this model is literally "openai/gpt-oss-120b" (Groq kept
    OpenAI's own naming), so if we passed "openai/gpt-oss-120b" here,
    CrewAI would strip it down to just "gpt-oss-120b" and Groq would
    reject it with a 404 model_not_found error.
    Doubling the prefix ("openai/openai/gpt-oss-120b") means CrewAI's
    single strip leaves exactly "openai/gpt-oss-120b" — the correct ID.
    """
    return LLM(
        model="openai/openai/gpt-oss-120b",  # see note above — do not "simplify" this
        custom_openai=True,
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
        temperature=0.4,
    )


# ---------------------------------------------------------------------
# 3. AGENT + TASK + CREW
# ---------------------------------------------------------------------
def build_crew(topic: str, api_key: str) -> Crew:
    llm = get_llm(api_key)

    researcher = Agent(
        role="Senior Research Analyst",
        goal=(
            f"Research the topic '{topic}' thoroughly using web search, "
            "and produce a clear, well-organized, factual report."
        ),
        backstory=(
            "You are an experienced research analyst known for turning "
            "raw search results into clear, well-structured, easy-to-read "
            "reports. You always search for information before writing "
            "instead of relying on memory, and you mention where key facts "
            "came from."
        ),
        tools=[duckduckgo_search],
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    report_task = Task(
        description=(
            f"Research the topic: '{topic}'.\n\n"
            "Steps:\n"
            "1. Use the DuckDuckGo Search tool at least 2-3 times with "
            "different focused queries to gather up-to-date information.\n"
            "2. Identify the most important facts, figures, and context.\n"
            "3. Write a well-organized report in Markdown.\n\n"
            "The report must include:\n"
            "- A short introduction to the topic\n"
            "- 3-5 sections with headings covering the key aspects\n"
            "- A short conclusion / summary\n"
            "- A 'Sources' section listing the links you used\n"
        ),
        expected_output=(
            "A complete, well-formatted Markdown report (roughly "
            "400-700 words) on the topic, with headings, a conclusion, "
            "and a sources list."
        ),
        agent=researcher,
    )

    return Crew(
        agents=[researcher],
        tasks=[report_task],
        process=Process.sequential,
        verbose=True,
    )


# ---------------------------------------------------------------------
# 4. PUBLIC FUNCTION — this is what app.py calls
# ---------------------------------------------------------------------
def run_research(topic: str, api_key: str | None = None) -> str:
    """
    Runs the single-agent research crew on `topic` and returns the
    final report as a Markdown string.
    """
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError(
            "No Groq API key found. Set GROQ_API_KEY as an environment "
            "variable or Streamlit secret."
        )

    crew = build_crew(topic, key)
    result = crew.kickoff()
    return str(result)


if __name__ == "__main__":
    # Quick manual test: `python research_agent.py`
    load_env_topic = input("Enter a research topic: ")
    print(run_research(load_env_topic))
