# 🤖 AI Career Coach: Economist → FinTech Python Freelancer

> **Portfolio Project**: Production-ready AI career transition system using local LLM + RAG architecture

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🎯 Project Vision

Personal AI coach that transforms **8 years of economics expertise** into a **€10k/month Python finance freelancing career** in 12 months. Built while learning Python from scratch.

### The Challenge
- Fragmented career data across 5+ apps
- Generic job advice (not personalized to economist background)
- Manual CV tailoring takes hours per application
- No accountability system for skill development

### The Solution
**Local-first AI brain** that:
- ✅ Unifies knowledge (Anytype + Todoist + Obsidian + files)
- ✅ Real-time job analysis (drop PDF → instant gap report)
- ✅ Privacy-first (local LLM + selective Perplexity research)
- ✅ Gamified progress tracking (56-day streak system)

---

## 🏗️ Architecture (Week 1 Complete)
```
📁 Files (CVs, job PDFs, notes)
↓ Real-time monitoring (watchdog)
🧠 Local RAG Brain (ChromaDB + Ollama)
↓ Smart routing
🤖 Dual LLMs
├─ Local (Ollama llama3.2) → Personal coaching
└─ Perplexity API → Market research
↓
📊 Outputs
├─ Skills gap analysis
├─ Learning roadmaps
└─ Todoist tasks

---

## ✨ Features (Week 1)

| Feature | Status | Demo |
|---------|--------|------|
| Local LLM integration | ✅ Done | Ollama llama3.2 |
| RAG knowledge base | ✅ Done | ChromaDB vector search |
| File processor (PDF/TXT) | ✅ Done | Multi-format support |
| Real-time file watcher | ✅ Done | Auto-index on drop |
| Job fit analyzer | ✅ Done | CV vs JD comparison |
| Skills inventory | ✅ Done | Economist expertise mapped |

**Coming Soon (Weeks 2-8)**:
- Anytype Live Sync (Week 3)
- Todoist task automation (Week 4)
- Perplexity market research (Week 5)
- Voice UI (Week 7)
- Progress dashboard (Week 8)

---

## 🚀 Quick Start

### Prerequisites
```
Install Python 3.11+
python3 --version

Install Ollama
macOS: brew install ollama
Linux: curl -fsSL https://ollama.ai/install.sh | sh
Pull LLM model
ollama pull llama3.2
```
```


### Installation
```
Clone repo
git clone https://github.com/YOUR_USERNAME/ai-career-coach-fintech.git
cd ai-career-coach-fintech

Setup environment
python3 -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate

Install dependencies
pip install -r requirements.txt

Create data folders
mkdir -p data/monitored_folders/{job_posts,econ_work,cv_archive}
mkdir -p data/knowledge_base/skills
```

### Usage

**1. Load your knowledge**:
```
Add your skills
cp your_cv.pdf data/monitored_folders/cv_archive/
nano data/knowledge_base/skills/economics_expertise.txt

(Paste your economist skills - see examples in repo)
```

**2. Run standard mode**:
```
python src/main.py
```


**3. Enable file monitoring** (real-time):
```
python src/main.py --watch

Drop job PDFs into data/monitored_folders/job_posts/
Instant analysis appears!
```


**4. Run tests**:
```
python tests/test_coach.py
```

---

## 💼 Portfolio Highlights

**Skills Demonstrated**:
- ✅ Local LLM integration (Ollama API)
- ✅ RAG architecture (ChromaDB embeddings)
- ✅ Real-time event processing (Watchdog)
- ✅ Multi-format file parsing (PDF/TXT)
- ✅ Prompt engineering (system prompts, context injection)
- ✅ Python OOP (classes, composition, error handling)

**Business Value**:
- Privacy-first AI (GDPR compliant, local-first)
- Scalable knowledge system (add unlimited documents)
- Cost-effective ($20/mo vs $500/mo career coach)
- Domain + code expertise (economist who codes Python)

---

## 📊 Project Stats
```
Build Time: 7 days (Week 1 complete)
Code Lines: ~800 SLOC
Components: 5 modules + tests
Dependencies: 12 core libraries
Learning: Python basics → Production RAG system
```


---

## 🎓 Learning Journey

**Week 1 Skills Mastered**:
1. Environment setup (venv, requirements.txt, git)
2. Local LLM integration (Ollama)
3. Vector databases (ChromaDB)
4. File I/O and PDF parsing
5. Event-driven programming (file watcher)

**Next Steps (Weeks 2-8)**:
- API integrations (Anytype, Todoist, Perplexity)
- Async processing
- Web UI (Streamlit)
- Data visualization (Plotly)

---

## 🤝 Contributing

This is a personal learning project, but feedback welcome!
- 🐛 Found a bug? Open an issue
- 💡 Have an idea? Start a discussion
- ⭐ Like it? Star the repo!

---

## 📝 License

MIT License - feel free to fork and adapt for your own career transition!

---

## 🎯 Unique Selling Point

**"8-year economist who built his own AI career coach while learning Python → targeting €10k/mo freelance gigs in finance automation, risk modeling, and economic data pipelines"**

Perfect for freelance proposals! 🚀

---

**Built with ❤️ and lots of ☕ by an economist learning to code**


