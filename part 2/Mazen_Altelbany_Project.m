% =========================================================================
% COMM502 - Communication Theory | Final Lab Project (Winter 2026)
% Digital Communication Link Simulation with Huffman Source Coding
%
% Group Members:
%   1. Mazen Altelbany      (ID: 64-12371)
%   2. Suhad Eyhab Rasheed  (ID: 64-31506)
%   3. Sama Ismael Ahel     (ID: 64-19880)
%
% Complete All-in-One MATLAB File:
% Main script + all local functions at the bottom of this file.
% =========================================================================

clear;
clc;
close all;

%% 1. Group Parameters & Input Signal Definition
% Student IDs:
% Mazen Altelbany:     64-12371 -> non-zero digits: {1, 2, 3, 4, 6, 7}
% Suhad Eyhab Rasheed: 64-31506 -> non-zero digits: {1, 3, 4, 5, 6}
% Sama Ismael Ahel:    64-19880 -> non-zero digits: {1, 4, 6, 8, 9}
%
% a: largest non-zero digit = 9 (from ID 64-19880)
% b: smallest non-zero digit = 1 (present across all three IDs)

a = 9; 
b = 1; 

% Continuous simulation time vector: t = 0 to 30 s with step 0.1 s
t = 0 : 0.1 : 30;

% Input sinusoidal signal formula:
% x(t) = a*sin(0.5*b*pi*t) + a*cos(0.3*b*pi*t)
x = a * sin(0.5 * b * pi * t) + a * cos(0.3 * b * pi * t);

fprintf('=========================================================\n');
fprintf('     COMM502 FINAL LAB PROJECT - COMMUNICATION LINK      \n');
fprintf('=========================================================\n');
fprintf('Parameters:\n');
fprintf('  a = %d (largest non-zero digit)\n', a);
fprintf('  b = %d (smallest non-zero digit)\n', b);
fprintf('  Input Signal: x(t) = %d*sin(%.1f*pi*t) + %d*cos(%.1f*pi*t)\n', a, 0.5*b, a, 0.3*b);
fprintf('  Time Range: 0 to 30 s with step 0.1 s (%d points)\n', length(t));
fprintf('  Signal Amplitude: Min = %.2f, Max = %.2f\n', min(x), max(x));
fprintf('=========================================================\n\n');

%% 2. Sampler Block
% Downsample x(t) by taking 1 sample for every Ns samples (Ns = 3)
Ns = 3; 
[x_s, t_s] = sample_signal(x, t, Ns);

fprintf('Sampler Block:\n');
fprintf('  Downsampling factor Ns = %d\n', Ns);
fprintf('  Continuous points: %d\n', length(t));
fprintf('  Sampled points:    %d\n\n', length(x_s));

%% 3. Simulation for Different Quantization Levels L = 2, 4, 16
levels_to_test = [2, 4, 16];
num_cases = length(levels_to_test);

% Storage for metrics
entropy_vals    = zeros(1, num_cases);
avg_len_vals    = zeros(1, num_cases);
efficiency_vals = zeros(1, num_cases);
fixed_bits_vals = zeros(1, num_cases);
cr_vals         = zeros(1, num_cases);
saving_vals     = zeros(1, num_cases);
mse_vals        = zeros(1, num_cases);

reconstructed_signals = cell(1, num_cases);

