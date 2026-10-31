# Sakshi AI Hackathon: Adaptive Exam-Prep Tutor with a Learner Model

An adaptive, syllabus-grounded intelligent tutor designed for standardized exam preparation. Unlike generic AI wrappers that merely answer user queries in isolation, **Sakshi AI** maintains a latent **Bayesian Knowledge Tracing (BKT)** learner model, evaluates intermediate reasoning to uncover cognitive misconceptions, schedules exam-paced spaced reviews, and visualizes class-wide learning gaps on an interactive teacher heatmap.

---

## 🏆 Problem Statement & Technical Solution Matrix

| # | Competition Requirement | Technical Implementation | Exact File References |
|---|---|---|---|
| **1** | **Diagnostic Test** | 6-milestone adaptive diagnostic assessment that establishes initial baseline probability $P(L_0)$ across major curriculum clusters and propagates priors across the prerequisite graph. | `deeptutor/learning/diagnostic.py`<br>`deeptutor/api/routers/diagnostic.py`<br>`tests/learning/test_diagnostic_engine.py` |
| **2** | **Concept Graph (Class 10 Physics)** | Directed Acyclic Graph (DAG) for NCERT Class 10 Physics (Light, Electricity, Magnetism) with NetworkX cycle detection, topological ordering, and prerequisite gating. | `deeptutor/data/curriculum/class10_physics.json`<br>`deeptutor/learning/curriculum.py`<br>`tests/learning/test_curriculum_graph.py` |
| **3** | **Learner Model (BKT)** | Authentic 4-parameter Bayesian Knowledge Tracing updating latent understanding probability $P(L_t)$ deterministically after every response, bounded to $[0.0001, 0.9999]$. | `deeptutor/learning/bkt.py`<br>`deeptutor/learning/mastery.py`<br>`tests/learning/test_bkt_mastery.py` |
| **4** | **Targeted Question Generation + Difficulty Calibration** | Algorithm locating concepts in the student's Zone of Proximal Development (ZPD) and calibrating difficulty across 3 tiers (Conceptual $\to$ Application $\to$ Calculation). | `deeptutor/learning/question_generator.py`<br>`deeptutor/api/routers/adaptive_learning.py`<br>`tests/learning/test_targeted_generation.py` |
| **5** | **Reasoning-Based Misconception Detection** | Two-stage evaluation extracting step-by-step reasoning traces to catch underlying cognitive flaws—including lucky guesses where the final answer is right but the reasoning is invalid. | `deeptutor/learning/misconception.py`<br>`deeptutor/learning/grading.py`<br>`tests/learning/test_misconception_detection.py` |
| **6** | **Spaced-Repetition Scheduling** | Exponential retention half-life scheduler with **Exam Horizon Compression**, tightening review intervals as test day approaches to guarantee 100% syllabus coverage. | `deeptutor/learning/scheduler.py`<br>`deeptutor/learning/models.py`<br>`tests/learning/test_exam_paced_scheduler.py` |
| **7** | **Teacher Dashboard (Class-Wide Gaps)** | Interactive cohort analytics screen displaying a 2D student $\times$ concept mastery heatmap, ranked class-wide knowledge gaps, and frequent misconception tallies. | `web/app/(workspace)/teacher/page.tsx`<br>`deeptutor/api/routers/teacher.py`<br>`deeptutor/services/cohort/service.py` |

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

*Standard Parameter Set:*
- Prior Mastery: $P(L_0) = 0.20$
- Transition Rate: $P(T) = 0.15$
- Slip Probability: $P(S) = 0.10$
- Guess Probability: $P(G) = 0.20$
- Numerical bounds: $[0.0001, 0.9999]$

### 2. Difficulty Calibration & Zone of Proximal Development (ZPD)
The engine queries the curriculum DAG to compute the frontier of eligible concepts:
- **Prerequisite Mastery Gate:** Concepts with $P(L) \ge 0.70$ unlock downstream nodes.
- **Eligible Frontier:** Unmastered concepts ($P(L) < 0.75$) whose prerequisites are satisfied.
- **Difficulty Scaling:**
  - $P(L) < 0.40 \implies$ **Level 1 (Conceptual):** Qualitative definitions, core laws, intuition.
  - $0.40 \le P(L) < 0.70 \implies$ **Level 2 (Application):** Direct formula substitution, basic circuits/ray diagrams.
  - $P(L) \ge 0.70 \implies$ **Level 3 (Calculation):** Multi-step numericals, combined resistors, complex lens equations.

