
function prob = algorithm(q)

load sp500;

% plot and return the probability
n = size(price_move,1);
% parameter configuation setup
increase = (price_move == 1);
decrease = (price_move == -1);
%pi(1) for good label; pi(2) for bad label
pi = [0.2,0.8];
%transition probability matrix
a = [0.8,0.2;0.2,0.8];
b = [q,1-q;1-q,q];

% forward algorithm
alpha = zeros(2,n);
alpha(1,1) = pi(1) * (b(1,1) * increase(1) + b(1,2) * decrease(1));%good initialize
alpha(2,1) = pi(2) * (b(2,1) * increase(1) + b(2,2) * decrease(1));%bad initialize
for i = 2:n
    emission_good = b(1,1) * increase(i) + b(1,2) * decrease(i);
    emission_bad = b(2,1) * increase(i) + b(2,2) * decrease(i);
    alpha(1,i) = emission_good * (alpha(1,i-1) * a(1,1) + alpha(2,i-1) * a(2,1));
    alpha(2,i) = emission_bad * (alpha(2,i-1) * a(2,2) + alpha(1,i-1) * a(1,2));
end
prob_y = sum(alpha(:,n));
% backward algorithm
beta = zeros(2,n);
beta(:,n) = ones(2,1);
for i = n-1:-1:1
    emission_good = b(1,1) * increase(i + 1) + b(1,2) * decrease(i + 1);
    emission_bad = b(2,1) * increase(i + 1) + b(2,2) * decrease(i + 1);
    beta(1,i) = emission_good * a(1,1) * beta(1,i + 1) + emission_bad * beta(2,i + 1) * a(1,2);
    beta(2,i) = emission_good * a(2,1) * beta(1,i + 1) + emission_bad * beta(2,i + 1) * a(2,2);
end
label_sequence = alpha(1,:) .* beta(1,:)/prob_y;
% plot(label_sequence);
prob = alpha(1,39) * beta(1,39)/prob_y;
end
