---
tags: [servo, fieldbus]
---

# Servo control and fieldbus

## Cloze: Cascaded servo control ^co-001
A servo drive typically uses three nested loops: the inner {{current (torque)}} loop,
the middle {{velocity}} loop and the outer {{position}} loop. Each inner loop must be
significantly {{faster}} than the loop around it.

## Q: Why is EtherCAT popular for multi-axis robots? ^co-002
- **Processing on the fly**: a single frame passes through all nodes, and each node reads and
  inserts its data as the frame passes, without store-and-forward.
- Cycle times **below 100 µs** are possible.
- **Distributed clocks** synchronise the nodes to well below 1 µs.
- Works with standard Ethernet hardware in a line topology, which suits the chain of joints in an arm.

## Term: Regelkreis = control loop ^co-003
