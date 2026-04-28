MarketHub.ai 
**A simple and powerful hub for jobs, AI insights, and community.**
VISIT: https://markethub-ai-2.onrender.com/ 
to see for yourself
MarketHub.ai helps you find the best jobs, use AI to see what you're worth, and connect with other agents while keeping your identity private. It's fast, secure, and ready to use.
<img width="1919" height="965" alt="Screenshot 2026-04-28 220159" src="https://github.com/user-attachments/assets/708bf463-578e-4bd9-b345-7e0fbc050371" />
<img width="1901" height="953" alt="Screenshot 2026-04-28 220625" src="https://github.com/user-attachments/assets/5de9fb0e-7054-4aef-a302-415132270f0e" />
<img width="1915" height="967" alt="Screenshot 2026-04-28 221154" src="https://github.com/user-attachments/assets/b2b9bc11-84a1-4b90-bfa5-aec8f19dd9da" />
<img width="1914" height="959" alt="Screenshot 2026-04-28 221414" src="https://github.com/user-attachments/assets/1716c5a2-c99d-4b6f-847f-fcd8646b0374" />

Core Capabilities
- Market Stream:** A live, real-time feed of global job dossiers and high-value roles.
- AI Simulator:** Intelligent salary market-value prediction powered by LLM zero-shot classification.
- Social Identities:** Protect your privacy with customizable Agent Names (Usernames) while browsing the community.
- Secure Cipher:** Robust authentication using JWT (JSON Web Tokens) and bcrypt hashing.
- Directives:** A sleek, glass-morphed task management system for agent operations.

### Technology Stack
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Database:** PostgreSQL with SQLAlchemy (ORM)
- **Intelligence (Optional):** [Groq API](https://groq.com/) (On-demand Salary Prediction)
- **Architecture:** Modular Service Layer (AI-Optional)

---

###  AI Intelligence (Optional)
The AI Intelligence module is fully isolated. You can toggle it using the `AI_PROVIDER` environment variable:

- `disabled` (Default): AI endpoints return a graceful "service disabled" message.
- `groq`: Enables salary prediction using the internal Groq provider (requires `GROQ_API_KEY`).

---

---

### Quick Start
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

### Architecture
The project follows a modular design pattern:
- `main.py`: Core API logic and identity gateways.
- `models.py`: Relational database schemas for Agents and Jobs.
- `security.py`: JWT encryption and cipher processing.
- `static/index.html`: The high-end Platinum Pro Console UI.

---
*Built for the 15-Day FastAPI Challenge and beyond. 
