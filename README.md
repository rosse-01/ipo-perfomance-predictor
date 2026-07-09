# IPO Listing Gain Prediction System

An end-to-end, production-grade microservice architecture designed to predict day-one IPO listing gains. This system decouples data science workflows into high-performance engineering components by featuring a **Streamlit** frontend dashboard linked via secure REST APIs to a containerized **FastAPI** inference engine deployed on **AWS Fargate (ECS)**.


https://github.com/user-attachments/assets/7cb7d1dd-68a8-48dd-9413-9bb405da6db0



---

## System Architecture & Workflow

The platform leverages a fully decoupled, client-server microservice topology built for structural isolation and compute optimization:

1. **Exploratory Data Analysis & Training:** Features engineered, models evaluated, and serialized (`Joblib`) using an optimized Random Forest Classifier pipeline inside Google Colab.
2. **Frontend UI Client (Streamlit):** Gathers real-time multi-variable investment metrics from users, validates state conditions, and coordinates asynchronous API web requests.
3. **Backend Routing Infrastructure (FastAPI):** Orchestrates high-throughput, concurrent inference routes (`async def`) and validates JSON payloads utilizing strict structural schemas.
4. **Cloud Virtualization & Security Layer:** Packaged via Docker containers and executed serverless on AWS Fargate with zero public port exposures outside of explicit programmatic authentication handshakes.

---

## Production Security & Cost Mitigation

To transition this from a localized data science experiment to a resilient, public-facing system, defensive software patterns were built directly into the network middleware:

* **Token-Based Header Authentication:** The backend endpoint is entirely locked down. It intercepts incoming HTTP traffic to verify a secret authorization token (`X-API-KEY`) inside the metadata headers before triggering any localized machine learning code. Unauthenticated scanners and brute-force scripts are instantly dropped with an HTTP `403 Forbidden` response, protecting cloud vCPU and RAM allocation from financial exhaustion.
* **Payload Sanitation via Pydantic:** Strict structural definitions enforce object schemas (`IPOFeatures`). Corrupted data types, out-of-bounds metrics, or injection payloads are safely rejected at the gate with an HTTP `422 Unprocessable Entity` status before hitting model memory layers.
* **Secure Credential Hygiene:** Hardcoded credential strings are entirely eliminated from production code. Cryptographic tokens and environmental settings are loaded dynamically at runtime via system memory variables (`os.getenv` / `st.secrets`) integrated with rigid `.gitignore` file tracking to maintain pristine open-source security profiles.

---

## Tech Stack & Key Tooling

* **Frontend Dashboard:** Streamlit, Python-Dotenv, Requests
* **Backend API Engine:** FastAPI, Uvicorn, Pydantic, Joblib
* **Data & Machine Learning:** Scikit-Learn, Pandas, NumPy, Jupyter (Google Colab)
* **DevOps & Cloud:** Docker, AWS ECS (Fargate), Linux Containers, Git

---
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

## End-to-End System Request Lifecycle

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
