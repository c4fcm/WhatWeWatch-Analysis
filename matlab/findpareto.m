%
% Find the parameters of a discrete pareto distribution over [1,inf).
%
% Requires the follwoing supplementary files from "On Estimating the Exponent
% of Power-Law Frequency Distributions" (White et al. 2008).
%
% http://esapubs.org/Archive/ecol/E089/052/mle_pareto.m
% http://esapubs.org/Archive/ecol/E089/052/mle_discretepareto.m
%

exp_id = '2014-07-16 13:18:16'

% Load data
filename = strcat('../results/findstatistics/', exp_id, '/spread_span.csv');
data = csvread(filename, 1, 1);
spread = data(:,1);
span = data(:,2);

% Plot spread data
[f x] = hist(spread, 1:max(spread));
h = figure
subplot(1,2,1);
loglog(x, f/sum(f), 'o', 'MarkerSize', 2)
hold on;

% Fit and plot pareto
xx = linspace(1, max(spread), 10000);
shape = mle_discretepareto(spread);
strcat('Global Reach Pareto shape: ', num2str(shape))
loglog(xx, xx.^shape ./ zeta(-shape));
grid on;
set(gca, 'XTick', [1 10])
set(gca, 'YTick', [0.00001 0.0001 0.001 0.01 0.1 1])
axis([1 60 0.00001 1])
hx = xlabel('Global Reach (nations)');
hy = ylabel('Frequency');
ht = title('Global Reach of Trending Videos');
set(ht, 'FontSize', 6)
set(hx, 'FontSize', 6)
set(hy, 'FontSize', 6)
set(gca, 'FontSize', 5)
%hl = legend('Observed', strcat('ML Pareto'));
%set(hl, 'FontSize', 4)

% Plot span data
[f x] = hist(span, 1:max(span));
subplot(1,2,2);
loglog(x, f/sum(f), 'o', 'Markersize', 2)
hold on;

% Fit and plot pareto
xx = linspace(1, max(span), 10000);
shape = mle_discretepareto(span);
strcat('Lifespan Pareto shape: ', num2str(shape))
loglog(xx, xx.^shape ./ zeta(-shape));
grid on;
set(gca, 'XTick', [1 10 100])
set(gca, 'YTick', [0.00001 0.0001 0.001 0.01 0.1 1])
axis([1 31 0.00001 1])
hx = xlabel('Lifespan (days)');
hy = ylabel('Frequency');
ht = title('Lifespan of Trending Videos');
set(ht, 'FontSize', 6)
set(hx, 'FontSize', 6)
set(hy, 'FontSize', 6)
set(gca, 'FontSize', 5)
%hl = legend('Observed', strcat('ML Pareto'));
%set(hl, 'FontSize', 4)

% Save figure
%set(h, 'Units', 'pixels')
%set(h, 'OuterPosition', [0 0 781 325])
%set(h, 'PaperSize', [3.3 1.4])
set(h, 'PaperPosition', [0 0 3.7 1.5])
saveas(h, strcat('../results/findstatistics/', exp_id, '/spread-span.fig'));
saveas(h, strcat('../results/findstatistics/', exp_id, '/spread-span.eps'));
