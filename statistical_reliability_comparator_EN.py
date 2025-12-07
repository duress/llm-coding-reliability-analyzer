#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats
from sklearn.metrics import cohen_kappa_score
from itertools import combinations
import logging
from typing import List, Tuple, Dict
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kappa_analyzer.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


class ReliabilityComparator:
    """
    Statistical Reliability Comparator for LLM Repeated Coding
    
    Compares coding reliability between two conditions (e.g., different prompts)
    """
    
    def __init__(self, bootstrap_iterations: int = 1000, n_raters: int = 6, alpha: float = 0.05):
        """
        Initialize the comparator
        
        Parameters:
        -----------
        bootstrap_iterations : int
            Number of bootstrap iterations, default 1000
        n_raters : int
            Total number of coding runs (5 LLM repeated runs + 1 Human standard), default 6
        alpha : float
            Significance level, default 0.05
        """
        self.bootstrap_iterations = bootstrap_iterations
        self.n_raters = n_raters
        self.alpha = alpha
        logging.info(f"Initialized ReliabilityComparator: bootstrap={bootstrap_iterations}, n_raters={n_raters}")
    
    def read_data(self, file_path: str, delimiter: str = '\t', encoding: str = 'utf-8') -> np.ndarray:
        """
        Read coding data file
        
        Parameters:
        -----------
        file_path : str
            File path
        delimiter : str
            Delimiter, default tab
        encoding : str
            File encoding, default utf-8
            
        Returns:
        --------
        np.ndarray
            Encoding matrix, shape = (n_samples, n_raters)
        """
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, header=None)
            logging.info(f"Successfully loaded file: {file_path}, shape: {df.shape}")
        except UnicodeDecodeError:
            logging.warning(f"Failed with {encoding} encoding, trying gbk encoding")
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='gbk', header=None)
            logging.info(f"Successfully loaded file with gbk encoding")
        
        # Take first n_raters columns as coding data
        encodings = df.iloc[:, :self.n_raters].values
        return encodings
    
    def calculate_kappa(self, r1: np.ndarray, r2: np.ndarray) -> float:
        """
        Calculate Cohen's Kappa coefficient using sklearn
        
        Parameters:
        -----------
        r1, r2 : np.ndarray
            Ratings from two raters
            
        Returns:
        --------
        float
            Cohen's Kappa value
        """
        return cohen_kappa_score(r1, r2)
    
    def bootstrap_kappa_se(self, r1: np.ndarray, r2: np.ndarray, n_iterations: int = None) -> float:
        """
        Estimate Kappa's standard error using Bootstrap method
        
        Parameters:
        -----------
        r1, r2 : np.ndarray
            Ratings from two raters
        n_iterations : int
            Number of bootstrap iterations
            
        Returns:
        --------
        float
            Standard error of Kappa
        """
        if n_iterations is None:
            n_iterations = self.bootstrap_iterations
        
        n = len(r1)
        kappas = []
        
        for _ in range(n_iterations):
            indices = np.random.choice(n, size=n, replace=True)
            r1_boot = r1[indices]
            r2_boot = r2[indices]
            kappas.append(self.calculate_kappa(r1_boot, r2_boot))
        
        return np.std(kappas)
    
    def calculate_all_kappas(self, encodings: np.ndarray) -> Tuple[List[float], List[float], List[float], List[float]]:
        """
        Calculate all Kappa values and their standard errors
        
        Parameters:
        -----------
        encodings : np.ndarray
            Encoding matrix, shape = (n_samples, n_raters)
            Last column is human standard coding, others are LLM repeated coding runs
            
        Returns:
        --------
        Tuple[List, List, List, List]
            - inter_kappas: Kappa values for LLM vs Human
            - inter_ses: Standard errors for LLM vs Human
            - intra_kappas: Kappa values for LLM coding consistency
            - intra_ses: Standard errors for LLM coding consistency
        """
        n_llm = self.n_raters - 1
        human_codes = encodings[:, -1]
        llm_codes = encodings[:, :n_llm]
        
        # Inter-rater: LLM vs Human
        inter_kappas = []
        inter_ses = []
        
        for i in range(n_llm):
            kappa = self.calculate_kappa(llm_codes[:, i], human_codes)
            se = self.bootstrap_kappa_se(llm_codes[:, i], human_codes)
            inter_kappas.append(kappa)
            inter_ses.append(se)
        
        # Intra-rater: LLM coding consistency across repeated runs
        intra_kappas = []
        intra_ses = []
        
        for i in range(n_llm):
            for j in range(i + 1, n_llm):
                kappa = self.calculate_kappa(llm_codes[:, i], llm_codes[:, j])
                se = self.bootstrap_kappa_se(llm_codes[:, i], llm_codes[:, j])
                intra_kappas.append(kappa)
                intra_ses.append(se)
        
        return inter_kappas, inter_ses, intra_kappas, intra_ses
    
    def fisher_z_transform(self, kappa: float) -> float:
        """
        Fisher's z transformation
        
        Transform Kappa values to approximately normal z values
        
        Parameters:
        -----------
        kappa : float
            Kappa value
            
        Returns:
        --------
        float
            Transformed z value
        """
        kappa = np.clip(kappa, -0.9999, 0.9999)
        z = 0.5 * np.log((1 + kappa) / (1 - kappa))
        return z
    
    def compare_kappas(self, kappas1: List[float], kappas2: List[float]) -> Tuple[float, float]:
        """
        Compare two groups of Kappa values using Fisher's z transformation and independent samples t-test
        
        Parameters:
        -----------
        kappas1, kappas2 : List[float]
            Two groups of Kappa values
            
        Returns:
        --------
        Tuple[float, float]
            - t_statistic: t statistic
            - p_value: p value
        """
        # Fisher's z transformation
        z1 = [self.fisher_z_transform(k) for k in kappas1]
        z2 = [self.fisher_z_transform(k) for k in kappas2]
        
        # Independent samples t-test
        t_stat, p_value = stats.ttest_ind(z1, z2)
        
        return t_stat, p_value
    
    def z_test_proportions(self, count1: int, n1: int, count2: int, n2: int) -> Tuple[float, float]:
        """
        Z-test for two proportions (disagreement rates)
        
        Parameters:
        -----------
        count1, count2 : int
            Number of disagreement cases in two groups
        n1, n2 : int
            Total number of cases in two groups
            
        Returns:
        --------
        Tuple[float, float]
            - z_statistic: Z statistic
            - p_value: p value
        """
        p1 = count1 / n1 if n1 > 0 else 0
        p2 = count2 / n2 if n2 > 0 else 0
        
        # Pooled proportion
        p_pool = (count1 + count2) / (n1 + n2) if (n1 + n2) > 0 else 0
        
        # Standard error
        se = np.sqrt(p_pool * (1 - p_pool) * (1/n1 + 1/n2)) if (n1 + n2) > 0 else 1e-10
        
        # Z statistic
        z_stat = (p1 - p2) / se if se > 0 else 0
        
        # p value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
        
        return z_stat, p_value
    
    def benjamini_hochberg_correction(self, p_values: List[float]) -> List[float]:
        """
        Benjamini-Hochberg FDR multiple comparison correction
        
        Parameters:
        -----------
        p_values : List[float]
            Original p values
            
        Returns:
        --------
        List[float]
            Corrected p values
        """
        p_values = np.array(p_values)
        n = len(p_values)
        
        # Sort p-values and track original indices
        sorted_indices = np.argsort(p_values)
        sorted_p = p_values[sorted_indices]
        
        # Calculate corrected p-values
        corrected_p = np.zeros(n)
        for i in range(n-1, -1, -1):
            if i == n-1:
                corrected_p[sorted_indices[i]] = sorted_p[i]
            else:
                corrected_p[sorted_indices[i]] = min(
                    sorted_p[i] * n / (i + 1),
                    corrected_p[sorted_indices[i + 1]]
                )
        
        return corrected_p.tolist()
    
    def get_significance_symbol(self, p_value: float) -> str:
        """Get significance symbol based on p-value"""
        if p_value < 0.001:
            return "**"
        elif p_value < 0.05:
            return "*"
        else:
            return "n.s."
    
    def calculate_disagreement_rate(self, encodings: np.ndarray) -> Tuple[float, int, int]:
        """
        Calculate LLM-Human disagreement rate
        
        Definition: Proportion of cases where any LLM coding run disagrees with human standard coding
        
        Parameters:
        -----------
        encodings : np.ndarray
            Encoding matrix
            
        Returns:
        --------
        Tuple[float, int, int]
            - disagreement_rate: Disagreement rate
            - disagreement_count: Number of disagreement cases
            - total_cases: Total number of cases
        """
        n_llm = self.n_raters - 1
        human_codes = encodings[:, -1]
        llm_codes = encodings[:, :n_llm]
        
        total_cases = len(encodings)
        disagreement_count = 0
        
        for i in range(total_cases):
            # Check if any LLM run disagrees with human
            if any(llm_codes[i, j] != human_codes[i] for j in range(n_llm)):
                disagreement_count += 1
        
        disagreement_rate = disagreement_count / total_cases if total_cases > 0 else 0.0
        
        return disagreement_rate, disagreement_count, total_cases
    
    def descriptive_stats(self, values: List[float]) -> Dict[str, float]:
        """Calculate descriptive statistics"""
        arr = np.array(values)
        return {
            'mean': np.mean(arr),
            'std': np.std(arr, ddof=1)
        }
    
    def compare_two_conditions(self, file1: str, file2: str) -> Dict:
        """
        Compare coding reliability between two conditions
        
        Parameters:
        -----------
        file1, file2 : str
            Paths to two files
            
        Returns:
        --------
        Dict
            Complete analysis results
        """
        logging.info("Starting two-condition comparison")
        
        # Read data
        encodings1 = self.read_data(file1)
        encodings2 = self.read_data(file2)
        
        # Calculate Kappa values
        inter_kappas1, inter_ses1, intra_kappas1, intra_ses1 = self.calculate_all_kappas(encodings1)
        inter_kappas2, inter_ses2, intra_kappas2, intra_ses2 = self.calculate_all_kappas(encodings2)
        
        # Calculate disagreement rates
        disagree_rate1, disagree_count1, total1 = self.calculate_disagreement_rate(encodings1)
        disagree_rate2, disagree_count2, total2 = self.calculate_disagreement_rate(encodings2)
        
        # Statistical comparisons
        # 1. Inter-rater Kappa comparison (t-test)
        inter_t, inter_p = self.compare_kappas(inter_kappas1, inter_kappas2)
        
        # 2. Intra-rater Kappa comparison (t-test)
        intra_t, intra_p = self.compare_kappas(intra_kappas1, intra_kappas2)
        
        # 3. Disagreement rate comparison (Z-test)
        disagree_z, disagree_p = self.z_test_proportions(
            disagree_count1, total1, disagree_count2, total2
        )
        
        # Multiple comparison correction
        original_p_values = [inter_p, intra_p, disagree_p]
        corrected_p_values = self.benjamini_hochberg_correction(original_p_values)
        
        # Organize results
        all_results = {
            'condition1': {
                'inter_kappas': inter_kappas1,
                'intra_kappas': intra_kappas1,
                'total_cases': total1,
                'disagreement_rate': disagree_rate1,
                'disagreement_count': disagree_count1
            },
            'condition2': {
                'inter_kappas': inter_kappas2,
                'intra_kappas': intra_kappas2,
                'total_cases': total2,
                'disagreement_rate': disagree_rate2,
                'disagreement_count': disagree_count2
            },
            'comparison': {
                'inter_t': inter_t,
                'inter_p': inter_p,
                'inter_p_corrected': corrected_p_values[0],
                'intra_t': intra_t,
                'intra_p': intra_p,
                'intra_p_corrected': corrected_p_values[1],
                'disagree_z': disagree_z,
                'disagree_p': disagree_p,
                'disagree_p_corrected': corrected_p_values[2]
            }
        }
        
        logging.info("Comparison analysis complete")
        
        # Save results
        self.save_results(file1, file2, all_results)
        
        return all_results
    
    def save_results(self, file1: str, file2: str, results: Dict):
        """
        Save analysis results to text file
        """
        output_dir = Path(file1).parent or Path('.')
        
        file1_name = Path(file1).stem
        file2_name = Path(file2).stem
        
        output_filename = f"Reliability_Analysis_{file1_name}_vs_{file2_name}"
        output_file = output_dir / f"{output_filename}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8-sig') as f:
                f.write("=" * 70 + "\n")
                f.write("編碼信度分析報告\n")
                f.write("Coding Reliability Analysis Report\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"分析日期 Analysis Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Bootstrap 迭代次數 Iterations: {self.bootstrap_iterations}\n\n")
                
                f.write("統計方法 Statistical Methods:\n")
                f.write("  1. Cohen's Kappa (Inter-rater & Intra-rater reliability)\n")
                f.write("  2. Bootstrap resampling (1,000 iterations)\n")
                f.write("  3. Fisher's z transformation\n")
                f.write("  4. Independent samples t-test (Kappa comparison)\n")
                f.write("  5. Z-test (Disagreement rate comparison)\n")
                f.write("  6. Benjamini-Hochberg FDR correction\n\n")
                
                f.write("不一致率定義 Disagreement Rate Definition:\n")
                f.write("  任何模型編碼與標準編碼不一致的樣本數 / 樣本總數\n")
                f.write("  Proportion of cases where any LLM run disagrees with human standard\n\n")
                
                f.write("顯著水準 Significance Levels: p < 0.05 (*), p < 0.001 (**)\n")
                f.write("=" * 70 + "\n\n")
                
                # Condition 1
                cond1 = results['condition1']
                desc_inter1 = self.descriptive_stats(cond1['inter_kappas'])
                desc_intra1 = self.descriptive_stats(cond1['intra_kappas'])
                
                f.write(f"條件一 Condition 1: {Path(file1).name}\n")
                f.write("-" * 70 + "\n")
                f.write(f"樣本數 Sample Size: {cond1['total_cases']}\n\n")
                
                f.write(f"模型與標準編碼一致性 Inter-rater (LLM vs. Human):\n")
                f.write(f"  平均 Kappa Mean: {desc_inter1['mean']:.4f}\n")
                f.write(f"  標準差 SD: {desc_inter1['std']:.4f}\n")
                f.write(f"  各次編碼 Individual Runs: ")
                f.write(", ".join([f"Run{i+1}={k:.4f}" for i, k in enumerate(cond1['inter_kappas'])]))
                f.write("\n\n")
                
                f.write(f"模型內部一致性 Intra-rater (LLM Consistency):\n")
                f.write(f"  平均 Kappa Mean: {desc_intra1['mean']:.4f}\n")
                f.write(f"  標準差 SD: {desc_intra1['std']:.4f}\n\n")
                
                f.write(f"不一致率 Disagreement Rate: {cond1['disagreement_rate']:.4f} ")
                f.write(f"({cond1['disagreement_count']}/{cond1['total_cases']})\n\n")
                
                # Condition 2
                cond2 = results['condition2']
                desc_inter2 = self.descriptive_stats(cond2['inter_kappas'])
                desc_intra2 = self.descriptive_stats(cond2['intra_kappas'])
                
                f.write(f"條件二 Condition 2: {Path(file2).name}\n")
                f.write("-" * 70 + "\n")
                f.write(f"樣本數 Sample Size: {cond2['total_cases']}\n\n")
                
                f.write(f"模型與標準編碼一致性 Inter-rater (LLM vs. Human):\n")
                f.write(f"  平均 Kappa Mean: {desc_inter2['mean']:.4f}\n")
                f.write(f"  標準差 SD: {desc_inter2['std']:.4f}\n")
                f.write(f"  各次編碼 Individual Runs: ")
                f.write(", ".join([f"Run{i+1}={k:.4f}" for i, k in enumerate(cond2['inter_kappas'])]))
                f.write("\n\n")
                
                f.write(f"模型內部一致性 Intra-rater (LLM Consistency):\n")
                f.write(f"  平均 Kappa Mean: {desc_intra2['mean']:.4f}\n")
                f.write(f"  標準差 SD: {desc_intra2['std']:.4f}\n\n")
                
                f.write(f"不一致率 Disagreement Rate: {cond2['disagreement_rate']:.4f} ")
                f.write(f"({cond2['disagreement_count']}/{cond2['total_cases']})\n\n")
                
                # Statistical comparison
                comp = results['comparison']
                
                f.write("=" * 70 + "\n")
                f.write("統計比較結果 Statistical Comparison\n")
                f.write("=" * 70 + "\n\n")
                
                f.write(f"1. 模型與標準編碼 Kappa 比較 Inter-rater Comparison:\n")
                f.write(f"   (轉換後獨立樣本 t 檢驗 Independent t-test after Fisher's z transformation)\n")
                f.write(f"   t = {comp['inter_t']:.3f}, p = {comp['inter_p']:.6f}\n")
                f.write(f"   校正後 p 值 Corrected p = {comp['inter_p_corrected']:.6f} ")
                f.write(f"{self.get_significance_symbol(comp['inter_p_corrected'])}\n\n")
                
                f.write(f"2. 模型內部一致性 Kappa 比較 Intra-rater Comparison:\n")
                f.write(f"   (轉換後獨立樣本 t 檢驗 Independent t-test after Fisher's z transformation)\n")
                f.write(f"   t = {comp['intra_t']:.3f}, p = {comp['intra_p']:.6f}\n")
                f.write(f"   校正後 p 值 Corrected p = {comp['intra_p_corrected']:.6f} ")
                f.write(f"{self.get_significance_symbol(comp['intra_p_corrected'])}\n\n")
                
                f.write(f"3. 不一致率比較 Disagreement Rate Comparison:\n")
                f.write(f"   (Z 檢驗 Z-test for proportions)\n")
                f.write(f"   Z = {comp['disagree_z']:.3f}, p = {comp['disagree_p']:.6f}\n")
                f.write(f"   校正後 p 值 Corrected p = {comp['disagree_p_corrected']:.6f} ")
                f.write(f"{self.get_significance_symbol(comp['disagree_p_corrected'])}\n\n")
                
                f.write("=" * 70 + "\n")
                f.write("註 Notes:\n")
                f.write("多重比較校正：Benjamini-Hochberg FDR\n")
                f.write("Multiple comparison correction: Benjamini-Hochberg FDR\n")
                f.write("* p < 0.05, ** p < 0.001, n.s. = not significant\n")
                f.write("=" * 70 + "\n")
            
            print(f"\n✅ 結果已儲存 Results saved to: {output_file.name}")
            logging.info(f"Results saved to: {output_file}")
            
        except Exception as e:
            print(f"❌ 儲存結果時發生錯誤 Error saving results: {e}")
            logging.error(f"Error saving results to {output_file}: {e}")


def main():
    """
    Main program
    """
    print("=" * 70)
    print("Statistical Reliability Comparator for LLM Repeated Coding Analysis")
    print("LLM 重複編碼統計信度比較工具")
    print("=" * 70)
    print()
    
    file1 = input("輸入第一個檔案路徑 Enter path to first file (Prompt 1): ").strip()
    file2 = input("輸入第二個檔案路徑 Enter path to second file (Prompt 2): ").strip()
    
    bootstrap_input = input("Bootstrap 迭代次數 Iterations (預設 default 1000): ").strip()
    bootstrap_iterations = int(bootstrap_input) if bootstrap_input else 1000
    
    n_raters_input = input("編碼次數 Number of coding runs (預設 default 6 = 5 LLM + 1 Human): ").strip()
    n_raters = int(n_raters_input) if n_raters_input else 6
    
    print()
    print(f"設定 Settings: Bootstrap = {bootstrap_iterations}, Coding runs = {n_raters}")
    print("開始分析 Starting analysis...")
    print()
    
    comparator = ReliabilityComparator(
        bootstrap_iterations=bootstrap_iterations,
        n_raters=n_raters
    )
    
    try:
        results = comparator.compare_two_conditions(file1, file2)
        print()
        print("=" * 70)
        print("✅ 分析完成 Analysis complete!")
        print("=" * 70)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ 分析時發生錯誤 Error during analysis: {e}")
        print("=" * 70)
        logging.error(f"Error during analysis: {e}", exc_info=True)


if __name__ == "__main__":
    main()
