import os
import re
import time
import requests
import streamlit as st
import feedparser

from dotenv import load_dotenv
from autogen import (
    AssistantAgent,
    UserProxyAgent,
    GroupChat,
    GroupChatManager
)

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f8fafc;
}

/* Title */

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
}

.sub-title {
    font-size: 18px;
    color: #6b7280;
    margin-bottom: 20px;
}

/* Chat Bubble */

.bubble {
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 15px;
    line-height: 1.7;
    font-size: 15px;
}

/* Agent Name */

.bubble-name {
    font-weight: bold;
    margin-bottom: 8px;
    font-size: 13px;
    text-transform: uppercase;
}

/* Planner */

.planner {
    background: #dbeafe;
    border-left: 6px solid #2563eb;
}

.planner .bubble-name {
    color: #2563eb;
}

/* Critic */

.critic {
    background: #fef3c7;
    border-left: 6px solid #d97706;
}

.critic .bubble-name {
    color: #d97706;
}

/* Researcher */

.researcher {
    background: #dcfce7;
    border-left: 6px solid #16a34a;
}

.researcher .bubble-name {
    color: #16a34a;
}

/* Writer */

.writer {
    background: #f3e8ff;
    border-left: 6px solid #9333ea;
}

.writer .bubble-name {
    color: #9333ea;
}

/* User */

.user-box {
    background: #e2e8f0;
    border-left: 6px solid #64748b;
}

.user-box .bubble-name {
    color: #475569;
}

/* Report */

.report-box {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

.metric-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 15px;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🤖 AI Research Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Multi-Agent Research System using AutoGen + Groq + GitHub + arXiv</div>',
    unsafe_allow_html=True
)

# =========================================================
# API KEY
# =========================================================

os.environ["GROQ_API_KEY"] = "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"

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Settings")

    model_name = st.selectbox(
        "Select Model",
        [
            "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile",
            "mixtral-8x7b-32768"
        ]
    )

    github_limit = st.slider(
        "GitHub Repositories",
        1,
        5,
        3
    )

    arxiv_limit = st.slider(
        "arXiv Papers",
        1,
        5,
        3
    )

# =========================================================
# LLM CONFIG
# =========================================================

config_list = [
    {
        "model": model_name,
        "api_key": os.environ["GROQ_API_KEY"],
        "base_url": "https://api.groq.com/openai/v1",
        "price": [0.0001, 0.0002]
    }
]

llm_config = {
    "config_list": config_list,
    "temperature": 0.2,
    "timeout": 120,
    "max_tokens": 500
}

# =========================================================
# VALIDATION
# =========================================================

def basic_topic_validation(topic):

    if len(topic.strip()) < 4:
        return False

    words = re.findall(r"[a-zA-Z]{3,}", topic)

    return len(words) > 0


def llm_topic_validation(topic):

    validator = AssistantAgent(
        name="Validator",
        system_message="""
Reply ONLY YES if topic is meaningful.
Otherwise reply ONLY NO.
""",
        llm_config=llm_config
    )

    try:

        response = validator.generate_reply(
            messages=[
                {
                    "role": "user",
                    "content": topic
                }
            ]
        )

        return response and "YES" in response.upper()

    except:
        return False

# =========================================================
# GITHUB SEARCH
# =========================================================

def search_github(query, max_results=3):

    repos = []

    try:

        encoded_query = requests.utils.quote(query)

        url = (
            "https://api.github.com/search/repositories?"
            f"q={encoded_query}&sort=stars&order=desc"
        )

        response = requests.get(url, timeout=10)

        if response.status_code == 200:

            data = response.json()

            for repo in data.get("items", []):

                if repo["stargazers_count"] >= 50:

                    repos.append({
                        "name": repo["full_name"],
                        "url": repo["html_url"],
                        "stars": repo["stargazers_count"],
                        "forks": repo["forks_count"]
                    })

                if len(repos) >= max_results:
                    break

    except Exception as e:
        st.error(f"GitHub Error: {e}")

    return repos

