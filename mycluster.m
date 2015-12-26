function [ class ] = mycluster( bow, K )
n = size(bow,1);
words = size(bow,2);

%initialize prior probability for mixture component of topic c 
mix_component = ones(1,K)./K;

% mu = zeros(w,K);%the probablity of a word being Wj in topic c
r = zeros(n,K); %the expectation of document Di belonging to cluster c

%initialize the probablity of a word being Wj in topic c

%initialize as uniform distribution
mu = rand(words,K); 
mu = mu ./ repmat(sum(mu,1),[words,1]);

%initialize with equal probability
% mu = ones(words,K);
% mu = mu./words;


iter = 0;
maxIter = 500;
while iter < maxIter
%     old = log_like;
    iter = iter + 1;
    %e-step
    for doc = 1:n
        r(doc,:) = mix_component .* prod(mu.^(repmat(bow(doc,:),K,1)'),1);
        temp_sum = sum(r(doc,:));
        r(doc,:) = r(doc,:)/temp_sum;
    end
    
   % m-step
    mu = bow' * r;
    temp_sum = sum(mu,1);
    mu = mu ./ repmat(temp_sum,[words,1]);
   % update mixture component
    mix_component = sum(r,1)/n;
end
largest = 5;
top_words = zeros(K,largest);
for topic = 1:K
    [~,sortingIndices] = sort(mu(:,topic),'descend');
    top_words(topic,:) = sortingIndices(1:largest);
end
% disp(top_words);

% interpret to class
[~,class] = max(r,[],2);

end

