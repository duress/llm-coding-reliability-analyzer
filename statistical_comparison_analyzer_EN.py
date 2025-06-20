def save_results_optimized(self, file1, file2, all_results, encodings1, encodings2):
    """
    Save analysis results to text and CSV files, with filenames including parts of the input filenames.

    Parameters:
    - file1, file2 (str): Paths to the input files.
    - all_results (dict): Analysis results.
    - encodings1, encodings2 (list): Encoded data from the two datasets.
    """
    output_dir = Path(file1).parent or Path('.')
    
    # Extract the core part of input filenames (without extension)
    file1_name = Path(file1).stem
    file2_name = Path(file2).stem
    
    # Construct output filename including input filenames and bootstrap iterations
    output_filename = f"Reliability_Analysis_{file1_name}_vs_{file2_name}_{self.bootstrap_iterations}"
    output_file = output_dir / f"{output_filename}.txt"
    csv_file = output_dir / f"{output_filename}.csv"
    
    csv_data = []

    try:
        with open(output_file, 'w', encoding='utf-8-sig') as f:
            f.write(f"=== Kappa Analysis Results (Bootstrap Iterations: {self.bootstrap_iterations}) ===\n")
            f.write(f"Input Files: {Path(file1).name} vs {Path(file2).name}\n")
            f.write("Statistical Methods: Fisher’s z transformation + Independent t-test (Kappa) and Z-test (AI-Human Disagreement Rate)\n")
            f.write("AI-Human Disagreement Rate: Proportion of cases where any AI rater disagrees with the human rater\n")
            f.write("Multiple Comparison Correction: Benjamini-Hochberg\n\n")

            for i, (file, encodings) in enumerate([(file1, encodings1), (file2, encodings2)], 1):
                stats = all_results[f'kappa{i}_results']
                desc_inter = self.descriptive_stats_fast(stats[0])
                desc_intra = self.descriptive_stats_fast(stats[2])
                consistency = all_results[f'consistency{i}']
                disagreement = self.disagreement_analysis_optimized(encodings)
                cat_dist = self.calculate_category_distribution(encodings)

                f.write(f"Prompt{i} File: {Path(file).name}\n")
                f.write(f"Data: {consistency['total_cases']} cases\n")
                f.write(f"Category Distribution (AI): {', '.join([f'{k}: {v:.3f}' for k, v in cat_dist['ai_dist'].items()])}\n")
                f.write(f"Category Distribution (Human): {', '.join([f'{k}: {v:.3f}' for k, v in cat_dist['human_dist'].items()])}\n")
                f.write(f"\n=== Prompt{i} Kappa Descriptive Statistics ===\n")
                f.write(f"Inter-rater Reliability (AI vs Human): μ={desc_inter['mean']:.4f}, σ={desc_inter['std']:.4f}\n")
                f.write(f"Intra-rater Reliability (AI vs AI): μ={desc_intra['mean']:.4f}, σ={desc_intra['std']:.4f}\n")
                f.write(f"Average Kappa per AI Coder: {', '.join([f'AI{i+1}: {v:.4f}' for i, v in stats[4].items()])}\n")

                disagreement_rates = all_results.get('disagreement_rates', [0, 0, 0, 0, 0, 0, np.nan, np.nan])
                if len(disagreement_rates) < 8:
                    logging.error(f"disagreement_rates length insufficient: {disagreement_rates}")
                    f.write("AI-Human Disagreement Rate: Cannot compute (insufficient data)\n")
                else:
                    rate_idx = 0 if i == 1 else 1
                    disagree_idx = 2 if i == 1 else 3
                    total_idx = 4 if i == 1 else 5
                    f.write(f"AI-Human Disagreement Rate: {disagreement_rates[rate_idx]:.4f} "
                            f"({disagreement_rates[disagree_idx]}/{disagreement_rates[total_idx]} cases)\n")

                ai_human_dist = disagreement.get('ai_human_disagreement_distribution', [0] * (self.n_raters-1))
                f.write(f"AI-Human Disagreement Distribution: ")
                for j, count in enumerate(ai_human_dist):
                    f.write(f"{j} AI Disagreements={count}, ")
                f.write(f"\n")

                for j, k in enumerate(stats[0], 1):
                    csv_data.append({'Prompt': i, 'Comparison': f'AI{j}-Human', 'Kappa': k, 'SE': stats[1][j-1]})
                for idx, (ai_i, ai_j) in enumerate(combinations(range(self.n_raters-1), 2)):
                    csv_data.append({'Prompt': i, 'Comparison': f'AI{ai_i+1}-AI{ai_j+1}', 'Kappa': stats[2][idx], 'SE': stats[3][idx]})

            if all_results.get('comparison_results'):
                comp = all_results['comparison_results']
                disagreement_rates = all_results.get('disagreement_rates', [0, 0, 0, 0, 0, 0, np.nan, np.nan])
                f.write("\n=== Statistical Comparison Results ===\n")
                f.write("Methods: Fisher’s z transformation + Independent t-test (Kappa) and Z-test (AI-Human Disagreement Rate)\n")
                f.write(f"Inter-rater Comparison: t={comp[0]:.3f}, p={comp[1]:.6f}, Cohen's d={comp[2]:.3f}\n")
                f.write(f"Intra-rater Comparison: t={comp[3]:.3f}, p={comp[4]:.6f}, Cohen's d={comp[5]:.3f}\n")
                if len(disagreement_rates) >= 8:
                    f.write(f"AI-Human Disagreement Rate Comparison: Z={disagreement_rates[6]:.4f}, p={disagreement_rates[7]:.6f}\n")
                else:
                    f.write("AI-Human Disagreement Rate Comparison: Cannot compute (insufficient data)\n")
                corrected_p = all_results.get('corrected_p_values', [comp[1], comp[4], disagreement_rates[7] if len(disagreement_rates) >= 8 else np.nan])
                f.write(f"\n=== Multiple Comparison Corrected p-values (Benjamini-Hochberg) ===\n")
                f.write(f"Inter-rater Comparison (Corrected): p={corrected_p[0]:.6f} {self.get_significance_symbol(corrected_p[0])}\n")
                f.write(f"Intra-rater Comparison (Corrected): p={corrected_p[1]:.6f} {self.get_significance_symbol(corrected_p[1])}\n")
                f.write(f"AI-Human Disagreement Rate Comparison (Corrected): p={corrected_p[2]:.6f} {self.get_significance_symbol(corrected_p[2])}\n")
                f.write(f"\n=== Non-parametric Test Verification ===\n")
                f.write(f"Inter-rater Mann-Whitney U: p={comp[6]:.6f} {self.get_significance_symbol(comp[6])}\n")
                f.write(f"Intra-rater Mann-Whitney U: p={comp[7]:.6f} {self.get_significance_symbol(comp[7])}\n")

        pd.DataFrame(csv_data).to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"📄 CSV results saved to: {csv_file.name}")
        print(f"📄 Results saved to: {output_file.name}")
    except IndexError as e:
        print(f"❌ Index error while saving results: {e}")
        logging.error(f"Index error while saving results: {e}")
    except Exception as e:
        print(f"❌ Error saving results: {e}")
        logging.error(f"Error saving results to {output_file}: {e}")