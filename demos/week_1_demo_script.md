[0:00-0:15] Introduction
"Hi, I'm [name], an economist building an AI career coach 
to transition into Python finance freelancing. 
Here's what I built in Week 1."

[0:15-0:45] Show Architecture
- Open README.md → scroll through features
- Show folder structure
- "Local-first: Ollama LLM + ChromaDB vector database"

[0:45-1:15] Live Demo
Terminal 1:
$ python src/main.py --watch

Terminal 2:
$ cat > data/monitored_folders/job_posts/demo_job.txt
[paste job description]

Terminal 1 shows:
📥 NEW FILE DETECTED: demo_job.txt
✓ Indexed as 'job_description'

Back to Terminal 2:
$ python src/main.py
[Shows job fit analysis with gap report]

[1:15-1:45] Show Output
"Coach analyzes my 8 years of economics experience 
vs Python finance job requirements.
Tells me: 40% ready, learn Pandas this week."

[1:45-2:00] Wrap-up
"Week 1 complete. Built RAG system, real-time monitoring,
and learned Python fundamentals.
Next: API integrations with Todoist and Perplexity.
Follow along on GitHub!"

[Show GitHub URL]
