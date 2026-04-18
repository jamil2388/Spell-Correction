# Project Objective: Real-time Spell Correction

**Goal:** Transform the evaluator into an interactive program that provides the top *k* spelling suggestions for a word as it is typed, using length-based filtering to optimize search performance.

## Milestones

- [ ] **1. Project Setup & Documentation**
    - [x] Create `MILESTONES.md` to track progress.
    - [ ] Update `README.md` with the new project direction.

- [ ] **2. Data Optimization**
    - [ ] Pre-process Wordnet dictionary into a length-indexed dictionary (e.g., `{length: [words]}`) for faster filtering.
    - [ ] Implement a caching mechanism for the length-indexed dictionary.

- [ ] **3. Core Suggestion Logic**
    - [ ] Implement length-based filtering: Search only words within the range `[len(input) - 2, len(input) + 3]`.
    - [ ] Develop the `get_suggestions(word, k)` function using Levenshtein distance.
    - [ ] Optimize the distance calculation for single-word lookups.

- [ ] **4. Interactive Interface**
    - [ ] Create a CLI-based interactive loop for user input.
    - [ ] Implement "as-you-type" simulation (processing input string updates).
    - [ ] Format and display the Top-K suggestions clearly.

- [ ] **5. Testing & Refinement**
    - [ ] Verify suggestion accuracy against common misspellings.
    - [ ] Benchmark performance of the filtered search vs. full dictionary search.
    - [ ] Final code cleanup and documentation.