for i = 1:num_cases
    L = levels_to_test(i);
    fprintf('---------------------------------------------------------\n');
    fprintf('>>> CASE %d: Quantization Levels L = %d <<<\n', i, L);
    fprintf('---------------------------------------------------------\n');
    
    % --- Uniform Quantizer ---
    % Range covers full signal excursion
    x_min = min(x);
    x_max = max(x);
    [x_q, idx, q_levels, delta] = uniform_quantizer(x_s, L, x_min, x_max);
    
    % --- Symbol Encoder ---
    % Encode each level with its integer number (0 to L-1) as per Req 3
    tx_symbols = idx - 1;
    
    % Compute empirical symbol probabilities
    all_symbols = 0:(L - 1);
    counts = histcounts(tx_symbols, -0.5:1:(L - 0.5));
    probs = counts / length(tx_symbols);
    
    % Filter active symbols (probability > 0)
    active_mask = probs > 0;
    active_symbols = all_symbols(active_mask);
    active_probs = probs(active_mask);
    
    % --- Huffman Source Encoder ---
    [dict, avg_len] = huffmandict(active_symbols, active_probs);
    encoded_bits = huffmanenco(tx_symbols, dict);
    
    % --- Noiseless Channel ---
    rx_bits = encoded_bits;
    
    % --- Huffman Source Decoder ---
    decoded_symbols = huffmandeco(rx_bits, dict);
    is_lossless = isequal(tx_symbols(:), decoded_symbols(:));
    
    % --- Decoder (Map symbols back to quantization levels) ---
    decoded_idx = decoded_symbols + 1;
    x_out = q_levels(decoded_idx);
    x_out = x_out(:);
    reconstructed_signals{i} = x_out;
    
    % --- Metrics Calculation ---
    % 1. Entropy: H = - sum(p * log2(p))
    entropy = -sum(active_probs .* log2(active_probs));
    
    % 2. Average Codeword Length: L_avg = sum(p * len)
    L_avg = avg_len;
    
    % 3. Huffman Coding Efficiency: eta = (H / L_avg) * 100%
    efficiency = (entropy / L_avg) * 100;
    
    % 4. Uncompressed Fixed-Length Bits: R = ceil(log2(L))
    R_fixed = ceil(log2(L));
    
    % 5. Compression Ratio: CR = R_fixed / L_avg
    CR = R_fixed / L_avg;
    
    % 6. Space Savings / Compression Rate: (1 - L_avg/R_fixed) * 100%
    compression_saving = (1 - L_avg / R_fixed) * 100;
    
    % 7. Mean Squared Error (MSE)
    mse = mean((x_s(:) - x_out(:)).^2);
    
    % Store metrics
    entropy_vals(i)    = entropy;
    avg_len_vals(i)    = L_avg;
    efficiency_vals(i) = efficiency;
    fixed_bits_vals(i) = R_fixed;
    cr_vals(i)         = CR;
    saving_vals(i)     = compression_saving;
    mse_vals(i)        = mse;
    
    % Display numerical results
    fprintf('  Quantizer Step Size (delta):       %.4f\n', delta);
    fprintf('  Total Sampled Points:              %d\n', length(x_s));
    fprintf('  Fixed-Length Code (PCM):           %d bits/sample\n', R_fixed);
    fprintf('  Total Fixed Bits (Uncompressed):   %d bits\n', length(x_s) * R_fixed);
    fprintf('  Total Huffman Encoded Bits:        %d bits\n', length(encoded_bits));
    fprintf('  Source Entropy (H):                %.4f bits/symbol\n', entropy);
    fprintf('  Average Code Length (L_avg):       %.4f bits/symbol\n', L_avg);
    fprintf('  Huffman Coding Efficiency:         %.2f %%\n', efficiency);
    fprintf('  Compression Ratio (CR):            %.4f\n', CR);
    fprintf('  Compression Rate (Space Savings):  %.2f %%\n', compression_saving);
    fprintf('  Mean Squared Error (MSE):          %.4f\n', mse);
    fprintf('  Channel Error Free:                %s\n', mat2str(is_lossless));
    
    fprintf('  Huffman Dictionary (sample codewords):\n');
    disp_limit = min(4, size(dict, 1));
    for d = 1:disp_limit
        fprintf('    Symbol %2d (p=%.3f) -> Code: %s\n', ...
            dict{d,1}, active_probs(d), num2str(dict{d,2}));
    end
    if size(dict, 1) > disp_limit
        fprintf('    ... (%d total codewords in dictionary)\n', size(dict, 1));
    end
    fprintf('\n');
end

%% 4. Summary Table of Results
fprintf('=========================================================================================\n');
fprintf('                              SUMMARY OF SIMULATION RESULTS                              \n');
fprintf('=========================================================================================\n');
fprintf('  L   | Fixed Bits | Entropy (H) | Avg Length | Efficiency (%%) | Comp Ratio | Savings (%%) | MSE\n');
fprintf('-----------------------------------------------------------------------------------------\n');
for i = 1:num_cases
    fprintf(' %2d   |     %d      |   %.4f    |   %.4f   |     %6.2f     |   %.4f   |    %5.2f   | %.4f\n', ...
        levels_to_test(i), fixed_bits_vals(i), entropy_vals(i), avg_len_vals(i), ...
        efficiency_vals(i), cr_vals(i), saving_vals(i), mse_vals(i));
