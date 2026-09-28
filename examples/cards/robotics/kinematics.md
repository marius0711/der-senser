---
tags: [kinematics, performance]
---

# Robot basics

## Q: What is the difference between the repeatability and the accuracy of a robot? ^ro-001
- **Repeatability**: how closely the robot returns to the **same taught pose** (ISO 9283).
- **Accuracy**: how far the reached pose deviates from a **commanded** pose in Cartesian space.

For serial robots, repeatability is typically much better than absolute accuracy.
Accuracy can be improved by kinematic **calibration**.

## Cloze: Redundancy ^ro-002
A typical serial articulated arm has {{6}} degrees of freedom. A 7-axis arm is
{{kinematically redundant}}, so it can move its elbow without moving the tool
(**null-space** motion).

## Term: Traglast = payload ^ro-003
