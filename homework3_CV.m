clear;

% Use real data:
load ('movie_data');
user_mean = mean(train,2);
users = size(train,1);
% movies = size(train,2);
% train = train - repmat(user_mean,1,movies);
K = 2;
indices = crossvalind('Kfold',size(train,1)* size(train,2),K);

% Global SVD Test:
lowRank = [1, 3, 5];
testRMSE = zeros(1,size(lowRank, 2));
for i = 1:K
    testMatrix = train;rateMatrix = train;
    testIdx = (indices == i); trainIdx = ~testIdx;
    rateMatrix(testIdx == 1) = 0;testMatrix(trainIdx == 1)=0; 
%     size(testMatrix)
%     size(rateMatrix)
%     testMatrix = reshape(testMatrix,size(train,1),size(train,2));
%     rateMatrix = reshape(rateMatrix,size(train,1),size(train,2));
%     nnz(rateMatrix)
%     nnz(testMatrix)
    for l=1:size(lowRank, 2)
        [U, V] = myRecommender(rateMatrix, lowRank(l));
%         trainRMSE(l) = trainRMSE(l) + norm((U*V' - rateMatrix) .* (rateMatrix > 0), 'fro') / sqrt(nnz(rateMatrix > 0));
    %     multiply each element of A with its corresponding element of B by
    %     using the .*  --> observerd rating

    %     norm(A,'fro') returns the Frobenius norm of A.
    % rateMatrix > 0 --> ???entity??0??1?????0
        testRMSE(l) = testRMSE(l) + norm((U*V' - testMatrix) .* (testMatrix > 0), 'fro') / sqrt(nnz(testMatrix > 0));
        
    end
    fprintf('%d finished',i);
%     disp(testRMSE);
end
disp(testRMSE/K);