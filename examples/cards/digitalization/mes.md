---
tags: [mes, isa95]
---

# Manufacturing IT

## Q: Where does an MES sit in the ISA-95 model, and what does it do? ^di-001
DE: Wo steht ein MES im ISA-95-Modell, und welche Aufgaben hat es?
**Level 3**: between ERP (level 4) and control systems such as PLCs and SCADA (levels 1–2).

Typical functions: order dispatching, production tracking and **traceability**, machine and
process data collection, quality data, performance monitoring (OEE), digital work instructions.

## Q: Batch vs. serial traceability: what is the difference? ^di-002
DE: Was ist der Unterschied zwischen chargenbezogener und seriennummernbezogener Rückverfolgbarkeit?
- **Batch (lot) traceability**: components are traced per lot, e.g. "all screws from lot 4711".
  It is cheaper, but a recall affects every unit that used the lot.
- **Serial traceability**: each unit or component has its own serial number and history,
  e.g. which tightening curve, which test result, which operator. It allows targeted recalls
  and root-cause analysis.

## Term: Rückverfolgbarkeit = traceability ^di-003
