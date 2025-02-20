
import numpy as np
from collections import Counter
from scipy.optimize import minimize
import random
from derivations import get_derivations

def solve_s0l(dict_list, init_guess=None):
    """
    Solve a stochastic 0L-system optimization (Theorem 5.1 style) for a given list of
    'derivation dictionaries'.

    Each dictionary in 'dict_list' maps (step_index, letter_index) -> (char, rewriting).
    We want to find a single set of probabilities x_{(char->rewrite)} that *maximizes*
    the sum of the product of probabilities across all dictionaries.

    If 'init_guess' is provided, it must match the total number of distinct
    (char, rewrite) pairs. Otherwise, we create a uniform guess (one distribution for each letter).

    Parameters
    ----------
    dict_list : list of dict
        Each dict represents a derivation, mapping e.g. (row, col) -> (char, rewriting_substring).
    init_guess : array-like or None, optional
        Initial guess for the probabilities. If None, a uniform guess is used.

    Returns
    -------
    tuple
        (success_flag, max_sum_of_products, final_distribution_dict, pairs_list)
        - success_flag : bool
            True if optimizer converged successfully, False otherwise.
        - max_sum_of_products : float or None
            The maximum sum-of-products found, or None if unsuccessful.
        - final_distribution_dict : dict or None
            A dictionary {(char, rewriting) : probability} if successful, else None.
        - pairs_list : list
            The sorted list of all unique (char, rewriting) pairs used for indexing.
    """
    # 1) Build frequency maps & collect all possible (char, rewriting) pairs
    freq_list = []  # freq_list[i] = Counter of (char, rewriting)->count in dict i
    all_pairs = set()  # global union of (char, rewriting)

    for derivation_dict in dict_list:
        fm = Counter(derivation_dict.values())  # count how many times each rewrite occurs
        freq_list.append(fm)
        all_pairs.update(fm.keys())

    # Convert the set of pairs into a stable, sorted list for indexing in arrays
    pairs_list = sorted(all_pairs)
    # Extract the set of letters and sort them
    unique_chars = sorted({p[0] for p in pairs_list})

    # 2) Build the initial guess array 'guess_arr' if none is provided
    if init_guess is None:
        # By default, fill the array with uniform probabilities per letter
        guess_arr = np.ones(len(pairs_list), dtype=float)
        for char in unique_chars:
            # Identify indices in pairs_list that correspond to 'char'
            indices_for_char = [i for i, pair in enumerate(pairs_list) if pair[0] == char]
            # Suppose letter 'char' can rewrite into k possibilities => each is 1/k
            k = len(indices_for_char)
            for idx in indices_for_char:
                guess_arr[idx] = 1.0 / k
    else:
        # Use user-supplied init_guess, ensuring correct length
        guess_arr = np.array(init_guess, dtype=float)
        if guess_arr.shape[0] != len(pairs_list):
            raise ValueError(
                "init_guess length ({}) does not match the number of pairs ({})".format(
                    guess_arr.shape[0], len(pairs_list)
                )
            )
        # Optionally normalize if the sum for a letter is near 0 or not 1
        for char in unique_chars:
            indices_for_char = [i for i, pair in enumerate(pairs_list) if pair[0] == char]
            sum_for_char = guess_arr[indices_for_char].sum()
            if sum_for_char > 1e-12:
                guess_arr[indices_for_char] /= sum_for_char
            else:
                # If sum was ~0, distribute uniformly among rewrites for this letter
                k = len(indices_for_char)
                for idx in indices_for_char:
                    guess_arr[idx] = 1.0 / k

    # Helper to map from array -> dict {(char, rewriting): prob}
    def array_to_dict(var_array):
        return {pairs_list[i]: var_array[i] for i in range(len(pairs_list))}

    # 3) Define the objective function: negative sum-of-products => minimize => maximize original
    def objective(var_array, freq_list_for_dicts):
        distribution = array_to_dict(var_array)
        total_sum = 0.0
        # for each derivation's frequency map:
        for freq_map in freq_list_for_dicts:
            # compute product( x_{(c->r)}^exponent ) for that derivation
            prod_val = 1.0
            for (c, r), exponent in freq_map.items():
                x_val = distribution[(c, r)]
                prod_val *= x_val ** exponent
            total_sum += prod_val
        return -total_sum  # negative for maximization

    # 4) Build constraints: for each char, sum of probabilities = 1
    def constraint_sum_for_char(var_array, char):
        distribution = array_to_dict(var_array)
        sum_for_char = 0.0
        for (c, rewriting), prob in distribution.items():
            if c == char:
                sum_for_char += prob
        return sum_for_char - 1.0

    constraints_list = []
    for char in unique_chars:
        constraints_list.append({
            'type': 'eq',
            'fun': constraint_sum_for_char,
            'args': (char,),
        })

    # 5) Probability must be between 0 and 1 for each pair
    bounds = [(0, 1)] * len(pairs_list)

    # 6) Solve the optimization problem using SLSQP
    res = minimize(
        fun=objective,
        x0=guess_arr,
        args=(freq_list,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints_list
    )

    # 7) Analyze result
    if res.success:
        max_sum_products = -res.fun  # revert to positive sum-of-products
        final_distribution = array_to_dict(res.x)
        return True, max_sum_products, final_distribution, pairs_list
    else:
        # If solver didn't converge, return a failure flag
        return False, None, None, pairs_list


def solve_with_restarts(dict_list, n_restarts=5):
    """
    Attempt multiple random or heuristic initial guesses for the S0L optimization,
    tracking the best local optimum found.

    For each guess:
      1) We group pairs by letter.
      2) We pick random values for each rewriting, then normalize them to sum=1.
      3) We call solve_s0l(...) with that guess.

    The best solution found across all restarts is returned.

    Parameters
    ----------
    dict_list : list of dict
        Each dict is a derivation, e.g. (step_i, letter_i)->(char, rewriting_substring).
    n_restarts : int
        The number of random initial guesses to try.

    Returns
    -------
    tuple
        (best_obj_value, best_solution_dict, best_pairs_list, success_count)
        - best_obj_value : float
            The highest sum-of-products found over all runs (or -inf if none).
        - best_solution_dict : dict or None
            The distribution { (char, rewriting) : prob } for the best solution.
        - best_pairs_list : list of (char, rewriting)
            The sorted pairs used for indexing. If no success, might be partial.
        - success_count : int
            How many runs converged successfully.
    """
    best_objective = -np.inf
    best_distribution = None
    best_pairs = None
    success_count = 0

    # First, run once with a uniform guess
    success, val, sol, pairs_list = solve_s0l(dict_list, init_guess=None)
    if success and val > best_objective:
        best_objective = val
        best_distribution = sol
        best_pairs = pairs_list
        success_count += 1

    # Build freq_list and pairs_list for the random guesses
    freq_list = []
    all_pairs = set()
    for d in dict_list:
        fm = Counter(d.values())
        freq_list.append(fm)
        all_pairs.update(fm.keys())

    # A global pairs list, used for random init
    pairs_list_global = sorted(all_pairs)
    unique_chars_global = sorted({p[0] for p in pairs_list_global})

    # Attempt n_restarts random initial guesses
    for _ in range(n_restarts):
        # Create a 0 array of length = number of pairs
        guess_arr = np.zeros(len(pairs_list_global), dtype=float)
        # For each letter, assign random values to its possible rewrites, then normalize
        for char in unique_chars_global:
            indices = [i for i, pair in enumerate(pairs_list_global) if pair[0] == char]
            rand_vals = np.random.random(len(indices))  # in [0,1)
            sum_rand = rand_vals.sum()

            # If sum is too close to zero, fallback to uniform
            if sum_rand < 1e-12:
                guess_for_char = np.full(len(indices), 1.0 / len(indices))
            else:
                guess_for_char = rand_vals / sum_rand

            # Insert into guess_arr
            for i, idx in enumerate(indices):
                guess_arr[idx] = guess_for_char[i]

        # Now solve from this random guess
        success, val, sol, global_pairs = solve_s0l(dict_list, init_guess=guess_arr)
        if success and val > best_objective:
            best_objective = val
            best_distribution = sol
            best_pairs = global_pairs
            success_count += 1

    # Return the best solution found among all attempts
    return best_objective, best_distribution, best_pairs, success_count
