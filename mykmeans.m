function [ class, centroid ] = mykmeans( pixels, K )
%
% Your goal of this assignment is implementing your own K-means.
%
% Input:
%     pixels: data set. Each row contains one data point. For image
%     dataset, it contains 3 columns, each column corresponding to Red,
%     Green, and Blue component.
%
%     K: the number of desired clusters. Too high value of K may result in
%     empty cluster error. Then, you need to reduce it.
%
% Output:
%     class: the class assignment of each data point in pixels. The
%     assignment should be 1, 2, 3, etc. For K = 5, for example, each cell
%     of class should be either 1, 2, 3, 4, or 5. The output should be a
%     column vector with size(pixels, 1) elements.
%
%     centroid: the location of K centroids in your result. With images,
%     each centroid corresponds to the representative color of each
%     cluster. The output should be a matrix with size(pixels, 1) rows and
%     3 columns. The range of values should be [0, 255].
%     
%
% You may run the following line, then you can see what should be done.
% For submission, you need to code your own implementation without using
% the kmeans matlab function directly. That is, you need to comment it out.

% 	[class, centroid] = kmeans(pixels, K);
    
    datanum = size(pixels,1);
    class = randi(K,datanum,1);
    threshold = 1e-9;
    iter = 0;
    decreaseRate = threshold + 1;
    indicator = sparse(1:datanum,class,1,datanum,K,datanum);
    tempSum = sum(indicator,1);
    flag = [];
%     delete empty cluster in order to handle large K value
    for j = 1:K
        if tempSum(1,j)==0
            flag(size(flag,2)+1) = j;
        end
    end
    tempSum(flag) = [];
    indicator(:,flag) = [];
    K = size(indicator,2);
    weight = spdiags(power(tempSum.',-1),0,K,K);
    centroid = weight * indicator.' * pixels;
    RSS = norm(indicator.' * pixels-centroid,2);
    [~,class] = max(bsxfun(@minus,pixels * centroid.',dot(centroid,centroid,2).'/2),[],2);
    
% use maximum iteration and decreasing rate together as termination condition
    while (iter < 100 && decreaseRate > threshold)
        iter = iter + 1;
        preRSS = RSS;
        indicator = sparse(1:datanum,class,1,datanum,K,datanum);
        tempSum = sum(indicator,1);
        flag = [];
        for j = 1:K
            if tempSum(1,j)==0
                flag(size(flag,2)+1) = j;
            end
        end
        tempSum(flag) = [];
        indicator(:,flag) = [];
        K = size(indicator,2);
        weight = spdiags(power(tempSum.',-1),0,K,K);
        centroid = weight * indicator.' * pixels;
        [~,class] = max(bsxfun(@minus,pixels * centroid.',dot(centroid,centroid,2).'/2),[],2);
        RSS = norm(indicator.' * pixels-centroid,2);
        decreaseRate = abs(RSS - preRSS)/preRSS;
    end
end

