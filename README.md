# Spell-Correction
This project involves calculating s@k for misspelled tokens in Birkbeck corpus and tokens in Wordnet with the aid of MED (Minimum Edit Distance)

# environment setup
# python 3.10.xxxx recommended
pip install virtualenv
virtualenv venvs/spell_correction
# if linux
source venvs/spell_correction/bin/activate
# else if Windows
venvs/spell_correction/Scripts/activate.bat
pip install -r requirements.txt

# run from the root folder 'Spell-Correction'
python -u assignment1.py

# run stats
| #Birkbeck Groups | #Wordnet Words | 1 CPU Core   | 4 CPU Cores | % Speed Boost | 8 CPU Cores | % Speed Boost | 
|------------------|----------------|--------------|-------------| ------------- |-------------| ------------- |
| 200              | 100000         | 2.49 minutes | 2.09 minutes | 

