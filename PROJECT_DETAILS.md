# Project Details: Spell-Correction Evaluation

This document provides a comprehensive technical overview of the Spell-Correction project, which evaluates the effectiveness of Minimum Edit Distance (MED) for correcting spelling errors using the Birkbeck corpus and Wordnet.

## 1. Project Overview
The goal of this project is to measure the **Success at k (s@k)** metric for misspelled words. It identifies the top $k$ closest words from a reference dictionary (Wordnet) for each misspelled word in a test set (Birkbeck) and checks if the correct intended word is within those top $k$ suggestions.

## 2. Dataset Information

### 2.1 Birkbeck Corpus
- **Total Correct Words:** 6,136
- **Total Misspelled Words:** 36,134
- **Format:** The data is processed from a raw format where groups of misspelled words are preceded by their correct version (marked with a `$` prefix).

### 2.2 Wordnet
- **Total Vocabulary Size:** 147,306 words
- **Role:** Serves as the "gold standard" dictionary against which misspelled words are compared.

## 3. Core Algorithms & Logic

### 3.1 Minimum Edit Distance (MED)
- The project uses the **Levenshtein Distance** algorithm to calculate the similarity between strings.
- Implementation: Utilizes the `Levenshtein` Python library for high-performance distance calculation.

### 3.2 Success at k (s@k)
- **Definition:** The probability that the correct word is among the first $k$ suggestions.
- **k-values evaluated:** 1, 5, and 10.
- **Matching Logic:** A match is counted if the correct word from the Birkbeck corpus is found within the top $k$ Wordnet words (sorted by ascending Levenshtein distance).

## 4. Technical Implementation

### 4.1 Architecture
- **Language:** Python 3.10+
- **Parallelization:** 
    - Due to the massive search space (~5.3 billion pairs), the system uses Python's `multiprocessing` module.
    - The workload is split into chunks of misspelled words, which are processed in parallel across available CPU cores.
- **Caching System:** 
    - Uses `pickle` (`.pkl`) files to store processed data in a `cache/` directory.
    - Cached items include:
        - `cw.pkl`: Mapping of incorrect words to correct words.
        - `iw.pkl`: List of incorrect words.
        - `wordnet_index.pkl`: Indexed Wordnet vocabulary.
        - `iw_matrix.pkl`: The calculated top-k nearest words for every misspelled word.

### 4.2 Key Modules
- `assignment_1.py`: Main execution script for batch evaluation.
- `param.py`: Configuration and hyperparameters.
- `utils/functionals.py`: Core functional logic for data processing, parallelization, distance calculations, and length-indexed dictionary management.

## 5. Performance Benchmarks
Testing on a server with 40 CPU cores showed near-linear scaling for large datasets:

| Birkbeck Words | Wordnet Words | 1 CPU Core | 40 CPU Cores | Speedup |
|----------------|---------------|------------|--------------|---------|
| 5,000          | 100,000       | 10.40 min  | 0.55 min     | 94.71%  |
| 36,134         | 147,306       | Timeout    | 3.64 min     | ~100%   |

## 6. Current Results
For the full dataset, the average s@k values achieved are:
- **s@1:** 0.4250
- **s@5:** 0.4927
- **s@10:** 0.5011

## 7. How to Run
1. Activate virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure `param.py` (e.g., set `toy: 1` for a quick test run).
4. Execute: `python assignment_1.py`.

## 8. Real-time Spell Correction Optimization

### 8.1 Data Optimization (Milestone 2) - [COMPLETE]
To enable real-time performance, the linear search across the entire Wordnet corpus (147k words) is optimized using a length-indexed dictionary.

**Implemented Details:**
1.  **Grouped by Length:** Wordnet vocabulary is processed into a dictionary where each key is an integer representing the word length.
2.  **Caching Mechanism:** 
    - The indexed dictionary is stored as `cache/wordnet_by_length.pkl`.
    - Implemented lazy-loading via `get_wordnet_by_length()` to minimize overhead.
3.  **Search Scope Reduction:** Future correction logic will only consider words within the range of `[len(input) - 2, len(input) + 3]`.

### 8.2 Interactive Logic (Milestone 3 & 4)
- **Top-K Retrieval:** Suggestions are ranked by Levenshtein distance, and only the top $k$ (default 5 or 10) are returned.
- **Dynamic Input Handling:** The system will simulate "as-you-type" suggestions by responding to each incremental update of the user's input.