end
fprintf('=========================================================================================\n\n');

%% 5. Plotting Requirement 8: Input and Output Signals on the Same Figure
% Combined 3-Subplot Figure
figure('Name', 'Input vs Reconstructed Output Signals', 'Position', [100, 100, 900, 700]);

for i = 1:num_cases
    L = levels_to_test(i);
    subplot(3, 1, i);
    plot(t, x, 'b-', 'LineWidth', 1.2);
    hold on;
    stairs(t_s, reconstructed_signals{i}, 'r--', 'LineWidth', 1.2);
    hold off;
    grid on;
    xlim([0, 30]);
    xlabel('Time (seconds)');
    ylabel('Amplitude');
    title(sprintf('Input vs Reconstructed Output (L = %d Levels, N_s = %d)', L, Ns));
    legend('Continuous Input x(t)', 'Reconstructed Output x_{out}(t)', 'Location', 'southwest');
end
saveas(gcf, 'input_vs_output_all_levels.png');

% Individual figures for each L
for i = 1:num_cases
    L = levels_to_test(i);
    fig = figure('Name', sprintf('Input vs Output L=%d', L), 'Position', [150, 150, 800, 450]);
    plot(t, x, 'b-', 'LineWidth', 1.5);
    hold on;
    stairs(t_s, reconstructed_signals{i}, 'r--', 'LineWidth', 1.3);
    stem(t_s, reconstructed_signals{i}, 'k:', 'MarkerSize', 3, 'LineWidth', 0.8);
    hold off;
    grid on;
    xlim([0, 30]);
    xlabel('Time (seconds)');
    ylabel('Amplitude');
    title(sprintf('Input Signal x(t) vs Reconstructed Output x_{out}(t) [L = %d]', L));
    legend('Input Signal x(t)', 'Reconstructed Output (Staircase)', 'Sample Points', 'Location', 'southwest');
    saveas(fig, sprintf('input_vs_output_L%d.png', L));
end

%% 6. Plotting Requirement 9: Huffman Coding Efficiency vs Number of Quantization Levels
curve_levels = [2, 4, 8, 16, 32];
curve_efficiency = zeros(size(curve_levels));

for k = 1:length(curve_levels)
    cL = curve_levels(k);
    [~, c_idx] = uniform_quantizer(x_s, cL, min(x), max(x));
    c_sym = c_idx - 1;
    c_counts = histcounts(c_sym, -0.5:1:(cL - 0.5));
    c_p = c_counts / length(c_sym);
    valid = c_p > 0;
    c_syms_v = (0:(cL-1)); c_syms_v = c_syms_v(valid);
    c_p_v = c_p(valid);
    [~, c_avglen] = huffmandict(c_syms_v, c_p_v);
    c_H = -sum(c_p_v .* log2(c_p_v));
    curve_efficiency(k) = (c_H / c_avglen) * 100;
end

figure('Name', 'Huffman Coding Efficiency vs Levels', 'Position', [200, 200, 750, 480]);
plot(curve_levels, curve_efficiency, 'b-o', 'LineWidth', 2, 'MarkerFaceColor', 'b', 'MarkerSize', 6);
hold on;
for i = 1:num_cases
    req_L = levels_to_test(i);
    req_eff = efficiency_vals(i);
    plot(req_L, req_eff, 'rs', 'MarkerSize', 10, 'MarkerFaceColor', 'r');
    text(req_L, req_eff - 0.4, sprintf('  L=%d (%.1f%%)', req_L, req_eff), ...
        'FontSize', 10, 'FontWeight', 'bold', 'Color', 'r');
end
hold off;
grid on;
xticks(curve_levels);
xlabel('Number of Quantization Levels (L)');
ylabel('Huffman Coding Efficiency (%)');
title('Huffman Coding Efficiency vs Number of Quantization Levels');
legend('Efficiency Curve', 'Required Simulation Points (L = 2, 4, 16)', 'Location', 'southeast');
ylim([95, 101]);
saveas(gcf, 'efficiency_vs_levels.png');

fprintf('Simulation and figure generation completed successfully.\n');


% =========================================================================
% LOCAL FUNCTIONS (All functions contained in this single file)
% =========================================================================

