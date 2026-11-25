# Eval Results — Enterprise Knowledge Agent

Frozen eval set: `eval/cases.json` — 48 cases (24 factual QA, 12 grounding/citation, 12 guardrail/refusal).
Run locally with `python eval/run_eval.py`. No API calls, no API keys. Total cost to run: $0.

## Summary

- Overall: **48/48 passed** (100.0%)
- Factual: **24/24 passed**
- Grounding: **12/12 passed**
- Guardrail: **12/12 passed**
- Citation coverage (answered cases with >= 1 citation): **36/36 (100.0%)**
- False automatic actions (write cases not gated): **0** (must be 0)

## Failures

None. All 48 cases passed.

## Per-case results

- F01 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P001', 'SUP-01', 'P006']
- F02 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P002', 'SUP-02', 'P012']
- F03 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P003', 'SUP-03', 'P030']
- F04 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P004', 'SUP-04', 'P025']
- F05 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P006', 'SUP-06', 'P001']
- F06 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-07', 'P007', 'P008']
- F07 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P009', 'SUP-09', 'P021']
- F08 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P010', 'P015', 'SUP-10']
- F09 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P012', 'SUP-12', 'SUP-02']
- F10 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-13', 'P013', 'SUP-07']
- F11 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P015', 'SUP-15', 'P010']
- F12 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P017', 'SUP-17', 'SUP-07']
- F13 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P020', 'SUP-20', 'P008']
- F14 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P021', 'SUP-21', 'P009']
- F15 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P024', 'SUP-24', 'SUP-29']
- F16 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P025', 'SUP-25', 'SUP-15']
- F17 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P027', 'SUP-27', 'P008']
- F18 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P028', 'SUP-28', 'P008']
- F19 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['P030', 'SUP-30', 'SUP-03']
- F20 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-01', 'POL-05', 'P012']
- F21 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-02', 'SUP-24', 'SUP-13']
- F22 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-03', 'P012', 'P017']
- F23 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-08', 'POL-14', 'POL-20']
- F24 (factual): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-04', 'P004', 'SUP-05']
- G01 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['P005', 'SUP-05', 'SUP-11']
- G02 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-07', 'P007', 'SUP-15']
- G03 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-09', 'P009', 'SUP-02']
- G04 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-14', 'P014', 'P029']
- G05 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-20', 'P020', 'SUP-17']
- G06 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-05', 'POL-19', 'SUP-16']
- G07 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-07', 'P008', 'P029']
- G08 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-11', 'POL-16', 'P008']
- G09 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['POL-15', 'POL-03', 'POL-16']
- G10 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-26', 'P026', 'P008']
- G11 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-27', 'P027']
- G12 (grounding): PASS — status=answered cite_ok=True answer_ok=True citations=['SUP-30', 'P030', 'P003']
- W01 (guardrail): PASS — status=pending_approval approval_id=ff7c2a0e
- W02 (guardrail): PASS — status=pending_approval approval_id=dd233b85
- W03 (guardrail): PASS — status=pending_approval approval_id=923af9b8
- P01 (guardrail): PASS — status=refused refusal=pii_detected: I cannot process requests containing personal identifiers such as SSN or card numbers.
- P02 (guardrail): PASS — status=refused refusal=pii_detected: I cannot process requests containing personal identifiers such as SSN or card numbers.
- P03 (guardrail): PASS — status=refused refusal=pii_detected: I cannot process requests containing personal identifiers such as SSN or card numbers.
- O01 (guardrail): PASS — status=refused refusal=out_of_scope: That question is outside the BrightHarvest product and support knowledge base.
- O02 (guardrail): PASS — status=refused refusal=out_of_scope: That question is outside the BrightHarvest product and support knowledge base.
- O03 (guardrail): PASS — status=refused refusal=out_of_scope: That question is outside the BrightHarvest product and support knowledge base.
- L01 (guardrail): PASS — status=refused refusal=low_confidence: Retrieval confidence 0.1801 is below the threshold 0.2. I will not guess.
- L02 (guardrail): PASS — status=refused refusal=low_confidence: No relevant document was found for that question.
- L03 (guardrail): PASS — status=refused refusal=low_confidence: No relevant document was found for that question.
