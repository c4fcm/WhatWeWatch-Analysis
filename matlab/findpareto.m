%
% Find the parameters of a discrete pareto distribution over [1,inf).
%
% Requires the follwoing supplementary files from "On Estimating the Exponent
% of Power-Law Frequency Distributions" (White et al. 2008).
%
% http://esapubs.org/Archive/ecol/E089/052/mle_pareto.m
% http://esapubs.org/Archive/ecol/E089/052/mle_discretepareto.m
%

exp_id = '1390097300.74'

% Load data
filename = strcat('../results/findstatistics/', exp_id, '/spread_span.csv');
data = csvread(filename, 1, 1);
spread = data(:,1);
span = data(:,2);

% Plot spread data
[f x] = hist(spread, 1:max(spread));
h = figure;
loglog(x, f/sum(f), 'o')
hold on;

% Fit and plot pareto
xx = linspace(1, max(spread), 10000);
shape = mle_discretepareto(spread);
loglog(xx, xx.^shape ./ zeta(-shape));
xlabel('Global Reach (nations)');
ylabel('Frequency');
title('Global Reach of Trending Videos');
legend('Observed', strcat('Best-fit Pareto (\lambda = ', num2str(shape), ')'));
grid on;

% Save figure
saveas(h, strcat('../results/findstatistics/', exp_id, '/spread.fig'));
saveas(h, strcat('../results/findstatistics/', exp_id, '/spread.eps'));

% Plot span data
[f x] = hist(span, 1:max(span));
h = figure;
loglog(x, f/sum(f), 'o')
hold on;

% Fit and plot pareto
xx = linspace(1, max(span), 10000);
shape = mle_discretepareto(span);
loglog(xx, xx.^shape ./ zeta(-shape));
xlabel('Lifespan (days)');
ylabel('Frequency');
title('Lifespan of Trending Videos');
legend('Observed', strcat('Best-fit Pareto (\lambda = ', num2str(shape), ')'));
grid on;

% Save figure
saveas(h, strcat('../results/findstatistics/', exp_id, '/span.fig'));
saveas(h, strcat('../results/findstatistics/', exp_id, '/span.eps'));
