---
tags: [position, encoder]
---

# Encoders

## Q: Incremental vs. absolute encoder: what is the difference? ^se-010
- **Incremental**: outputs pulses on channels A/B with a 90° phase shift (quadrature gives
  the direction), plus an index pulse Z. Position is lost on power-off, so **homing** is required.
- **Absolute**: every position has a unique code (e.g. Gray code), so the position is known
  immediately at power-on. **Multi-turn** versions also count revolutions (gear, battery or Wiegand wire).

Robot joints typically use absolute encoders so the robot does not have to re-home after power-up.

## Cloze: Quadrature resolution ^se-011
Evaluating all edges of both channels (4x evaluation) gives {{4}} counts per line.
A 2,500-line encoder therefore provides {{10,000}} counts per revolution.
