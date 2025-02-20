from solver_q1 import overall_dervs_maxprob
def main():
    det_seq1 = ['AB', 'ABAB', 'ABABABAB']
    result_dist, result_derivation, final_prob = overall_dervs_maxprob(det_seq1)
    print(f"Info ragarding sequence: {det_seq1}")
    print("Best distribution:", result_dist)
    print("Best derivation:", result_derivation)
    print("Final probability:", final_prob)

    det_seq2 = ['AB', 'ABAC', 'ABACABCD']
    result_dist, result_derivation, final_prob = overall_dervs_maxprob(det_seq2)
    print(f"Info ragarding sequence: {det_seq2}")
    print("Best distribution:", result_dist)
    print("Best derivation:", result_derivation)
    print("Final probability:", final_prob)

    S0L_seq1 = ['AB', 'AB', 'ABB']
    result_dist, result_derivation, final_prob = overall_dervs_maxprob(S0L_seq1)
    print(f"Info ragarding sequence: {S0L_seq1}")
    print("Best distribution:", result_dist)
    print("Best derivation:", result_derivation)
    print("Final probability:", final_prob)

    S0L_seq2 = ['AB', 'ABAB', 'ABABABC']
    result_dist, result_derivation, final_prob = overall_dervs_maxprob(S0L_seq2 )
    print(f"Info ragarding sequence: {S0L_seq2}")
    print("Best distribution:", result_dist)
    print("Best derivation:", result_derivation)
    print("Final probability:", final_prob)

if __name__ == "__main__":
    main()