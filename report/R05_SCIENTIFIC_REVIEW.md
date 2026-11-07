# R05 independent scientific and editorial review

## WHAT — problem and assumptions

The manuscript identifies the specific educational failure: encrypting the same integer with unpadded RSA, public exponent 3 and different pairwise-coprime moduli. Eve's inputs are public $(n_i,e,c_i)$ triples; private keys and the original integer are reserved for the builder/evaluator. The exact condition is $M^3<N_S$, not merely $M<N_S$. The text consistently distinguishes recovering integer 2 from recovering its original 96-byte leading-zero serialization.

## WHY — motivation and comparison

The same-key textbook/OAEP pairing gives a controlled reason to attribute the observed difference to the encryption scheme rather than changing RSA moduli. Prior work is bounded: the fixed-message CRT result is derived here, while Håstad is cited only for broader low-degree modular context. RFC 8017 supports implemented OAEP parameters and its size bound; NIST SP 800-38D supports GCM/AAD terminology. The introduction links the attack to defense and then to authenticated multi-recipient file sharing, rather than presenting disconnected demonstrations.

## HOW — implementation, evaluation and analysis

The CRT inverse construction and exact integer-root test demonstrate algorithmic understanding. The architecture figure marks the public-only attacker and independent evaluator, as well as the separate secure-sharing path. E1 covers 20 key sets × four messages × seven subsets; E2 has 60 paired comparisons within 20 blocks; E3 has nine configurations with 20 timing repetitions and separate recipient-key generation; E4 consists of 11 selected correctness cases. Results distinguish cryptographic encrypt+wrap time from JSON/Base64 serialization, and the structural package-size identity explains observed overhead without treating it as an independently fitted law.

## Evidence and limits

The source is the immutable official run official-20261106T083221Z-3bbf57cc, whose manifest identifies source commit 46c455819e4588736d4777c252d844fa03e7caf3. R05 does not rerun or alter experiments. E1's success indicator is evaluator-confirmed integer equality; E2's 0/60 OAEP recovery applies only to the tested attack; E3 timing describes one Windows computer and first-recipient decryption; E4 is deterministic case testing, not a sampled attack population. Public keys are assumed authenticated, metadata remains visible, and the system lacks sender authentication, replay protection, PKI and revocation. These boundaries remain explicit after compression.

## Editorial verdict and remaining human review

**Suitable for human academic review as an eight-page candidate.** The hierarchy and TOC make the short report easier to navigate, while the mathematical derivation, paired comparison, statistical decomposition and threat-model limits remain defensible. A lecturer should confirm the final course formatting rule. The seven student authors must approve the exact wording and take responsibility for the claims before submission. This review does not guarantee a grade or imply formal proof of system security.
