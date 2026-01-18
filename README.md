MarketHub.ai 

**A simple and powerful hub for jobs, AI insights, and community.**

MarketHub.ai helps you find the best jobs, use AI to see what you're worth, and connect with other agents while keeping your identity private. It's fast, secure, and ready to use.

---

 Core Capabilities
- Market Stream:** A live, real-time feed of global job dossiers and high-value roles.
- AI Simulator:** Intelligent salary market-value prediction powered by LLM zero-shot classification.
- Social Identities:** Protect your privacy with customizable Agent Names (Usernames) while browsing the community.
- Secure Cipher:** Robust authentication using JWT (JSON Web Tokens) and bcrypt hashing.
- Directives:** A sleek, glass-morphed task management system for agent operations.

### 🛠️ Technology Stack
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** PostgreSQL with SQLAlchemy (ORM)
- **Intelligence (Optional):** [Groq API](https://groq.com/) (On-demand Salary Prediction)
- **Architecture:** Modular Service Layer (AI-Optional)

---

### 🧠 AI Intelligence (Optional)
The AI Intelligence module is fully isolated. You can toggle it using the `AI_PROVIDER` environment variable:

- `disabled` (Default): AI endpoints return a graceful "service disabled" message.
- `groq`: Enables salary prediction using the internal Groq provider (requires `GROQ_API_KEY`).

---

---

### 🚀 Quick Start
1. **Clone the Registry:**
   ```bash
   git clone https://github.com/your-username/markethub-ai.git
   cd markethub-ai
   ```

2. **Initialize Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Deploy Locally:**
   ```bash
   python -m uvicorn main:app --reload
   ```

---

### 📑 Architecture
The project follows a modular design pattern:
- `main.py`: Core API logic and identity gateways.
- `models.py`: Relational database schemas for Agents and Jobs.
- `security.py`: JWT encryption and cipher processing.
- `static/index.html`: The high-end Platinum Pro Console UI.

---
*Built for the 30-Day FastAPI Challenge and beyond. Platinum Pro Console Edition.* 💎
