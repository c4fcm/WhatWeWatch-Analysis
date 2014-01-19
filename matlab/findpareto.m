%
% Find the parameters of a discrete pareto distribution over [1,inf).
%
% Requires the follwoing supplementary files from "On Estimating the Exponent
% of Power-Law Frequency Distributions" (White et al. 2008).
%
% http://esapubs.org/Archive/ecol/E089/052/mle_pareto.m
% http://esapubs.org/Archive/ecol/E089/052/mle_discretepareto.m
%

exp_id = '1390159603.95'

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
strcat('Global Reach Pareto shape: ', num2str(shape))
loglog(xx, xx.^shape ./ zeta(-shape));
hx = xlabel('Global Reach (nations)');
hy = ylabel('Frequency');
ht = title('Global Reach of Trending Videos');
hl = legend('Observed', strcat('ML Pareto'));
grid on;
set(h, 'Units', 'inches')
set(h, 'OuterPosition', [0 0 9.375 7.03125])
set(h, 'PaperPosition', [0 0 3.125 2.34375])
set(hl, 'FontSize', 7)
set(ht, 'FontSize', 10)
set(hx, 'FontSize', 10)
set(hy, 'FontSize', 10)
set(gca, 'FontSize', 6)
set(gca, 'XTick', [1 10])
set(gca, 'YTick', [0.00001 0.0001 0.001 0.01 0.1 1])
axis([1 60 0.00001 1])

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
strcat('Lifespan Pareto shape: ', num2str(shape))
loglog(xx, xx.^shape ./ zeta(-shape));
hx = xlabel('Lifespan (days)');
hy = ylabel('Frequency');
ht = title('Lifespan of Trending Videos');
hl = legend('Observed', strcat('ML Pareto'));
grid on;
set(h, 'Units', 'inches')
set(h, 'OuterPosition', [0 0 9.375 7.03125])
set(h, 'PaperPosition', [0 0 3.125 2.34375])
set(hl, 'FontSize', 7)
set(ht, 'FontSize', 10)
set(hx, 'FontSize', 10)
set(hy, 'FontSize', 10)
set(gca, 'FontSize', 6)
set(gca, 'XTick', [1 10 100])
set(gca, 'YTick', [0.00001 0.0001 0.001 0.01 0.1 1])
axis([1 200 0.00001 1])

% Save figure
saveas(h, strcat('../results/findstatistics/', exp_id, '/span.fig'));
saveas(h, strcat('../results/findstatistics/', exp_id, '/span.eps'));
