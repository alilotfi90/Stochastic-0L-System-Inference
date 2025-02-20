from derivations import get_derivations
def constant_factor(seq):
    """
    Compute a constant factor 1 / (∏ (count(c)^(count(c))) ) for the given sequence,
    plus a dictionary of how many times each character appears in all but the last string.

    Parameters
    ----------
    seq : list of str
        A list of strings forming a sequence, e.g. ['AB','ABA','ABABA','ABABAAABB'].

    Returns
    -------
    tuple
        (1/const_factor, seq_char_count)
        - 1/const_factor : float
            The reciprocal of the product ∏(count(c)^count(c)) for each character c.
        - seq_char_count : dict
            A dictionary mapping each character c -> total count of c in seq[:-1].
    """
    seq_char_count = {}

    # Count occurrences of each character in all strings except the last
    for s in seq[:-1]:
        for c in s:
            seq_char_count[c] = seq_char_count.get(c, 0) + 1

    # const_factor = ∏(count(c)^count(c))
    const_factor = 1
    for c in seq_char_count:
        count_c = seq_char_count[c]
        const_factor *= (count_c ** count_c)

    return (1 / const_factor), seq_char_count


def get_prod_count(derivation):
    """
    From a derivation mapping, count how many times each production (char, rewriting)
    occurs. For example, if derivation has multiple 'A'->'AB', that production's count
    is incremented accordingly.

    Parameters
    ----------
    derivation : dict
        Maps (step_index, char_index) -> (char, rewriting_substring).

    Returns
    -------
    dict
        production_count : {(char, rewriting_substring) : occurrence_count}
    """
    production_count = {}
    for key in derivation:
        production = derivation[key]  # e.g. ('A','AB')
        production_count[production] = production_count.get(production, 0) + 1

    return production_count


def non_constant_factor(derivation):
    """
    Compute ∏(count^count) across all productions used in the derivation.

    If a particular production (char, rewriting) appears 'a' times,
    we multiply the factor by (a^a).

    Parameters
    ----------
    derivation : dict
        The derivation mapping (step_index, char_index) -> (char, rewriting_substring).

    Returns
    -------
    float
        The product of a^a over all productions, where a is the frequency
        of that production in 'derivation'.
    """
    prod_count = get_prod_count(derivation)
    factor = 1

    for production in prod_count:
        a = prod_count[production]
        factor *= (a ** a)

    return factor


def optimal_scaled_probability_val(seq, derivation):
    """
    Compute a scaled probability for a single derivation, ignoring the
    constant factor from Theorem 4.1 (the factor that depends only on
    character frequencies). We only compute the 'non_constant_factor'
    part that depends on the production frequencies.

    Parameters
    ----------
    seq : list of str
        The input sequence of strings.
    derivation : dict
        A particular derivation mapping.

    Returns
    -------
    float
        The scaling factor for the probability (the 'non_constant_factor').
    """
    return non_constant_factor(derivation)