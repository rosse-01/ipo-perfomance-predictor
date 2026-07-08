## The Data Science Pipeline

Before deploying the microservice, a rigorous machine learning lifecycle was executed within Google Colab to ensure model reliability:

### 1. Data Processing & Feature Engineering

* **Feature Selection:** The model analyzes key institutional and retail demand metrics: Issue Size, Qualified Institutional Buyers (QIB) subscription multiplier, High Net-worth Individuals (HNI) subscription multiplier, and Retail Individual Investors (RII) subscription multiplier.
* **Target Mapping:** Continuous historical listing gains were transformed into a binary classification problem ($1$ for profitable listings yielding day-one premium returns, $0$ for flat or negative discount listings).
* **Class Imbalance Handling:** Checked and balanced historical IPO performance trends to ensure the training loop didn't over-fit toward market bull runs.

### 2. Model Selection & Evaluation Matrix

A **Random Forest Classifier** was selected due to its ensemble resilience against localized market anomalies and its ability to rank feature importances accurately.

* **The Scoring System:** The backend doesn't just pass back a hard prediction; it extracts the underlying prediction probability ($P(\text{profitable} \mid X)$). This allows the Streamlit UI to dynamically display risk thresholds:
* **$P > 70\%$**: Green Sign (`High Market Confidence`)
* **$45\% \le P \le 70\%$**: Yellow Sign (`Moderate Market Caution`)
* **$P < 45\%$**: Red Sign (`High Capital Risk`)



---

## 🔄 End-to-End System Request Lifecycle

When a user interacts with your deployed application, data traverses through a classic enterprise microservice pattern:

```text
[ User Input ] 
       │
       ▼
 ┌───────────┐
 │ Streamlit │ ────► Packages features into JSON payload
 └───────────┘       Injects secure 'X-API-KEY' into HTTP Request Header
       │
       ▼  (Traverses public internet via HTTP POST)
 ┌───────────┐
 │  AWS ECS  │ ────► Intercepted by AWS Virtual Network Endpoint
 └───────────┘
       │
       ▼
 ┌───────────┐
 │  FastAPI  │ ────► Check 1: Middleware validates 'X-API-KEY' token match
 │ Container │       Check 2: Pydantic sanitizes and parses JSON input data
 └───────────┘
       │
       ▼  (Data passes internal validation checks)
 ┌───────────┐
 │ ML Model  │ ────► Compute inference score via serialized Scikit-Learn pipeline
 └───────────┘
       │
       ▼
 [ JSON Resp ] ◄──── FastAPI sends HTTP 200 status back with prediction payload
       │
       ▼
 [ Render UI ] ◄──── Streamlit extracts JSON, evaluates conditional logic, displays UI cards

```

---

## 💎 Key Architectural Takeaways for Interviewers

If an interviewer asks you about this project, focus your discussion on these three engineering paradigms:

1. **Decoupled Lifecycles:** Training code is heavy and slow; inference code must be lightweight and rapid. By separating the training phase (Colab) from the live inference endpoint (FastAPI), the application can scale up production instances instantly without dragging the entire machine learning engine with it.
2. **Stateless Operations:** The FastAPI backend is entirely stateless. It does not track user sessions or keep history. This allows you to scale your AWS Fargate container horizontally (from 1 task to 10 tasks) smoothly under sudden market traffic spikes.
3. **Defensive API Constraints:** By implementing Pydantic validation schemas, the model is completely protected from crashes caused by bad or empty input fields, making the production container incredibly stable.

Would you like to add an automated performance tracking tool (like Prometheus or simple internal timings) to monitor how fast your backend returns predictions?
