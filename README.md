# Sakshi AI Hackathon: Adaptive Exam-Prep Tutor with a Learner Model

An adaptive, syllabus-grounded intelligent tutor designed for standardized exam preparation. Unlike generic AI wrappers that merely answer user queries in isolation, **Sakshi AI** maintains a latent **Bayesian Knowledge Tracing (BKT)** learner model, evaluates intermediate reasoning to uncover cognitive misconceptions, schedules exam-paced spaced reviews, and visualizes class-wide learning gaps on an interactive teacher heatmap.

---

## 🏆 Problem Statement & Technical Solution Matrix

| # | Competition Requirement | Technical Implementation | File Reference |
|---|---|---|---|
| **1** | **Diagnostic Test** | 6-milestone adaptive diagnostic assessment that establishes initial baseline probability $P(L_0)$ across major curriculum clusters. | `deeptutor/learning/diagnostic.py`<br>`deeptutor/api/routers/diagnostic.py` |
| **2** | **Concept Graph (Class 10 Physics)** | Directed Acyclic Graph (DAG) for NCERT Class 10 Physics (Light, Electricity, Magnetism) with NetworkX cycle detection, topological ordering, and prerequisite gating. | `deeptutor/data/curriculum/class10_physics.json`<br>`deeptutor/learning/curriculum.py` |
| **3** | **Learner Model (BKT)** | Authentic 4-parameter Bayesian Knowledge Tracing updating latent understanding probability $P(L_t)$ after **every** response. | `deeptutor/learning/bkt.py`<br>`deeptutor/learning/mastery.py` |
| **4** | **Targeted Question Generation + Difficulty Calibration** | Algorithm locating concepts in the student's Zone of Proximal Development (ZPD) and calibrating difficulty across 3 tiers (Conceptual $\to$ Application $\to$ Calculation). | `deeptutor/learning/question_generator.py`<br>`deeptutor/api/routers/adaptive_learning.py` |
| **5** | **Reasoning-Based Misconception Detection** | Two-stage evaluation extracting step-by-step reasoning traces to catch underlying cognitive flaws—including lucky guesses where the final answer is right but the reasoning is invalid. | `deeptutor/learning/misconception.py`<br>`deeptutor/learning/semantic_assessment.py` |
| **6** | **Spaced-Repetition Scheduling** | Exponential retention half-life scheduler with **Exam Horizon Compression**, tightening review intervals as test day approaches to guarantee 100% syllabus coverage. | `deeptutor/learning/scheduler.py`<br>`deeptutor/learning/models.py` |
| **7** | **Teacher Dashboard (Class-Wide Gaps)** | Interactive cohort analytics screen displaying a 2D student $\times$ concept mastery heatmap, ranked class-wide knowledge gaps, and frequent misconception tallies. | `web/app/(workspace)/teacher/page.tsx`<br>`deeptutor/api/routers/teacher.py` |

---

## 🧠 Architectural Overview & Mathematical Models

```
                                  ┌──────────────────────────────┐
                                  │   Curriculum Prerequisite    │
                                  │       DAG (Class 10)         │
                                  └──────────────┬───────────────┘
                                                 │
                                                 ▼
┌─────────────────────────┐          ┌───────────────────────┐
│ Student Diagnostic Test │ ───────▶ │ Bayesian Knowledge    │
│  (6 Milestone Questions)│          │ Tracing (BKT) Engine  │
└─────────────────────────┘          └───────────┬───────────┘
                                                 │
                                                 ▼
┌─────────────────────────┐          ┌───────────────────────┐          ┌───────────────────────────┐
│ Reasoning Misconception │ ◀─────── │  Targeted Generation  │ ───────▶ │ Teacher Cohort Dashboard  │
│    Detection Engine     │          │  (ZPD + 3 Tiers)      │          │   (Matrix Heatmap & Gaps) │
└─────────────────────────┘          └───────────────────────┘          └───────────────────────────┘
```

### 1. Bayesian Knowledge Tracing (BKT) Formulation
For each concept $k$, latent understanding probability $P(L_t)$ updates on observation $\text{Obs} \in \{\text{correct}, \text{incorrect}\}$:

