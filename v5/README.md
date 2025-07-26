# SAM v5 — Current State and Improvements

# [NOTES FOR FUTURE README REWRITE]
- The main goal of v5 is to build a natural, fast, and robust **voice interface** for SAM.
- This includes:
  - Making the assistant's responses sound super natural and human-like.
  - Integrating TTS (Text-to-Speech) for voice output (already implemented).
  - Planning for STT (Speech-to-Text) for voice input (coming soon).
- All optimizations (slot-filling speed, hardcoded follow-ups, etc.) are in service of making the voice experience seamless and real-time.
- v5 is the "voice-first" version: everything is designed to make talking to SAM as smooth as possible.

# (End notes)

## Recent Changes and Rationale

### 1. **Slot-Filling Timing Analysis**
- Added detailed timing logs to measure time spent on LLM-based argument extraction (`extract_arguments`) and follow-up question generation (`generate_followup_question`).
- This helps identify bottlenecks and optimize the user experience by pinpointing where delays occur in the slot-filling process.

### 2. **Slot-Filling Inefficiency Analysis**
- Reviewed the slot-filling flow and found that LLM calls for follow-up questions are slow and unnecessary, as these questions are formulaic and can be templated.
- Identified that failed JSON parsing of LLM responses can lead to unnecessary follow-up questions and reduced efficiency.

### 3. **Hardcoded Follow-up Questions**
- Replaced LLM-based follow-up question generation with hardcoded, natural-sounding templates for each action/argument pair.
- This change eliminates LLM latency for follow-up questions, making the assistant more responsive and consistent.
- For arguments without a custom template, a generic but natural fallback is used.

### 4. **General Philosophy**
- Use LLMs only where their generative power is truly needed (e.g., argument extraction from complex user input).
- Use fast, deterministic logic (templates, regex, ML classifiers) for everything else to maximize speed and reliability.

## Next Steps
- Consider further reducing LLM reliance for argument extraction by using heuristics or lightweight models for common argument types.
- Continue to monitor timing logs to guide future optimizations.

---

**This README reflects the current state of SAM v5, focusing on speed, efficiency, and a pragmatic use of LLMs.**