%% Function 1: Sampler Block
function [xs, ts] = sample_signal(x, t, Ns)
% Downsamples input x(t) by taking 1 sample every Ns samples
    idx = 1:Ns:length(x);
    xs = x(idx);
    ts = t(idx);
end

%% Function 2: Uniform Quantizer Block
function [xq, idx, levels, delta] = uniform_quantizer(x, L, x_min, x_max)
% Uniform quantizer adapted from Practical Assignment 1
    if nargin < 3 || isempty(x_min)
        x_min = min(x);
    end
    if nargin < 4 || isempty(x_max)
        x_max = max(x);
    end

    delta = (x_max - x_min) / L;
    levels = x_min + ((1:L) - 0.5) * delta;
    
    idx = floor((x - x_min) / delta) + 1;
    idx(idx > L) = L;
    idx(idx < 1) = 1;
    
    xq = levels(idx);
    xq = xq(:);
end

%% Function 3: Huffman Dictionary Generator
function [dict, avglen] = huffmandict(symbols, probs)
% Builds Huffman codebook dictionary (compatible with Communications Toolbox)
    symbols = symbols(:);
    probs = probs(:);
    
    if length(symbols) ~= length(probs)
        error('Symbols and probabilities must have the same length.');
    end
    
    probs = probs / sum(probs);
    n = length(symbols);
    
    if n == 1
        dict = {symbols(1), [0]};
        avglen = 1;
        return;
    end
    
    nodes = cell(2 * n - 1, 1);
    for i = 1:n
        nodes{i} = struct('left', 0, 'right', 0, 'prob', probs(i), 'is_leaf', true, 'symbol', symbols(i));
    end
    
    active = 1:n;
    curr_prob = probs;
    node_count = n;
    
    while length(active) > 1
        [sorted_p, sort_idx] = sort(curr_prob);
        idx1 = active(sort_idx(1));
        idx2 = active(sort_idx(2));
        
        node_count = node_count + 1;
        new_prob = sorted_p(1) + sorted_p(2);
        nodes{node_count} = struct('left', idx1, 'right', idx2, 'prob', new_prob, 'is_leaf', false, 'symbol', []);
        
        active(sort_idx(1:2)) = [];
        curr_prob(sort_idx(1:2)) = [];
        active = [active, node_count];
        curr_prob = [curr_prob; new_prob];
    end
    
    root = node_count;
    dict = cell(n, 2);
    leaf_idx = 0;
    
    function traverse(node_idx, code)
        node = nodes{node_idx};
        if node.is_leaf
            leaf_idx = leaf_idx + 1;
            dict{leaf_idx, 1} = node.symbol;
            dict{leaf_idx, 2} = code;
        else
            traverse(node.left, [code, 0]);
            traverse(node.right, [code, 1]);
        end
    end

    traverse(root, []);
    
    % Sort dictionary to match original symbol order
    orig_dict = cell(n, 2);
    for i = 1:n
        for j = 1:n
            if isequal(dict{j, 1}, symbols(i))
                orig_dict(i, :) = dict(j, :);
                break;
            end
        end
    end
    dict = orig_dict;
    
    avglen = 0;
    for i = 1:n
        avglen = avglen + probs(i) * length(dict{i, 2});
    end
end

%% Function 4: Huffman Encoder
function code = huffmanenco(sig, dict)
% Encodes symbols using Huffman dictionary
    sig = sig(:);
    n_syms = size(dict, 1);
    code_cell = cell(length(sig), 1);
    
    for i = 1:length(sig)
        s = sig(i);
        found = false;
        for j = 1:n_syms
            if isequal(dict{j, 1}, s)
                code_cell{i} = dict{j, 2};
                found = true;
                break;
            end
        end
        if ~found
            error(['Symbol ' num2str(s) ' not found in Huffman dictionary.']);
        end
    end
    
    code = cell2mat(code_cell')';
    code = code(:);
end

%% Function 5: Huffman Decoder
function sig = huffmandeco(code, dict)
% Decodes binary bitstream using Huffman dictionary
    code = code(:)';
    n_syms = size(dict, 1);
    sig = [];
    current_bits = [];
    
    for bit = code
        current_bits = [current_bits, bit];
        for j = 1:n_syms
            if isequal(dict{j, 2}, current_bits)
                sig = [sig, dict{j, 1}];
                current_bits = [];
                break;
            end
        end
    end
    sig = sig(:);
end
