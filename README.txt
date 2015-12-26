Instruction to run:
1. to get "result.csv" file: open command line in current directory and type in:
" Recommender.py ratings.csv toBeRated.csv dimensions learning_rate regularization", for example "Recommender.py ratings.csv toBeRated.csv 5 0.001,0.1"

2. to do cross validation: open command line in current directory and type in:
"Recommender_CV.py ratings.csv dimensions learning_rate regularization N_fold"

Notes:
1. The basic regularized MF has been implemented under the maximum iteration for stopping criteria.
2. The cross validation experiment MF has been implemented under the rmse stablibity of test set for stopping criteria.