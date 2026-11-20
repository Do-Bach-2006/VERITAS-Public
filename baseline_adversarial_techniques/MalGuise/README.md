# MalGuise Baseline Reproduction

Paper: *A Wolf in Sheep's Clothing: Practical Black-Box Adversarial Attacks for Evading Learning-Based Windows Malware Detection in the Wild* (USENIX Security 2024)

This directory contains the reproduction of the **MalGuise** black-box adversarial malware generation framework:
- **Search Strategy**: Non-parametric Monte Carlo Tree Search (MCTS) with UCT exploration ($C = 40$ simulation budget, maximum sequence depth $6$).
- **Transformation Space**: Semantics-preserving code and control-flow graph (CFG) perturbations (`CFG_EDGE_REDIVIDE` call-based redividing and `SEMANTIC_NOP_INJECT` semantic NOP insertion).
- **Surrogate Detector**: Attributed Control Flow Graph (ACFG) deep graph neural network (**MAGIC**).

See [`how-to-run.md`](how-to-run.md) for environment setup, dataset verification, and batch evaluation instructions.
