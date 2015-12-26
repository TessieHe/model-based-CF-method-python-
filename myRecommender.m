function [ U, V ] = myRecommender( rateMatrix, lowRank )
    % Please type your name here:
    name = 'Mengying, Du';
    disp(name); % Do not delete this line.

    % Parameters
    maxIter = 1000; % Choose your own.
    learningRate = 0.00015; % Choose your own.
    regularizer = 0.15; % Choose your own.
    
    % Random initialization:
    [n1, n2] = size(rateMatrix);
    U = rand(n1, lowRank) / lowRank;
    V = rand(n2, lowRank) / lowRank;
    
    threshold = 1e-4;
    % Gradient Descent:
    iter = 0;
    pre_rmse = norm((U*V' - rateMatrix) .* (rateMatrix > 0), 'fro') / sqrt(nnz(rateMatrix > 0));
    while iter < maxIter
        iter = iter + 1;
        pre_U = U;
        pre_V = V;
        R = (rateMatrix-pre_U* pre_V') .* (rateMatrix > 0);
        U = pre_U + 2* learningRate * (R * pre_V - regularizer * pre_U);
        V = pre_V + 2 * learningRate * (R' * pre_U - regularizer * pre_V);
        rmse = norm((U*V' - rateMatrix) .* (rateMatrix > 0), 'fro') / sqrt(nnz(rateMatrix > 0));
        if abs(rmse-pre_rmse)/pre_rmse < threshold
            break
        end
        pre_rmse = rmse;
    end
    % IMPLEMENT YOUR CODE HERE.
end