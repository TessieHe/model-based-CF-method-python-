The cross-validation has been done on the original data set.
Please put ratings.csv, movies.csv, users.csv and toBeRated.csv in the code directory.
Instruction on how to run the code: 
1. user based: 
a) Jaccard similarity: recommender.py U J ratings.csv
b) Pearson similarity: recommender.py U P ratings.csv
c) Cosine similarity: recommender.py U C ratings.csv
2. item based:
a) Jaccard similarity: recommender.py I J ratings.csv
b) Pearson similarity: recommender.py I P ratings.csv
c) Cosine similarity: recommender.py I C ratings.csv
3. combine information of users and movies: 
    recommender.py users.csv movies.csv ratings.csv
4. To write the result csv file:
a) to get results1.csv with rating from user based and best similarity: 1 toBeRated.csv ratings.csv
b) to get results2.csv with rating from item based and best similarity: 2 toBeRated.csv ratings.csv
c) to get results3.csv with rating from combine method best similarity: 3 toBeRated.csv ratings.csv