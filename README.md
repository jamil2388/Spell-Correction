# Spell-Correction
This project involves calculating s@k for misspelled tokens in Birkbeck corpus and tokens in Wordnet with the aid of MED (Minimum Edit Distance)

# Dataset Details
Birkbeck <br>
Total number of correct words : 6136 <br>
Total misspelled words : 36134 <br>
<br>
Wordnet <br>
Total number of words (all correct) in the corpus : 147306 <br>

# Environment setup
python 3.10 recommended <br>
Use the following commands to setup the environment <br>

```
pip install virtualenv
virtualenv venvs/spell_correction

# If Windows
venvs/spell_correction/Scripts/activate.bat
# else
source venvs/spell_correction/bin/activate

pip install -r requirements.txt

# [OPTIONAL] change any desired setting in param.py for a modified run

# run from the root folder 'Spell-Correction'
python -u assignment1.py
```
# Parallelization

1. The primary step includes calculating the Levenshtein Distance for each pair of incorrect word in Birkbeck and a correct word in Wordnet
2. Because each step of calculation of a single instance of Levenshtein distance depends on three other dependent steps, the parallelization is complicated or quite impossible. 
3. Moreover, considering step 2 as parallelized, we are left with calculating distance calculation for 36134 * 147306 pairs (!) This is at the same time space and time intensive
4. So, instead of trying to parallelize step 2, we parallelize step 3 in this code
5. We build a matrix (iw_matrix) by stacking up chunks of rows from multiple processes
6. Each row i consists of a list of tuple (j, d) where j is the index of the correct wordnet word and d is the distance between i-th incorrect word from Birkbeck and j-th correct word from Wordnet
7. We reduce the size of the iw_matrix by sorting the tuples in i-th row in ascending order and keeping only the k lowest columns (k = 10)
8. The total number of rows processed in Step 5-7 are distributed to max 40 cores of cpu in a server
9. The result of the multiprocessing Step 8 are collected and concatenated to produce the final sorted matrix. This matrix contains the indices of the k nearest words from Wordnet corpus for each incorrect word in Birkbeck
10. The matrix, Birkbeck and Wordnet corpora can be saved in the 'cache/' folder for faster loading in the later runs
11. s_at_k for 1, 5 and 10 for each incorrect word in Birkbeck are calculated by looking up into the iw_matrix and then the results are averaged accordingly

# Run time Stats
The stats of the total program runtime with and without multiprocessing are shown in the table : 

| #Birkbeck Incorrect Words | #Wordnet Correct Words | 1 CPU Core      | 40 CPU Cores | % Speed Boost | 
|---------------------------|------------------------|-----------------|--------------|---------------|
| 200                       | 100000                 | 0.4641 minutes  | 0.0734 minutes | 84.18%        |
| 500                       | 100000                 | 1.0256 minutes  | 0.0953 minutes | 90.70%        |
| 5000                      | 100000                 | 10.3997 minutes | 0.5503 minutes | 94.71%        |
| 36134                     | 147306                 | Process killed  | 3.6430 minutes | ~100%         |

# Results
For the entire dataset, the average s@k was calculated for k = 1, 5 and 10 <br>
<br>
Average s@k for k = 1 : 0.4250013837383074 <br>
Average s@k for k = 5 : 0.4926661869707201 <br>
Average s@k for k = 10 : 0.5010516411136325 <br>
