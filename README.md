# Spell-Correction
This project involves calculating s@k for misspelled tokens in Birkbeck corpus and tokens in Wordnet with the aid of MED (Minimum Edit Distance)

# environment setup
pip install -e git+https://github.com/yeahwhat-mc/goslate#egg=goslate
pip install PyDictionary

# run stats
| #Birkbeck Groups | #Wordnet Words | Without Threading | Threading 4096 | % Speed Boost | Threading 16384 | % Speed Boost | 
|------------------|----------------| ----------------- |----------------| ------------- | --------------- | ------------- |
| 200              | 100000         | 2.49 minutes | 