$$\begin{aligned}
P(L_{t-1} \mid \text{correct}) &= \frac{P(L_{t-1}) \cdot (1 - P(S))}{P(L_{t-1}) \cdot (1 - P(S)) + (1 - P(L_{t-1})) \cdot P(G)} \\
P(L_{t-1} \mid \text{incorrect}) &= \frac{P(L_{t-1}) \cdot P(S)}{P(L_{t-1}) \cdot P(S) + (1 - P(L_{t-1})) \cdot (1 - P(G))} \\
P(L_t) &= P(L_{t-1} \mid \text{Obs}) + (1 - P(L_{t-1} \mid \text{Obs})) \cdot P(T)
\end{aligned}$$

*Priors:* $P(L_0) = 0.20, P(T) = 0.15, P(S) = 0.10, P(G) = 0.20$. Probabilities are strictly bounded to $[0.0001, 0.9999]$ to prevent numerical zero-division.

### 2. Difficulty Calibration & Zone of Proximal Development (ZPD)
The engine queries the curriculum DAG to compute the frontier of eligible concepts:
- **Eligible Frontier:** Unmastered concepts ($P(L) < 0.75$) whose prerequisites are mastered ($P(L) \ge 0.70$).
- **Difficulty Scaling:**
  - $P(L) < 0.40 \implies$ **Level 1 (Conceptual):** Qualitative definitions, core laws, intuition.
  - $0.40 \le P(L) < 0.70 \implies$ **Level 2 (Application):** Direct formula substitution, basic circuits/ray diagrams.
  - $P(L) \ge 0.70 \implies$ **Level 3 (Calculation):** Multi-step numericals, combined resistors, complex lens equations.

### 3. Exam-Paced Spaced Repetition Horizon
When a target exam date $t_{\text{exam}}$ is set, remaining days $\Delta_{\text{exam}} = (t_{\text{exam}} - t_{\text{now}}) / 86400$:
$$\kappa = \max\left(0.2, \frac{\Delta_{\text{exam}}}{14}\right)$$
$$\Delta t_{\text{review}} = \min\left(t_{\text{now}} + \kappa \cdot \Delta t_{\text{base}}, \, t_{\text{exam}} - 0.5 \times 86400\right)$$
Guarantees high-retention review sessions occur at least 12 hours prior to the examination.

---

## 🚀 Quickstart & Verification

### 1. Prerequisites
- Linux / macOS
- Python 3.11+
- Node.js 20+

### 2. Run the Full Test Suite
Execute the comprehensive test suite verifying all 7 requirements end-to-end:

```bash
# Set PYTHONPATH to the repo root
export PYTHONPATH=$(pwd)

# Run all backend unit and integration test suites
pytest tests/test_pruned_runtime.py \
       tests/learning/ \
       tests/api/ \
       tests/integration/test_e2e_tutor_loop.py -v
```

### 3. Run the Web Unit Tests
```bash
cd web
npm run test:unit -- teacher-dashboard.spec.tsx
```

### 4. Start the Application
```bash
# Start FastAPI backend on port 8001
python -m deeptutor.api.main --port 8001

# In another terminal, start the Next.js frontend
cd web
npm run dev
```

Navigate to:
- Student Diagnostic Test: `http://localhost:3000/diagnostic`
- Teacher Cohort Analytics: `http://localhost:3000/teacher`

---

## 🔍 Judge Evaluation Walkthrough

To verify our claims during presentation or automated evaluation:

1. **Test Diagnostic Calibration:**
   ```bash
   curl -X POST http://localhost:8001/api/diagnostic/start \
        -H "Content-Type: application/json" \
        -d '{"syllabus": "class10_physics"}'
   ```
2. **Inspect Prerequisite DAG:**
   Examine `deeptutor/data/curriculum/class10_physics.json` and run `pytest tests/learning/test_curriculum_graph.py`.
3. **Verify BKT Mathematical Convergence:**
   Run `pytest tests/learning/test_bkt_mastery.py`.
4. **Trigger Reasoning Misconception Detection:**
   Run `pytest tests/learning/test_misconception_detection.py` to see the test pass where a lucky guess with flawed reasoning is caught and penalized.
5. **Inspect Teacher Cohort Heatmap:**
   Open `http://localhost:3000/teacher` or `curl http://localhost:8001/api/teacher/cohorts/class-10-a/summary`.
