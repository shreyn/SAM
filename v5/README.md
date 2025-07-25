# SAM v4 — Fast, Accurate, and Data-Driven AI Assistant

## Overview

SAM v4 addresses the key limitations of v3 by introducing a fast ML-based action classifier and comprehensive slot-filling logging. This version maintains the reliability of LLM-driven slot-filling while dramatically improving speed and setting up for future ML-based improvements.

---

## v3 Limitations and v4 Solutions

### Problem 1: Innaccurate Action Classification
**v3 Limitation:** Used cosine similarity over sentence embeddings for action selection, which was faster but lacked nuance detection (frequent incorrect classifications).

**v4 Solution:** Implemented a fast ML classifier (logistic regression) that:
- Runs in ~30ms 
- Achieves near-perfect accuracy on real usage
- Uses minimal training data (just 20-30 examples per action)

### Problem 2: Slow Slot-Filling
**v3 Limitation:** Used the large LLM for argument extraction, resulting in ~2000ms response times.

**v4 Attempts:**
1. **Smaller LLM (Phi):** Still too slow (~1500ms)
2. **BERT Model Training:** Failed due to data quality issues:
   - Is insanely brittle (need alot of diverse training data)
   - Required massive amounts of training data (manual data creation is impractical)
   - LLM-generated data was inconsistent and error-prone

**v4 Solution:** Comprehensive logging strategy for future ML training:
- Logs every slot-filling interaction (user prompt, action, LLM output)
- Captures my own real behavior and language patterns
- Maintains current LLM reliability while building dataset, with the goal of replacing the LLM eventually

---

### Data Flow
1. User input → ML intent classifier (simple vs. query vs. agent) → ML action classifier
2. Action selected → LLM slot-filling with logging
3. Missing args → Follow-up questions with logging
4. Action execution → Service integration

---

## Future Plans

### ML Slot-Filling (Future)
- Train slot-filling models on collected real data
- Achieve sub-100ms slot-filling while maintaining accuracy
- Gradual transition from LLM to ML-based extraction

---

## Files and Structure

```
v4/
├── brain/                 # Core logic and orchestration
├── commands/             # Action handlers and registry
├── data/                 # Logs and persistent data
├── models/               # Trained ML models
├── scripts/              # Training and testing scripts
├── services/             # External service integrations
├── utils/                # Utilities including logging
└── main.py              # Entry point
```

---

## Lessons Learned

1. **ML for Classification:** Small, focused ML models can dramatically outperform similarity-based approaches
2. **Data Quality Matters:** LLM-generated training data is unreliable
3. **Real Data is King:** Authentic user interactions provide the best training data
4. **Logging is Investment:** Comprehensive logging enables future improvements without disrupting current functionality

