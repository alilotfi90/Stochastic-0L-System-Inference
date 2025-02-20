def _dfs_all_derivations(
    seq: list[str],
    string_index: int,
    char_index: int,
    last_used_in_t: int,
    current_mapping: dict,
    all_mappings: list
):
    """
    A depth-first search that enumerates ways to map each character of seq[string_index]
    onto consecutive substrings of seq[string_index + 1].

    Parameters
    ----------
    seq : list of str
        A sequence of strings, e.g. ['A', 'AB', 'ABBA'].
    string_index : int
        The index of the current string in 'seq' that we're processing.
    char_index : int
        The index of the current character in seq[string_index].
    last_used_in_t : int
        The end position in seq[string_index + 1] used so far, so we know
        where to start the next substring.
    current_mapping : dict
        A partial mapping (derivation) of the form:
        (string_index, char_index) -> (character, substring_of_next).
        This dictionary is updated as we explore possibilities.
    all_mappings : list
        A list that collects all fully-formed derivation dictionaries. Each
        time we complete a mapping for all characters, we append a copy here.

    Returns
    -------
    None
        The function populates 'all_mappings' with dictionary copies of
        all discovered derivations.
    """
    # If we've reached the last string in 'seq', then there's no "next" string
    # to map into. Record the current derivation and return.
    if string_index == len(seq) - 1:
        all_mappings.append(current_mapping.copy())
        return

    # If we've assigned all characters in seq[string_index],
    # move on to the next string in 'seq'.
    if char_index == len(seq[string_index]):
        # Move to the next string, reset char_index and last_used_in_t
        _dfs_all_derivations(seq, string_index + 1, 0, -1, current_mapping, all_mappings)
        return

    # For readability, define two references:
    s = seq[string_index]         # current string
    t = seq[string_index + 1]     # next string (from which we form substrings)

    # If we're at the *last character* in the current string 's',
    # we must take the *remainder* of 't' for that character.
    if char_index == len(s) - 1:
        current_mapping[(string_index, char_index)] = (
            s[char_index],
            t[last_used_in_t + 1 : ]  # from last_used_in_t+1 to end
        )
        # Now move to the next character, effectively triggering next string
        _dfs_all_derivations(
            seq,
            string_index,
            char_index + 1,
            len(s) - 1,
            current_mapping,
            all_mappings
        )
        return

    # Otherwise, we handle a "middle" character of s. We can try all possible
    # splits of 't' from (last_used_in_t + 1) to (len(t) - 1).
    for right_index in range(last_used_in_t + 1, len(t) - 1):
        # Assign the current character of 's' to the substring in 't'.
        current_mapping[(string_index, char_index)] = (
            s[char_index],
            t[last_used_in_t + 1 : right_index + 1]
        )

        # Recursively explore the next character of 's' with updated 'last_used_in_t'
        _dfs_all_derivations(
            seq,
            string_index,
            char_index + 1,
            right_index,
            current_mapping,
            all_mappings
        )


def get_derivations(seq: list[str]) -> list[dict]:
    """
    Enumerate all possible derivations (mappings) for a given sequence of strings,
    where each character in seq[i] is mapped to a consecutive substring in seq[i+1].

    Each derivation is represented as a dictionary:
        (string_index, char_index) -> (character, substring_in_next_string)

    Example:
    --------
    If seq = ['A', 'AB', 'ABBA'], then get_derivations(seq) returns all ways
    to map the single character in 'A' to a substring of 'AB', and subsequently
    map each character in 'AB' to substrings of 'ABBA', etc.

    Parameters
    ----------
    seq : list of str
        The sequence of strings, e.g. ['A','AB','ABBA'].

    Returns
    -------
    list of dict
        A list of derivation dictionaries, one for each possible mapping.
    """
    derivation_list = []  # will store all completed mappings

    _dfs_all_derivations(
        seq=seq,
        string_index=0,
        char_index=0,
        last_used_in_t=-1,
        current_mapping={},
        all_mappings=derivation_list
    )

    return derivation_list


def print_derivations(seq: list[str]):
    """
    Print all derivations (mappings) for the given sequence of strings.

    Parameters
    ----------
    seq : list of str
        The sequence to derive.
    """
    all_maps = get_derivations(seq)
    for m in all_maps:
        print(m)


# Example usage:
if __name__ == "__main__":
    example_seq = ["A", "AB", "ABBA"]
    print_derivations(example_seq)
