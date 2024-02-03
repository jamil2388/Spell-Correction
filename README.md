# Spell-Correction
This project involves calculating s@k for misspelled tokens in Birkbeck corpus and tokens in Wordnet with the aid of MED (Minimum Edit Distance)

# Dataset Details
Birkbeck 
Total number of correct words : 6136
Total misspelled words : 36133
Total number of words in the corpus : 42269

Wordnet
Total number of words (all correct) in the corpus : 147306

# Environment setup
python 3.10.xxxx recommended

```
pip install virtualenv
virtualenv venvs/spell_correction

# If Windows
venvs/spell_correction/Scripts/activate.bat
# else
source venvs/spell_correction/bin/activate

pip install -r requirements.txt

# run from the root folder 'Spell-Correction'
python -u assignment1.py
```

# Run Stats
| #Birkbeck Groups | #Wordnet Words | 1 CPU Core  | 4 CPU Cores | % Speed Boost | 8 CPU Cores | % Speed Boost | 
|------------------|----------------|-------------|------------| ------------- |-------------| ------------- |
| 500              | 100000         |  minutes    | 3.9606 minutes | 

# Results
For the entire dataset, the average s@k was calculated for k = 1, 5 and 10

Average s@k for k = 1 : <br>
Average s@k for k = 5 : <br>
Average s@k for k = 10 : <br>
