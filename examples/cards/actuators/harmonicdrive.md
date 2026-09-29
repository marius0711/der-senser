---
tags: [gearbox, strain-wave]
---

# Strain wave gearing (Harmonic Drive)

## Q: What are the three components of a strain wave gear? ^ac-001
DE: Aus welchen drei Bauteilen besteht ein Wellgetriebe (Harmonic Drive)?
- **Wave generator**: elliptical cam with a thin, flexible ball bearing. Usually the **input**.
- **Flexspline**: thin-walled, flexible cup with external teeth. Usually the **output**.
- **Circular spline**: rigid ring with internal teeth. Usually **fixed** to the housing.

## Cloze: Gear ratio ^ac-002
DE: Der Flexspline hat typischerweise {{2}} Zähne weniger als der Circular Spline. Bei festem Circular Spline gilt i = Z_FS / (Z_CS − Z_FS). Ein Flexspline mit 200 Zähnen ergibt also {{100:1}}, und der Abtrieb dreht {{entgegengesetzt}} zum Antrieb.
The flexspline typically has {{2}} fewer teeth than the circular spline.
With the circular spline fixed, the ratio is i = Z_FS / (Z_CS − Z_FS).
A flexspline with 200 teeth therefore gives {{100:1}}, and the output turns in the {{opposite}} direction to the input.

## Q: What are the pros and cons of strain wave gears in robot joints? ^ac-003
DE: Was sind Vor- und Nachteile von Wellgetrieben in Robotergelenken?
**Advantages:** zero backlash, high ratio in a single stage (about 30–320:1), compact and light,
hollow shaft for cables, high positioning accuracy.

**Disadvantages:** limited and non-linear torsional stiffness (soft near zero load), fatigue of
the flexspline, lower efficiency at low temperatures, and **ratcheting** (tooth skipping) under overload.