### 3. Exam-Paced Spaced Repetition Horizon
When a target exam date $t_{\text{exam}}$ is set, remaining days $\Delta_{\text{exam}} = (t_{\text{exam}} - t_{\text{now}}) / 86400$:
$$\kappa = \max\left(0.2, \frac{\Delta_{\text{exam}}}{14}\right)$$
$$\Delta t_{\text{review}} = \min\left(t_{\text{now}} + \kappa \cdot \Delta t_{\text{base}}, \, t_{\text{exam}} - 0.5 \times 86400\right)$$
Enforces review sessions to finish at least 12 hours prior to the exam.

---

## 🚀 Running Instructions & Verification

### 1. Prerequisites
- Linux / macOS
- Python 3.11+ (with virtual environment)
- Node.js 20+

### 2. Run the Full Automated Test Suite
Execute the test suites verifying all 7 requirements and end-to-end integration:

```bash
# Set PYTHONPATH to the repo root
export PYTHONPATH=/home/blank/sakshi-ai-hackathon

# Run backend unit and end-to-end integration test suites
PYTHONPATH=/home/blank/sakshi-ai-hackathon /home/blank/DeepTutor-git/.venv/bin/pytest \
    tests/integration/test_e2e_tutor_loop.py \
    tests/api/ \
    tests/learning/ \
    tests/test_pruned_runtime.py -v
```

### 3. Run Web / Frontend Unit Tests
```bash
cd web
npm test
```

### 4. Start the Full System

#### Start Backend (FastAPI)
```bash
# Start FastAPI backend server on port 8001
PYTHONPATH=/home/blank/sakshi-ai-hackathon /home/blank/DeepTutor-git/.venv/bin/uvicorn deeptutor.api.main:app --host 0.0.0.0 --port 8001
```

#### Start Frontend (Next.js)
```bash
cd web
npm run dev
```

Navigate to:
- Student Diagnostic Test: `http://localhost:3000/diagnostic`
- Teacher Cohort Analytics: `http://localhost:3000/teacher`
- Backend API Docs (Swagger): `http://localhost:8001/docs`

---

## 🔍 Judge Evaluation Walkthrough: The 5-Step Adaptive Loop

Our complete adaptive loop is validated by `tests/integration/test_e2e_tutor_loop.py`:

1. **Step 1: Diagnostic Assessment Establishes Baseline $P(L)$**
   ```bash
   curl -X POST http://localhost:8001/api/diagnostic/start \
        -H "Content-Type: application/json" \
        -d '{"syllabus": "class10_physics"}'
   ```
   Submitting milestone responses initializes the Bayesian Knowledge Tracing vector and propagates priors topologically across the curriculum DAG.

2. **Step 2: ZPD Question Selection Calibrates to Learner Frontier**
   ```bash
   curl -X POST http://localhost:8001/api/learning/next-question \
        -H "Content-Type: application/json" \
        -d '{"student_id": "std_1", "syllabus": "class10_physics"}'
   ```
   Selects the weakest concept in the eligible frontier (`c_electric_current`) calibrated to Level 1 Conceptual difficulty.

3. **Step 3: Reasoning-Based Misconception Detection**
   ```bash
   curl -X POST http://localhost:8001/api/learning/submit-answer \
        -H "Content-Type: application/json" \
        -d '{
          "student_id": "std_1",
          "question_id": "<question_id>",
          "answer": "Resistance doubles",
          "reasoning": "R = V / I so if V doubles R doubles"
        }'
   ```
   Unpacks the student's step-by-step reasoning trace, diagnosing cognitive misconception `ohm_r_depends_on_v` and returning targeted remedial feedback.

4. **Step 4: Deterministic BKT Mastery Update & Spaced Review**
   Mastery probability drops deterministically from $0.20 \to < 0.35$ and an exam-horizon review task is scheduled.

5. **Step 5: Teacher Dashboard Real-Time Gap Aggregation**
   ```bash
   curl -X GET http://localhost:8001/api/teacher/cohorts/class-10-a/summary
   curl -X GET http://localhost:8001/api/teacher/cohorts/class-10-a/heatmap
   ```
   The student's attempt immediately updates the cohort gap ranking and colors the 2D student $\times$ concept heatmap in the teacher dashboard.