# =========================================================
# ARXIV SEARCH
# =========================================================

def search_arxiv(query, max_results=3):

    papers = []

    try:

        encoded_query = requests.utils.quote(query)

        url = (
            "http://export.arxiv.org/api/query?"
            f"search_query=all:{encoded_query}"
            f"&start=0&max_results={max_results}"
        )

        feed = feedparser.parse(url)

        for entry in feed.entries:

            papers.append({
                "title": entry.title,
                "link": entry.link
            })

    except Exception as e:
        st.error(f"arXiv Error: {e}")

    return papers

# =========================================================
# EVALUATION METRICS
# =========================================================

def calculate_relevance(topic, report):

    topic_words = set(re.findall(r'\w+', topic.lower()))

    report_words = set(re.findall(r'\w+', report.lower()))

    matched = topic_words.intersection(report_words)

    if len(topic_words) == 0:
        return 0

    score = (len(matched) / len(topic_words)) * 100

    return round(score, 2)


def calculate_agent_contribution(history):

    counts = {}

    total = 0

    for msg in history:

        name = msg.get("name", "Unknown")

        counts[name] = counts.get(name, 0) + 1

        total += 1

    contribution = {}

    for agent, count in counts.items():

        contribution[agent] = round((count / total) * 100, 2)

    return contribution


def calculate_coverage(report, github_results, arxiv_results):

    total_resources = len(github_results) + len(arxiv_results)

    found = 0

    for repo in github_results:

        if repo["name"] in report:
            found += 1

    for paper in arxiv_results:

        if paper["title"] in report:
            found += 1

    if total_resources == 0:
        return 0

    return round((found / total_resources) * 100, 2)

# =========================================================
# AGENTS
# =========================================================

planner = AssistantAgent(
    name="Planner",
    system_message="Give ONLY 2 short research directions.",
    llm_config=llm_config
)

critic = AssistantAgent(
    name="Critic",
    system_message="Give ONLY 1 short improvement.",
    llm_config=llm_config
)

researcher = AssistantAgent(
    name="Researcher",
    system_message="Summarize repositories and papers in 3 short lines.",
    llm_config=llm_config
)

writer = AssistantAgent(
    name="Writer",
    system_message="""
Create a COMPLETE markdown research report.

STRICT RULES:
- Use ONLY provided GitHub repositories and arXiv papers
- DO NOT create fake links
- Include ALL repositories and papers
- Keep report under 300 words

FORMAT:

# Research Report

## GitHub Repositories

### Repository Name
- Stars:
- Forks:
- URL:

## Research Papers

### Paper Title
- URL:

## Summary
Short summary.
""",
    llm_config=llm_config
)

user = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config=False
)

# =========================================================
# MAIN FUNCTION
# =========================================================

