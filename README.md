# Stochastic-0L-System-Inference
Implementation of stochastic 0L-system inference methods (Q1 &amp; Q2) from ‘Optimal L-Systems for Stochastic L-system Inference Problems’ (Lotfi &amp; McQuillan, 2025).

This repository provides an implementation of **stochastic 0L-system** inference methods,
inspired by the results of [Ali Lotfi and Ian McQuillan (2025)](https://arxiv.org/abs/2409.02259v2)
on **Optimal L-systems for Stochastic L-system Inference Problems**. Specifically,
we address two main questions:

1. **Q1**: Construct a stochastic L-system and a specific derivation that maximizes
   the probability of generating a given sequence (through a single best derivation).
2. **Q2**: Construct a stochastic L-system that globally maximizes the probability
   of generating the sequence (possibly summing over all derivations).

This code implements Theorem 4.1, Corollary 4.2 and Theorem 5.1 from the paper (and related results) using
[scipy’s SLSQP optimizer](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html).


---

## File Overview


- **derivations.py**  
  Contains the depth-first search (`_dfs_all_derivations`) and the public function
  `get_derivations(seq)`, which enumerate all ways characters in string i can map
  to substrings in string i+1.  The enumerations are returned as “derivation dictionaries.”

- **solver_q1.py**  
  Implements a function `overall_dervs_maxprob(seq)` for Question 1, finding
  *one single derivation* with maximum scaled probability.  It uses:
  - `get_derivations(seq)` (from `derivations.py`),
  - and utility functions in `utils.py` (like `constant_factor`, `optimal_scaled_probability_val`).

- **solver_q2.py**  
  Contains two main parts for Question 2:
  1. `solve_s0l(...)`: Builds the “sum of dictionary-wise products” objective, the constraints
     (“sum of probabilities = 1 per letter”), and calls `scipy.optimize.minimize`.
  2. `solve_with_restarts(...)`: Runs multiple random initial guesses for `solve_s0l(...)`
     to reduce the risk of getting stuck in a local optimum.

- **utils.py**  
  A grab-bag of smaller helper functions, e.g.
  - `constant_factor(seq)`: builds the reciprocal factor needed to finalize probabilities,
  - `get_prod_count(derivation)`: counts how often a production is used,
  - `non_constant_factor(derivation)`: product of a^a for each production’s count,
  - `optimal_scaled_probability_val(seq, derivation)`: the “non-constant” portion
    of probability for a single derivation.

- **q1_example.py**  
  A script that demonstrates *Question 1 usage*.  It calls `overall_dervs_maxprob` on
  various sequences and prints out the “best distribution,” “best derivation,” and
  final scaled probability.

- **q2_example.py**  
  Demonstrates *Question 2 usage*.  It:
  1. Uses `get_derivations(seq)` to form a list of derivation dictionaries,
  2. Calls `solve_with_restarts(...)` to do multiple SLSQP runs,
  3. Prints the best sum-of-products found and the distribution that achieves it.

- **requirements.txt**  
  Lists required Python packages:  

## Installation

1. **Clone** this repository or download the files.
2. **Create** (optional) and activate a virtual environment:
 ```bash
 python -m venv venv
 source venv/bin/activate   # Linux/Mac
 venv\Scripts\activate      # Windows
 pip install -r requirements.txt
```

## Installation
python q1_example.py
python q2_example.py

