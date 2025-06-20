# LACA Reliability Analysis Toolkit

A comprehensive toolkit for LLM Annotation Consistency Assessment (LACA) featuring two complementary tools designed for different stages of prompt optimization and statistical analysis.

## Overview

This research toolkit provides two specialized tools for evaluating LLM coding reliability and consistency. The toolkit supports the complete workflow from prompt iterative optimization to formal statistical comparison analysis.

## Toolkit Components

### 1. Coding Quality Check Tool (編碼品質檢查工具)
A lightweight Python program specifically designed for LLM prompt iterative optimization. This tool processes tab-separated text files containing six coding values per row (five LLM codings plus one human standard coding) and automatically calculates Cohen's Kappa values for both LLM-standard coding reliability and LLM internal consistency.

**Key Features:**
- **Lightweight Design**: Optimized for quick iterative prompt testing
- **Real-time Quality Assessment**: Immediate feedback for prompt optimization
- **Detailed Inconsistency Reports**: Complete sample details with coder IDs and results
- **Dual Output Format**: TXT reliability reports and CSV result files
- **Problem Sample Identification**: Easy identification of problematic cases for prompt refinement

### 2. Statistical Comparison Analysis Tool (統計比較分析工具)
A comprehensive statistical analysis program designed to examine LLM coding differences under various conditions. This tool integrates a complete statistical analysis pipeline for rigorous research applications.

**Key Features:**
- **Advanced Statistical Methods**: Cohen's Kappa, Bootstrap resampling, Fisher's z transformation, independent t-tests, Z-tests
- **Multiple Comparison Correction**: Benjamini-Hochberg FDR correction for robust statistical inference
- **Dual Dataset Comparison**: Automated comparison between two coding datasets
- **Comprehensive Reporting**: Detailed statistical reports with descriptive statistics, category distributions, and corrected p-values
- **Non-parametric Validation**: Additional verification through non-parametric tests
- **Configurable Bootstrap**: Adjustable iterations for statistical robustness

## Output Files

### Coding Quality Check Tool
- **Detailed TXT Reliability Report**: Complete inconsistency sample details showing sample IDs, coder results, and final coding
- **CSV Result File**: Final coding results with original coding data for further analysis

### Statistical Comparison Analysis Tool
- **Comprehensive TXT Statistical Report**: 
  - Kappa descriptive statistics
  - Category distribution analysis
  - Statistical comparison results
  - Corrected p-values
  - Non-parametric test verification
- **Structured CSV Data File**: Kappa values and standard errors for each combination

## Requirements

- **Python Version**: 3.7 or higher
- **Required Packages**: 
  - numpy
  - scipy  
  - pandas
  - scikit-learn
  - pathlib
  - itertools
  - logging

## Installation

1. Clone this repository:
```bash
git clone https://github.com/duress/kappa-reliability-analyzer.git
cd kappa-reliability-analyzer
```

2. Install required packages:
```bash
pip install numpy scipy pandas scikit-learn
```

## Usage

### Coding Quality Check Tool (For Prompt Optimization)

```python
from basic_reliability_analyzer import analyze_coding_agreement

# Quick quality assessment for prompt iteration
df, reliability = analyze_coding_agreement(
    file_path='prompt_test_data.txt',
    delimiter='\t',
    encoding='utf-8',
    ai_columns=None,  # Auto-select first 5 columns (LLM codings)
    human_column=None,  # Auto-select last column (human standard)
    valid_categories=['a', 'b']
)
```

### Statistical Comparison Analysis Tool (For Formal Analysis)

```python
from statistical_comparison_analyzer import KappaReliabilityAnalyzer

# Comprehensive statistical comparison
analyzer = KappaReliabilityAnalyzer(
    n_raters=6,  # 5 LLM raters + 1 human rater
    bootstrap_iterations=1000
)

# Compare two different prompting conditions
analyzer.run_analysis('condition1_data.csv', 'condition2_data.csv')
```

## Input Data Format

### Tab-separated Text Files (Coding Quality Check Tool)
```
AI1	AI2	AI3	AI4	AI5	Human
a	a	b	a	a	a
b	b	b	b	b	b
a	a	a	a	a	a
```

