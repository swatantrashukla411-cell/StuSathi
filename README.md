# CampusPilot AI — Voice-First Personal Academic Agent

> A production-grade, voice-first academic co-pilot for college students.  
> Combines real-time voice orchestration, deterministic academic calculators, timetable intelligence, and calibrated machine learning.

---

## 🎯 Architecture Philosophy

```
[ User Voice / Text ]
         │
         ▼
[ Gemini 1.5 Flash / Live Agent ]  ── (Extracts parameters & intent)
         │
         ▼
[ Deterministic Domain Engine ]    ── (Zero LLM math. 100% verified Python formulas)
         │
         ▼
[ Verified JSON Result ]          ── (LLM translates to natural conversational Hinglish/English)
         │
         ▼
[ Real-Time Voice Audio Stream + UI Dashboard ]
```

### Why we do NOT let AI do arithmetic:
Large Language Models (LLMs) are probabilistic text prediction engines. They do not have built-in arithmetic verifiers and frequently hallucinate fractional percentages or miscalculate graduation credit weights. 
In **CampusPilot AI**, the AI acts purely as an **Orchestrator** — it decides *which* tool to call, and our validated Python domain services execute the exact formulas.

---

## 📐 Mathematical Models

### 1. Attendance Engine
Let:
- $A$ = classes attended so far
- $T$ = classes conducted so far
- $R$ = remaining planned sessions in semester
- $p$ = required institutional threshold (e.g. $0.75$ for 75%)

* **Maximum Future Absences Allowed:**
  $$\text{Max Absences} = \max\left(0, \min\left(R, \left\lfloor A + R - p \cdot (T + R) \right\rfloor\right)\right)$$
* **What-If Absence Simulation:**
  $$\text{Projected Attendance} = \frac{A + R - y}{T + R} \times 100$$
* **Attendance Recovery Target (consecutive classes needed):**
  $$k = \left\lceil \frac{p \cdot T - A}{1 - p} \right\rceil$$

### 2. Credit-Weighted GPA Engine
* **Semester SGPA:**
  $$\text{SGPA} = \frac{\sum (\text{credits}_i \times \text{grade\_points}_i)}{\sum \text{credits}_i}$$
* **Target CGPA Solver:**
  To reach target CGPA $G$ with completed credits $E_c$ and remaining credits $E_r$:
  $$S_{\text{future}} = \frac{G \cdot (E_c + E_r) - C \cdot E_c}{E_r}$$
  If $S_{\text{future}} > 10.0$, the engine detects mathematical infeasibility and computes the maximum attainable ceiling.

---

## 🚀 Running Tests

Activate virtual environment and execute tests:
```bash
# Windows
.venv\Scripts\pytest -v tests --cov=apps/api/src
```
