function [ class, centroid ] = mykmedoids( pixels, K )
%
% Your goal of this assignment is implementing your own K-medoids.
% Please refer to the instructions carefully, and we encourage you to
% consult with other resources about this algorithm on the web.
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
    datanum = size(pixels,1);    
    centroidid = randsample(size(pixels,1),K);
    centroid = pixels(centroidid,:);
    
    [class,cost] = knnsearch(centroid,pixels,'Distance','cityblock');
%     [class,cost] = knnsearch(centroid,pixels);
% poor initialization
%     [~,centroidid] = pdist2(pixels(randsample(size(pixels,1),1),:),pixels,'cityblock','Smallest',K);
%     centroid = pixels(centroidid,:);
    
    
    RSS = sum(cost);
    threshold = 1e-6;
    iter = 0;
    decreaseRate = threshold + 1;

    while (iter < 100 && decreaseRate > threshold)
        iter = iter + 1;
        preRSS = RSS;
        indicator = sparse(1:datanum,class,1,datanum,K,datanum);
        tempSum = sum(indicator,1);
        flag = [];
        for i = 1:K
            if tempSum(1,i) == 0
                flag(size(flag,2)+1) = i;
            end
        end
        indicator(:,flag) = [];
        K = size(indicator,2);
        centroid(flag,:) = [];
%            update centroid --> then class --> indicator --> RSS
        for i = 1:K
            subcluster_member = pixels(class == i,:);
            numMember = size(subcluster_member,1);
            curWithinDist =  sum(sum(abs(repmat(centroid(i,:),numMember,1)-subcluster_member)));
%             curWithinDist = sum(pdist2(centroid(i,:),subcluster_member,'cityblock'));
%             curWithinDist = sum(pdist2(centroid(i,:),subcluster_member));
            for j = 1:numMember
                tempWithinDist = sum(sum(abs(repmat(subcluster_member(j,:),numMember,1)-subcluster_member)));
%                 tempWithinDist = sum(pdist2(subcluster_member(j,:),subcluster_member,'cityblock'));
%                 tempWithinDist = sum(pdist2(subcluster_member(j,:),subcluster_member));
                if tempWithinDist < curWithinDist 
                    centroid(i,:) = subcluster_member(j,:);
                    curWithinDist =  tempWithinDist;
                end
            end
        end
        [class,cost] = knnsearch(centroid,pixels,'Distance','cityblock');
%         [class,cost] = knnsearch(centroid,pixels);
        RSS = sum(cost);
        
        decreaseRate = abs(RSS - preRSS)/preRSS;
    end
end