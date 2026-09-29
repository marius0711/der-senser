---
tags: [force, strain-gauge]
---

# Force/torque sensing

## Q: How does a strain-gauge based force sensor work? ^se-001
DE: Wie funktioniert ein Kraftsensor auf Basis von Dehnungsmessstreifen (DMS)?
1. An **elastic body** deforms under load.
2. Bonded **strain gauges** change resistance: ΔR/R = k · ε (gauge factor k ≈ 2 for metal foil).
3. A **Wheatstone bridge** converts the small ΔR into a voltage. A full bridge also
   compensates for temperature effects.
4. An amplifier and ADC digitise the signal. Multi-axis sensors combine several bridges
   through a **calibration matrix**.

## Cloze: 6-axis F/T sensor ^se-002
DE: Ein 6-Achs-Kraft-Momenten-Sensor misst die Kräfte {{Fx, Fy, Fz}} und die Momente {{Mx, My, Mz}}. Die Brückensignale werden über eine {{Kalibriermatrix}} umgerechnet, die auch das {{Übersprechen}} zwischen den Achsen ausgleicht.
A 6-axis force/torque sensor measures the forces {{Fx, Fy, Fz}} and the torques {{Mx, My, Mz}}.
Raw bridge signals are converted into these values with a {{calibration matrix}}, which
also compensates for {{crosstalk}} between the axes.

## Term: Dehnungsmessstreifen (DMS) = strain gauge ^se-003
