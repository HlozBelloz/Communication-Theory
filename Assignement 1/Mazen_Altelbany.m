%% Communication Theory - Assignment 1
% Simulation and Comparison of Uniform and K-means Quantization
% Group Members: 
%   1. Mazen Altelbany (64-12371)
%   2. Suhad Eyhab Rasheed (64-31506)
%   3. Sama Ismael Ahel (64-19880)
% Largest digit across IDs: a = 9 (from ID 64-19880) -> Range [-9, 9]

clear;
clc;
close all;

%% 1. Simulation Setup & Input Signal Generation
% Range parameter determined by maximum digit across all IDs
a = 9; 

% Number of samples
N = 10000;

% Set random seed for repeatable results across runs
rng(42);

% Generate uniformly distributed input signal between [-a, a]
% Formula: x = -a + 2*a*rand(N, 1)
x = -a + 2 * a * rand(N, 1);

% Number of quantization levels to test (adaptable to any levels vector)
levels = [2, 4, 8];
numCases = length(levels);

% Preallocate metric arrays
mae_uniform  = zeros(1, numCases);
mae_kmeans   = zeros(1, numCases);

var_uniform  = zeros(1, numCases);
var_kmeans   = zeros(1, numCases);
var_theory   = zeros(1, numCases);

sqnr_uniform = zeros(1, numCases);
sqnr_kmeans  = zeros(1, numCases);
sqnr_theory  = zeros(1, numCases);

% Signal power: simulated and theoretical (for uniform distribution P_sig = a^2 / 3)
P_signal_sim    = mean(x.^2);
P_signal_theory = (a^2) / 3;

fprintf('========================================================================\n');
fprintf('           COMMUNICATION THEORY - ASSIGNMENT 1 SIMULATION              \n');
fprintf('  Signal Range: [-%d, %d] | Number of Samples: %d | Signal Power: %.4f \n', ...
        a, a, N, P_signal_sim);
fprintf('========================================================================\n\n');

%% 2. Loop Through Quantization Levels (L = 2, 4, 8)
for i = 1:numCases
    L = levels(i);
    
    fprintf('------------------------------------------------------------------------\n');
    fprintf('                           TESTING L = %d LEVELS                         \n', L);
    fprintf('------------------------------------------------------------------------\n');
    
    %% --- Part A: Uniform Quantizer ---
    % Step size (Delta)
    delta = (2 * a) / L;
    
    % Mid-point reconstruction levels for each interval
    uniform_levels = -a + ((1:L) - 0.5) * delta;
    
    % Map each sample to its corresponding interval index (1 to L)
    interval_idx = floor((x - (-a)) / delta) + 1;
    interval_idx(interval_idx > L) = L;
    interval_idx(interval_idx < 1) = 1;
    
    % Uniform quantized vector (guaranteed column vector)
    x_q_uniform = uniform_levels(interval_idx);
    x_q_uniform = x_q_uniform(:);
    
    %% --- Part B: Machine-Learning K-means Quantizer ---
    % Using MATLAB built-in kmeans function with multiple replicates
    % This lets K-means cluster the data independently from scratch
    [kmeans_idx, kmeans_centers] = kmeans(x, L, 'Replicates', 5, 'MaxIter', 100);
    
    % K-means quantized vector
    x_q_kmeans = kmeans_centers(kmeans_idx);
    x_q_kmeans = x_q_kmeans(:);
    
    %% --- Task 1: Display First 6 Samples ---
    fprintf('\n[Task 1] First 6 Elements Comparison (L = %d):\n', L);
    sample_table = table((1:6)', x(1:6), x_q_uniform(1:6), x_q_kmeans(1:6), ...
        'VariableNames', {'Sample_Index', 'Original_x', 'Uniform_x_q', 'Kmeans_x_q'});
    disp(sample_table);
    
    %% --- Task 2: Mean Absolute Error (MAE) ---
    e_uniform = x - x_q_uniform;
    e_kmeans  = x - x_q_kmeans;
    
    mae_uniform(i) = mean(abs(e_uniform));
    mae_kmeans(i)  = mean(abs(e_kmeans));
    
    fprintf('[Task 2] Mean Absolute Error (MAE):\n');
    fprintf('         Uniform Quantizer : %.4f\n', mae_uniform(i));
    fprintf('         K-means Quantizer : %.4f\n', mae_kmeans(i));
    
    %% --- Task 3: Quantization Error Variance ---
    var_uniform(i) = var(e_uniform);
    var_kmeans(i)  = var(e_kmeans);
    var_theory(i)  = (delta^2) / 12;
    
    fprintf('[Task 3] Quantization Error Variance:\n');
    fprintf('         Uniform Quantizer (Simulated)   : %.4f\n', var_uniform(i));
    fprintf('         K-means Quantizer (Simulated)   : %.4f\n', var_kmeans(i));
    fprintf('         Theoretical Variance (Delta^2/12): %.4f\n', var_theory(i));
    
    %% --- Task 4: Signal-to-Quantization-Noise Ratio (SQNR) ---
    P_noise_u = mean(e_uniform.^2);
    P_noise_k = mean(e_kmeans.^2);
    
    sqnr_uniform(i) = 10 * log10(P_signal_sim / P_noise_u);
    sqnr_kmeans(i)  = 10 * log10(P_signal_sim / P_noise_k);
    sqnr_theory(i)  = 10 * log10(P_signal_theory / var_theory(i));
    
    fprintf('[Task 4] Signal-to-Quantization-Noise Ratio (SQNR):\n');
    fprintf('         Uniform Quantizer (Simulated) : %.2f dB\n', sqnr_uniform(i));
    fprintf('         K-means Quantizer (Simulated) : %.2f dB\n', sqnr_kmeans(i));
    fprintf('         Theoretical SQNR              : %.2f dB\n\n', sqnr_theory(i));