### CSV Files (Statistical Comparison Analysis Tool)
```csv
AI1,AI2,AI3,AI4,AI5,Human
a,a,b,a,a,a
b,b,b,b,b,b
a,a,a,a,a,a
```

## Statistical Methods

### Reliability Assessment
- **Cohen's Kappa**: Inter-rater and intra-rater reliability measurement
- **Bootstrap Resampling**: Standard error estimation for robust inference
- **Fisher's z Transformation**: For statistical comparisons between conditions

### Hypothesis Testing
- **Independent Sample t-test**: Compare Kappa coefficients between conditions
- **Z-test**: AI-Human disagreement rate comparison
- **Mann-Whitney U Test**: Non-parametric validation

### Multiple Comparison Correction
- **Benjamini-Hochberg FDR**: Controls false discovery rate across multiple tests

## Advanced Features

### Automatic Detection and Processing
- **Character Encoding Detection**: Supports UTF-8, GBK, and other encodings
- **Multi-language Support**: International dataset compatibility
- **Flexible Column Selection**: Customizable AI and human coder assignments

### Quality Assurance
- **Data Validation**: Built-in checks for data integrity
- **Error Handling**: Robust error reporting and recovery
- **Inconsistency Analysis**: Detailed breakdown of disagreement patterns

## Recommended Workflow

### Phase 1: Prompt Development (Use Coding Quality Check Tool)
1. **Initial Testing**: Test prompts with small datasets
2. **Quality Assessment**: Run quick reliability checks
3. **Problem Identification**: Review inconsistency cases
4. **Prompt Refinement**: Iterate based on quality feedback
5. **Validation**: Confirm improved consistency

### Phase 2: Formal Analysis (Use Statistical Comparison Analysis Tool)
1. **Data Preparation**: Prepare final datasets for comparison
2. **Statistical Analysis**: Run comprehensive Bootstrap analysis
3. **Multiple Comparison**: Review corrected statistical results
4. **Validation**: Check non-parametric confirmations
5. **Reporting**: Generate final research reports

### Integrated Approach
The toolkit is designed for seamless integration: start with the Coding Quality Check Tool for rapid prompt optimization, then proceed to the Statistical Comparison Analysis Tool for rigorous statistical validation.

## Output Interpretation

### Kappa Values
- **> 0.8**: Excellent agreement
- **0.6-0.8**: Good agreement  
- **0.4-0.6**: Moderate agreement
- **< 0.4**: Poor agreement

### Statistical Significance (After FDR Correction)
- **p < 0.001**: *** (highly significant)
- **p < 0.01**: ** (very significant)
- **p < 0.05**: * (significant)
- **p ≥ 0.05**: ns (not significant)

## Example Output

### Coding Quality Check Tool Output
```
=== Analysis Summary ===
Number of AI coders: 5
Total cases: 150

=== Kappa Statistics ===
Average inter-rater Kappa (AI vs. Human): 0.7234
Average intra-rater Kappa (AI vs. AI): 0.8123

=== Disagreement Analysis ===
AI-Human Disagreement Rate: 0.2133 (32/150 cases)
AI Internal Disagreement: 18/150 cases where AIs disagree among themselves
```

### Statistical Comparison Analysis Tool Output
```
=== Statistical Comparison Results ===
Methods: Fisher's z transformation + Independent t-test

Inter-rater Comparison: t=2.456, p=0.014532, Cohen's d=0.423
Multiple Comparison Corrected p-values (Benjamini-Hochberg):
Inter-rater Comparison (Corrected): p=0.021798 *
```

## Applications

- **LLM Prompt Engineering**: Optimize prompts for consistent annotation
- **Content Analysis Research**: Evaluate LLM reliability for systematic coding
- **Machine Learning Validation**: Assess model consistency across conditions
- **Quality Control**: Monitor annotation quality in production systems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this toolkit in your research, please cite:

```bibtex
@software{laca_reliability_toolkit,
  title={LACA Reliability Analysis Toolkit: Tools for LLM Annotation Consistency Assessment},
  author={Ko, Lu-Yen},
  year={2025},
  url={https://github.com/duress/kappa-reliability-analyzer}
}
```

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub.

---

**Note**: This toolkit is designed for research applications in LLM annotation consistency assessment. The two-stage approach (quality check → statistical analysis) provides both rapid feedback for prompt development and rigorous validation for research publication.
