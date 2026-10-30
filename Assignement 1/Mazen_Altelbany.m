% Communication Theory - Assignment 1
% Group Members: 
%   1. Mazen Altelbany (64-12371)
%   2. Suhad Eyhab Rasheed (64-31506)
%   3. Sama Ismael Ahel (64-19880)

clear;
clc;
close all;

% Max digit across IDs is 9 -> range [-9, 9]
a = 9; 
N = 10000;
rng(42);

% Generate uniform signal
x = -a + 2 * a * rand(N, 1);
P_sig = mean(x.^2);

levels = [2, 4, 8];
numCases = length(levels);

mae_u = zeros(1, numCases);
mae_k = zeros(1, numCases);
var_u = zeros(1, numCases);
var_k = zeros(1, numCases);
var_th = zeros(1, numCases);
sqnr_u = zeros(1, numCases);
sqnr_k = zeros(1, numCases);
sqnr_th = zeros(1, numCases);

for i = 1:numCases
    L = levels(i);
    delta = (2 * a) / L;
    
    % Uniform Quantizer
    levels_u = -a + ((1:L) - 0.5) * delta;
    idx_u = floor((x - (-a)) / delta) + 1;
    idx_u(idx_u > L) = L;
    idx_u(idx_u < 1) = 1;
    x_q_u = levels_u(idx_u);
    x_q_u = x_q_u(:);
    
    % K-means Quantizer
    [idx_k, centers_k] = kmeans(x, L, 'Replicates', 3);
    x_q_k = centers_k(idx_k);
    
    % Task 1: First 6 elements
    fprintf('\n--- L = %d ---\n', L);
    disp('First 6 original samples:');
    disp(x(1:6)');
    disp('First 6 Uniform quantized:');
    disp(x_q_u(1:6)');
    disp('First 6 K-means quantized:');
    disp(x_q_k(1:6)');
    
    % Quantization error
    e_u = x - x_q_u;
    e_k = x - x_q_k;
    
    % Task 2: MAE
    mae_u(i) = mean(abs(e_u));
    mae_k(i) = mean(abs(e_k));
    fprintf('MAE -> Uniform: %.4f | K-means: %.4f\n', mae_u(i), mae_k(i));
    
    % Task 3: Variance
    var_u(i) = var(e_u);
    var_k(i) = var(e_k);
    var_th(i) = (delta^2) / 12;
    fprintf('Variance -> Uniform: %.4f | K-means: %.4f | Theory: %.4f\n', var_u(i), var_k(i), var_th(i));
    
    % Task 4: SQNR
    sqnr_u(i) = 10 * log10(P_sig / mean(e_u.^2));
    sqnr_k(i) = 10 * log10(P_sig / mean(e_k.^2));
    sqnr_th(i) = 20 * log10(L);
    fprintf('SQNR (dB) -> Uniform: %.2f | K-means: %.2f | Theory: %.2f\n', sqnr_u(i), sqnr_k(i), sqnr_th(i));
end

% Figures
figure(1);
plot(levels, mae_u, '-o', levels, mae_k, '--s', 'LineWidth', 1.5);
grid on;
xlabel('Number of Levels (L)');
ylabel('MAE');
title('Mean Absolute Error vs Levels');
legend('Uniform', 'K-means');
xticks(levels);
saveas(gcf, 'task2_mae_vs_levels.png');

figure(2);
plot(levels, var_u, '-o', levels, var_k, '--s', levels, var_th, ':d', 'LineWidth', 1.5);
grid on;
xlabel('Number of Levels (L)');
ylabel('Variance');
title('Quantization Error Variance vs Levels');
legend('Uniform', 'K-means', 'Theory');
xticks(levels);
saveas(gcf, 'task3_variance_vs_levels.png');

figure(3);
plot(levels, sqnr_u, '-o', levels, sqnr_k, '--s', levels, sqnr_th, ':d', 'LineWidth', 1.5);
grid on;
xlabel('Number of Levels (L)');
ylabel('SQNR (dB)');
title('SQNR vs Levels');
legend('Uniform', 'K-means', 'Theory', 'Location', 'southeast');
xticks(levels);
saveas(gcf, 'task4_sqnr_vs_levels.png');