end

%% 3. Comments and Performance Discussion Output to Console
fprintf('========================================================================\n');
fprintf('                           SUMMARY & COMMENTS                           \n');
fprintf('========================================================================\n');
fprintf('1. MAE Performance (Task 2):\n');
fprintf('   - As the number of levels L doubles (2 -> 4 -> 8), step size Delta is halved.\n');
fprintf('   - Consequently, MAE drops by approximately 50%% at each doubling.\n');
fprintf('   - Both quantizers produce almost identical MAE across all tested levels.\n\n');

fprintf('2. Variance Performance (Task 3):\n');
fprintf('   - Error variance drops by a factor of 4 (approx 75%% decrease) when L doubles,\n');
fprintf('     consistent with the theoretical formula Var = Delta^2 / 12.\n');
fprintf('   - Simulated uniform and K-means variances match theoretical values closely.\n\n');

fprintf('3. SQNR Performance (Task 4):\n');
fprintf('   - SQNR increases by approximately 6 dB for each added bit of resolution\n');
fprintf('     (L = 2 -> ~6 dB, L = 4 -> ~12 dB, L = 8 -> ~18 dB).\n');
fprintf('   - Both techniques match the theoretical 6.02 dB/bit rule closely.\n\n');

fprintf('4. Uniform vs. K-means Quantization:\n');
fprintf('   - Uniform quantizer determines levels analytically prior to observing data.\n');
fprintf('   - K-means quantizer determines levels iteratively based on data distribution.\n');
fprintf('   - For a uniform distribution, K-means naturally converges to uniform levels.\n');
fprintf('   - For non-uniform distributions (e.g. Gaussian), K-means would place more levels\n');
fprintf('     in high-density regions, significantly outperforming uniform quantization.\n');
fprintf('========================================================================\n\n');

%% 4. Plotting Results & Saving Figures

% Figure 1: Mean Absolute Error (MAE) vs Levels
h1 = figure('Name', 'Task 2 - Mean Absolute Error vs Levels', 'NumberTitle', 'off');
plot(levels, mae_uniform, '-o', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'Uniform Quantizer');
hold on;
plot(levels, mae_kmeans, '--s', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'K-means Quantizer');
grid on;
xlabel('Number of Quantization Levels (L)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Mean Absolute Error (MAE)', 'FontSize', 11, 'FontWeight', 'bold');
title('Task 2: Mean Absolute Quantization Error vs Number of Levels', 'FontSize', 12, 'FontWeight', 'bold');
legend('Location', 'northeast', 'FontSize', 10);
xticks(levels);
saveas(h1, 'task2_mae_vs_levels.png');

% Figure 2: Quantization Error Variance vs Levels
h2 = figure('Name', 'Task 3 - Error Variance vs Levels', 'NumberTitle', 'off');
plot(levels, var_uniform, '-o', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'Uniform (Simulated)');
hold on;
plot(levels, var_kmeans, '--s', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'K-means (Simulated)');
plot(levels, var_theory, ':d', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'Theoretical (\Delta^2 / 12)');
grid on;
xlabel('Number of Quantization Levels (L)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('Quantization Error Variance', 'FontSize', 11, 'FontWeight', 'bold');
title('Task 3: Quantization Error Variance vs Number of Levels', 'FontSize', 12, 'FontWeight', 'bold');
legend('Location', 'northeast', 'FontSize', 10);
xticks(levels);
saveas(h2, 'task3_variance_vs_levels.png');

% Figure 3: SQNR vs Levels
h3 = figure('Name', 'Task 4 - SQNR vs Levels', 'NumberTitle', 'off');
plot(levels, sqnr_uniform, '-o', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'Uniform (Simulated)');
hold on;
plot(levels, sqnr_kmeans, '--s', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'K-means (Simulated)');
plot(levels, sqnr_theory, ':d', 'LineWidth', 1.8, 'MarkerSize', 8, 'DisplayName', 'Theoretical (20 log_{10}(L))');
grid on;
xlabel('Number of Quantization Levels (L)', 'FontSize', 11, 'FontWeight', 'bold');
ylabel('SQNR (dB)', 'FontSize', 11, 'FontWeight', 'bold');
title('Task 4: Signal-to-Quantization-Noise Ratio (SQNR) vs Number of Levels', 'FontSize', 12, 'FontWeight', 'bold');
legend('Location', 'southeast', 'FontSize', 10);
xticks(levels);
saveas(h3, 'task4_sqnr_vs_levels.png');

fprintf('Simulation complete. Three figures displayed and saved as PNG images:\n');
fprintf('  - task2_mae_vs_levels.png\n');
fprintf('  - task3_variance_vs_levels.png\n');
fprintf('  - task4_sqnr_vs_levels.png\n');
