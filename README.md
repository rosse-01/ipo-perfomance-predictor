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
