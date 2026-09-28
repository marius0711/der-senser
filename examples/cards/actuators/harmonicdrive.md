---
tags: [gearbox, strain-wave]
---

# Strain wave gearing (Harmonic Drive)

## Q: What are the three components of a strain wave gear? ^ac-001
- **Wave generator**: elliptical cam with a thin, flexible ball bearing. Usually the **input**.
- **Flexspline**: thin-walled, flexible cup with external teeth. Usually the **output**.
- **Circular spline**: rigid ring with internal teeth. Usually **fixed** to the housing.

## Cloze: Gear ratio ^ac-002
The flexspline typically has {{2}} fewer teeth than the circular spline.
With the circular spline fixed, the ratio is i = Z_FS / (Z_CS − Z_FS).
A flexspline with 200 teeth therefore gives {{100:1}}, and the output turns in the {{opposite}} direction to the input.

## Q: Advantages and disadvantages of strain wave gears in robot joints? ^ac-003
**Advantages:** zero backlash, high ratio in a single stage (about 30–320:1), compact and light,
hollow shaft for cables, high positioning accuracy.

**Disadvantages:** limited and non-linear torsional stiffness (soft near zero load), fatigue of
the flexspline, lower efficiency at low temperatures, and **ratcheting** (tooth skipping) under overload.
