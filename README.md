# TicketFlow – NLP-Based Support Ticket Classification System

A professional, modern SaaS-style web application for automated customer support ticket triage. **TicketFlow** analyzes incoming customer complaints using Natural Language Processing (NLP), predicts issue categories using machine learning, determines priority levels using keyword heuristics, and routes tickets to appropriate support departments.

Built with a sleek **Black & Yellow (#FACC15)** dark design system, persistent SQLite database, and high-performance cached inference.

---

## 🎯 Key Features

1. **Modern SaaS Interface (Black & Yellow Theme)**:
   - Deep dark backgrounds (`#0B0B0B` / `#171717`) with crisp yellow accents (`#FACC15`).
   - Clean card-based dashboard with real-time ticket counters and metric badges.
   - Fluid sidebar navigation between Dashboard, Ticket Classifier, Ticket History, and Project Documentation.

2. **Text Classification (NLP + ML)**:
   - Categorizes incoming complaints into four distinct classes:
     - **Technical** ➔ `Technical Support`
     - **Billing** ➔ `Billing Support`
     - **Account** ➔ `Account Support`
     - **Service** ➔ `Customer Service`
   - Trained on `tickets_dataset.csv` using **TF-IDF Vectorization** and **Logistic Regression** (81.25% test accuracy).

3. **Rule-Based Priority Detection**:
   - Transparent, keyword-driven heuristics:
     - 🔴 **High Priority**: `crash`, `unauthorized`, `urgent`, `charged twice`, `locked out`, `severe`, `emergency`
     - 🟡 **Medium Priority**: `error`, `refund`, `delay`, `bug`, `slow`, `timeout`, `declined`, `failed`
     - 🟢 **Low Priority**: General inquiries, how-to requests, feedback, onboarding questions

4. **Persistent SQLite Storage**:
   - Replaces transient session-only storage with a lightweight local SQLite database (`database/tickets.db`).
   - Tickets persist across browser refreshes, application restarts, and system reboots.
   - Built-in audit trail, search query engine, category/priority filters, and CSV export.

5. **Authentication & Session Handling**:
   - Local user authentication with salted **PBKDF2-HMAC-SHA256** password hashing.
   - Pre-seeded evaluation demo credentials (`demo@ticketflow.io` / `demo123`).
   - User profile avatar and sign-out controls in the sidebar.

6. **Fast Startup & Streamlit Optimization**:
   - Model and vectorizer loading cached with `@st.cache_resource`.
   - Telemetry calls disabled via `.streamlit/config.toml` (`gatherUsageStats = false`).
   - Native system typography fallbacks without slow external web-font requests.

---

## 📂 Project Structure

```text
TicketFlow/
│
├── app.py                     # Main Streamlit SaaS application & routing
├── train_model.py             # Model training, evaluation & serialization script
├── tickets_dataset.csv        # Balanced support complaints dataset
├── requirements.txt           # Python dependencies (streamlit, pandas, scikit-learn)
├── README.md                  # Project documentation & manual test guide
├── model.pkl                  # Trained Logistic Regression model
├── tfidf_vectorizer.pkl       # Fitted TF-IDF Vectorizer
│
├── .streamlit/
│   └── config.toml            # Performance & black-yellow theme configuration
│
├── database/
│   ├── __init__.py
│   ├── db.py                  # SQLite database access layer (users & tickets)
│   └── tickets.db             # Persistent SQLite database file
│
└── utils/
    ├── __init__.py
    ├── ml_engine.py           # Cached inference, priority detection & routing
    └── styles.py              # Black and yellow SaaS CSS design tokens
```

---

## ⚙️ Quick Start

### 1. Prerequisites
- Python 3.9+ installed on your computer.

### 2. Navigate to Project Directory
```bash
cd TicketFlow
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Retrain Model
If you ever want to regenerate `model.pkl` and `tfidf_vectorizer.pkl`:
```bash
python train_model.py
```

### 5. Launch Application Easily (One-Click)

**On Windows:**
- Double-click **`start.bat`** (or run `start.bat` from terminal)
  - Automatically verifies environment, dependencies, and model artifacts.
  - Prevents starting duplicate instances if already running.
  - Opens `http://127.0.0.1:8501` in your default browser.

**To stop the application:**
- Double-click **`stop.bat`** (or run `stop.bat` from terminal)
  - Identifies the TicketFlow process on port 8501.
  - Prompts for confirmation and terminates only the verified TicketFlow server.

**Alternative command-line startup:**
```bash
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

---

## 🔑 Demo Account Credentials

For quick evaluation and viva demonstrations, a pre-configured account is ready to use:
- **Email:** `demo@ticketflow.io`
- **Password:** `demo123`

You can also create a new account in seconds via the **Sign Up** tab.

---

## 🧪 Demonstration Test Cases

| # | Sample Complaint Text | Expected Category | Priority | Assigned Department |
|---|---|---|---|---|
| 1 | *"The app keeps crashing with a 500 error whenever I open analytics."* | **Technical** | High (`crashing`) | Technical Support |
| 2 | *"I was charged twice on my credit card and need an urgent refund."* | **Billing** | High (`charged twice`, `urgent`) | Billing Support |
| 3 | *"My account has been locked due to unauthorized login attempts."* | **Account** | High (`unauthorized`, `locked`) | Account Support |
| 4 | *"The customer support representative was very rude on the phone call."* | **Service** | Low | Customer Service |
| 5 | *"There is a minor bug causing a slow delay in dashboard loading."* | **Technical** | Medium (`bug`, `slow`, `delay`) | Technical Support |
| 6 | *"Where can I find the official user guide documentation?"* | **Service** | Low | Customer Service |

---

## 🧠 NLP Architecture

```text
Customer Complaint Text
          ↓
TF-IDF Feature Extraction (unigrams + bigrams)
          ↓
Logistic Regression Classifier (81.25% test accuracy)
          ↓
Category Prediction [Technical, Billing, Account, Service]
          ↓
Keyword Heuristic Priority Detection [High, Medium, Low]
          ↓
Support Department Routing [e.g. Technical Support]
          ↓
Persistent SQLite Audit Log (database/tickets.db)
```