def run_research(topic):

    start_time = time.time()

    if not basic_topic_validation(topic):
        return "❌ Invalid Topic", [], [], [], 0

    if not llm_topic_validation(topic):
        return "❌ Topic Rejected", [], [], [], 0

    github_results = search_github(
        topic,
        github_limit
    )

    arxiv_results = search_arxiv(
        topic,
        arxiv_limit
    )

    if not github_results and not arxiv_results:
        return "❌ No Results Found", [], [], [], 0

    # =====================================================
    # FALLBACK REPORT
    # =====================================================

    report_fallback = "# Research Report\n\n"

    report_fallback += "## GitHub Repositories\n\n"

    for repo in github_results:

        report_fallback += f"""
### {repo['name']}
- Stars: {repo['stars']}
- Forks: {repo['forks']}
- URL: {repo['url']}

"""

    report_fallback += "\n## Research Papers\n\n"

    for paper in arxiv_results:

        report_fallback += f"""
### {paper['title']}
- URL: {paper['link']}

"""

    report_fallback += """
## Summary

This report contains GitHub repositories and arXiv papers related to the selected research topic.
"""

    # =====================================================
    # MESSAGE FOR AGENTS
    # =====================================================

    github_text = ""

    for repo in github_results:

        github_text += f"""
Repository: {repo['name']}
Stars: {repo['stars']}
Forks: {repo['forks']}
URL: {repo['url']}
"""

    arxiv_text = ""

    for paper in arxiv_results:

        arxiv_text += f"""
Paper: {paper['title']}
URL: {paper['link']}
"""

    message = f"""
Research Topic: {topic}

GITHUB REPOSITORIES:
{github_text}

ARXIV PAPERS:
{arxiv_text}
"""

    # =====================================================
    # GROUP CHAT
    # =====================================================

    groupchat = GroupChat(
        agents=[
            user,
            planner,
            critic,
            researcher,
            writer
        ],
        messages=[],
        max_round=6,
        speaker_selection_method="round_robin"
    )

    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=llm_config
    )

    try:

        result = user.initiate_chat(
            manager,
            message=message
        )

        history = result.chat_history if result else []

        final_report = report_fallback

        for msg in reversed(history):

            if (
                msg.get("name") == "Writer"
                and msg.get("content")
                and len(msg.get("content").strip()) > 20
            ):

                final_report = msg["content"]
                break

        end_time = time.time()

        execution_time = round(end_time - start_time, 2)

        return (
            final_report,
            history,
            github_results,
            arxiv_results,
            execution_time
        )

    except Exception as e:

        return f"❌ Agent Error: {e}", [], [], [], 0

# =========================================================
# INPUT
# =========================================================

topic = st.text_input(
    "🔍 Enter Research Topic",
    placeholder="Example: Vision Transformers"
)

# =========================================================
# BUTTON
# =========================================================

if st.button("🚀 Generate Research Report"):

    if not topic.strip():

        st.warning("Please enter a research topic.")

    else:

        with st.spinner("AI Agents are working..."):

            (
                report,
                history,
                github_results,
                arxiv_results,
                execution_time
            ) = run_research(topic)

        st.success("Research Report Generated Successfully!")

        # =================================================
        # CHAT SECTION
        # =================================================

        st.subheader("💬 Agents Conversation")

        agent_styles = {
            "Planner": ("planner", "🗺️ Planner"),
            "Critic": ("critic", "🔍 Critic"),
            "Researcher": ("researcher", "🧪 Researcher"),
            "Writer": ("writer", "✍️ Writer"),
            "User": ("user-box", "👤 User")
        }

        if history:

            for msg in history:

                name = msg.get("name", "User")
                content = msg.get("content", "")

                if not content:
                    continue

                css_class, label = agent_styles.get(
                    name,
                    ("user-box", name)
                )

                st.markdown(
                    f"""
<div class="bubble {css_class}">
<div class="bubble-name">{label}</div>
{content}
</div>
""",
                    unsafe_allow_html=True
                )

        st.divider()

        # =================================================
        # REPORT DISPLAY
        # =================================================

        if not report or report.strip() == "":

            report = """
# Research Report

No report generated.
"""

        st.subheader("📄 Final Research Report")

        st.markdown(report)

        st.divider()

        # =================================================
        # EVALUATION METRICS
        # =================================================

        st.subheader("📊 Evaluation Metrics")

        relevance_score = calculate_relevance(
            topic,
            report
        )

        coverage_score = calculate_coverage(
            report,
            github_results,
            arxiv_results
        )

        contribution_scores = calculate_agent_contribution(
            history
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "🎯 Relevance Score",
                f"{relevance_score}%"
            )

        with col2:
            st.metric(
                "📚 Coverage Score",
                f"{coverage_score}%"
            )

        with col3:
            st.metric(
                "⏱️ Response Time",
                f"{execution_time} sec"
            )

        st.write("### 🤝 Agent Contribution")

        for agent, score in contribution_scores.items():

            st.write(f"**{agent}** : {score}%")

            st.progress(score / 100)

        st.divider()

        # =================================================
        # DOWNLOAD BUTTON
        # =================================================

        st.download_button(
            label="⬇️ Download Report",
            data=report,
            file_name=f"{topic.replace(' ', '_')}_report.md",
            mime="text/markdown"
        )