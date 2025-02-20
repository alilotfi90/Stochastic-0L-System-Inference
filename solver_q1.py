from derivations import get_derivations
from utils import optimal_scaled_probability_val
from utils import get_prod_count
from utils import constant_factor

def overall_dervs_maxprob(seq):
    """
    Among all possible derivations for 'seq', find the one with the highest scaled probability
    (non_constant_factor). Then compute an adjusted probability distribution for each production
    that matches Theorem 4.1 / Theorem 5.1 logic.

    Steps:
    1. Gather all derivations of seq (via get_derivation_list).
    2. For each derivation, compute 'optimal_scaled_probability_val'.
    3. Identify the derivation with the largest scaled probability.
    4. Compute the final distribution (production -> freq / char_count).
    5. Multiply that best scaled probability by the constant factor, returning the final
       recommended probability measure and best derivation.

    Parameters
    ----------
    seq : list of str
        The sequence of strings, e.g. ['AB','ABA','ABABA','ABABAAABB'].

    Returns
    -------
    tuple
        (best_derv_distribution, best_derivation, final_probability)
        where:
        - best_derv_distribution : dict
            Maps (char, rewriting_substring) -> production_probability
        - best_derivation : dict
            The actual derivation dictionary that gave the maximum scaled probability
        - final_probability : float
            The scaled probability multiplied by the constant factor
    """
    # 1) Get all derivations for the sequence.
    derivation_list = get_derivations(seq)  # This must be defined somewhere.

    # 2) Calculate the scaled probability for each derivation
    scaled_probs = [optimal_scaled_probability_val(seq, d) for d in derivation_list]

    # 3) Identify the derivation with the largest scaled probability
    max_prob = max(scaled_probs)
    max_index = scaled_probs.index(max_prob)
    best_derivation = derivation_list[max_index]

    # 4) Build a distribution for each production in 'best_derivation'
    #    freq_of_production / total_char_occurrences
    production_count = get_prod_count(best_derivation)
    const_factor, seq_char_count = constant_factor(seq)

    best_derv_distribution = {}
    for prod, freq in production_count.items():
        # 'prod' is (char, rewriting), so prod[0] is 'char'.
        char = prod[0]
        char_count = seq_char_count[char]  # how many times 'char' appears in seq[:-1]
        best_derv_distribution[prod] = freq / char_count

    # 5) final_probability = scaled probability * const_factor
    final_probability = max_prob * const_factor

    return best_derv_distribution, best_derivation, final_probability


# Example usage:
if __name__ == "__main__":
    # Suppose we have 'get_derivation_list' already defined
    seq = ['AB', 'ABAB', 'ABABABAB']
    result_dist, result_derivation, final_prob = overall_dervs_maxprob(seq)
    print("Best distribution:", result_dist)
    print("Best derivation:", result_derivation)
    print("Final probability:", final_prob)
