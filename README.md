# 🤖 A Multi-Agent LLM-Based Research Framework Using AutoGen

## 📌 Overview

AI Research Assistant is a Multi-Agent LLM-based system that automates research by gathering information from GitHub repositories and arXiv research papers. The application uses multiple AI agents powered by AutoGen and Groq LLMs to collaboratively analyze a research topic and generate a structured research report.

The system provides researchers, students, and developers with relevant repositories, academic papers, summaries, evaluation metrics, and downloadable reports through an interactive Streamlit interface.

---

## 🚀 Features

* Multi-Agent AI Collaboration
* Research Topic Validation
* GitHub Repository Search
* arXiv Research Paper Search
* Automated Research Report Generation
* Interactive Streamlit Dashboard
* Agent Conversation Visualization
* Research Evaluation Metrics
* Markdown Report Download
* Fast Response using Groq LLMs

---

## 🏗️ System Architecture

The system consists of multiple AI agents:

### 🗺️ Planner Agent

* Generates research directions.
* Breaks down the research topic.

### 🔍 Critic Agent

* Reviews generated content.
* Suggests improvements.

### 🧪 Researcher Agent

* Analyzes GitHub repositories.
* Reviews arXiv papers.
* Extracts key insights.

### ✍️ Writer Agent

* Creates the final research report.
* Organizes repositories, papers, and summaries.

### 👤 User Agent

* Initiates the conversation.
* Coordinates interactions among agents.

---

## 🛠️ Technologies Used

* Python
* Streamlit
* AutoGen
* Groq API
* GitHub API
* arXiv API
* Feedparser
* Requests
* Regular Expressions (Regex)
* dotenv

---

## 📂 Workflow

1. User enters a research topic.
2. Topic is validated.
3. GitHub repositories related to the topic are fetched.
4. Relevant arXiv papers are retrieved.
5. AI agents collaborate through group chat.
6. Research findings are analyzed.
7. Final report is generated automatically.
8. Evaluation metrics are calculated.
9. Report is displayed and available for download.

---

## 📊 Evaluation Metrics

The system evaluates generated reports using:

* Relevance Score
* Coverage Score
* Agent Contribution Score
* Response Time

---

## 📋 Generated Output

The generated report contains:

* Research Topic
* GitHub Repositories
* Repository Statistics
* Research Papers
* Paper Links
* Summary and Insights

---

## 🔧 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/ai-research-assistant.git
cd ai-research-assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

---

## 🎯 Applications

* Academic Research
* Literature Review
* Technology Exploration
* Research Paper Discovery
* Open Source Project Discovery
* AI-Assisted Knowledge Gathering

---

## 🔮 Future Enhancements

* PDF Report Generation
* Citation Management
* Research Paper Summarization
* Multi-LLM Support
* Research Trend Analysis
* Interactive Visual Analytics
* Export to DOCX and PDF

---

## 👨‍💻 Author

**Yaswitha**

---

## ⭐ Conclusion

AI Research Assistant leverages Multi-Agent AI systems to automate research workflows by integrating large language models, GitHub repositories, and arXiv papers. The platform enables efficient knowledge discovery, structured report generation, and collaborative AI-driven research analysis.
