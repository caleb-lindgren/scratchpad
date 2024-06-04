1. What are cancer persister cells?
    1. Upon treatment with drug, a small population of cells survives
    2. These cells are slow-growing
    3. When drug is removed, they expand like normal cells, and then the majority die again upon retreatment
        - I.e., the resistance is reversible
    4. Under long-term drug treatment, they acquire permanent resistance mutations and expand even in the presence of drug
    - Examples
        - Sharma 2010 (NSCLC)
        - Hata 2016 (NSCLC)
        - Russo 2022 (CRC)
    - Questions
        - Persister vs. cancer stem cell: Persister is a transient state, not a consistent subpopulation
2. How are permanent resistance mutations acquired?
    1. Originally assumed to be replication-dependent
    2. However, replication-independent mutations are another possible source
        - Commonly seen in bacterial persisters, and several examples in human cancers seen too
            - Russo 2019: CRC; Drugs lead to more DNA damage, and induce error-prone repair
            - Cipponi 2020: Multiple cancers; Increased DNA damage under drug treatment, even under non-genotoxic drug; paired with increase mutation rate; linked to suppression of MTOR signalling
            - Isozaki 2023: NSCLC; Drugs induce APOBEC3A activity => more mutations
        - Russo 2021 (atavistic idea)
3. Hypothesis: Cancer persisters are more likely to gain permanent resistance mutations through replication-independent mechanisms than replication-dependent mechanisms
    - Plan to test: Model growth, and see what's within the range of realistic rates
4. General description of my model
    - Consider a population of persisters. At any given moment, a cell can:
        1. Divide
            1. If it divides too frequently, it will die
            2. If it divides, it could gain a replication-dependent permanent resistance mutation
        2. Gain a replication-independent mutation
        3. Once a mutation is gained, we assume that the growth advantage is great enough that its progeny quickly outnumber the rest of the cells
5. Gillespie algorithm simulation
    - dN/dt = Nr - Nrd - Nr * ud - ui
            = Nr(1 - d - ud) - ui
    - Units for each parameter:
        - N: cells
        - r: time ^ -1
        - d: unitless
        - ud: unitless
        - ui: cells / time
    - Deterministic solution:
        N = (N0r(1 - d - ud) - ui) / r(1 - d - ud) * e ^ tr(1 - d - ud) + ui / r(1 - d - ud)
6. Individual-based simulation
7. Conclusions

Whiteboard figures
1. S1, persister cell explanation
2. S2, permanent mutation acquisition mechanisms
3. S3, hypothesis
4. S4, model description
5. S5, Gillespie setup
