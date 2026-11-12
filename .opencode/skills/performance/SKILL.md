---
name: Performance
description: Measure, profile, optimize, and re-measure a performance bottleneck.
---

# Performance

Measure before changing code.

## Procedure

1. Define the metric and the target.
2. Reproduce the workload.
3. Measure a baseline.
4. Profile to find the bottleneck.
5. Choose the smallest change that addresses the bottleneck.
6. Re-measure with the same workload.
7. Report the change and the variance.

## Rules

- Do not optimize without a measurement.
- Do not trade correctness for speed.
- Check database queries, network calls, allocations, and rendering.
- Keep benchmarks reproducible.
- Report noise and confidence.

## Output

Baseline, bottleneck, change, after, delta, and residual risk.
