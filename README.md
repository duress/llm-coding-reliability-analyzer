# Kappa Reliability Analyzer

A comprehensive statistical analysis tool for evaluating inter-coder reliability between LLM and human annotations using Cohen's Kappa, Bootstrap resampling, and multiple comparison corrections.

## Overview

The Kappa Reliability Analyzer is a specialized statistical analysis program designed to examine LLM coding differences under various conditions. This tool integrates a complete statistical analysis pipeline including Cohen's Kappa coefficient calculation, Bootstrap resampling standard error estimation, Fisher's z transformation, independent sample t-tests, Z-tests, and Benjamini-Hochberg FDR multiple comparison corrections.

## Key Features

- **Comprehensive Statistical Methods**: Cohen's Kappa, Bootstrap resampling, Fisher's z transformation, independent t-tests, Z-tests
- **Multiple Comparison Correction**: Benjamini-Hochberg FDR correction for robust statistical inference  
- **Dual Dataset Analysis**: Compare two coding datasets automatically
- **Reliability Assessment**: Calculate reliability between LLM-standard coding and LLM internal consistency
- **Inconsistency Analysis**: Detailed disagreement rate analysis between AI and human coders
- **Multi-language Support**: Automatic character encoding detection for international datasets
- **Configurable Bootstrap**: Adjustable Bootstrap iterations for statistical robustness

## Output Files

The tool generates two types of output files:

### 1. Detailed TXT Statistical Report
- Kappa descriptive statistics
- Category distribution analysis  
- Statistical comparison results
- Corrected p-values
- Non-parametric test verification

### 2. Structured CSV Data File
- Records Kappa values and standard errors for each combination
- Suitable for further statistical analysis or visualization

## Requirements

- **Python Version**: 3.7 or higher
- **Required Packages**: 
  - numpy
  - scipy  
  - pandas
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
pip install numpy scipy pandas
```

## Usage

### Basic Usage

```python
from kappa_analyzer import KappaReliabilityAnalyzer

# Initialize the analyzer
analyzer = KappaReliabilityAnalyzer(
    n_raters=4,  # Number of AI raters + 1 human rater
    bootstrap_iterations=1000
)

# Run analysis
analyzer.run_analysis('dataset1.csv', 'dataset2.csv')
```

### Configuration Options

- `n_raters`: Total number of raters (AI raters + human rater)
- `bootstrap_iterations`: Number of Bootstrap iterations (default: 1000)

### Input Data Format

Your CSV files should contain coding data where:
- Each row represents a case/item to be coded
- Each column represents a rater (AI1, AI2, AI3, Human)
- Values should be categorical codes

Example:
```csv
AI1,AI2,AI3,Human
1,1,2,1
2,2,2,2
1,1,1,1
...
```

## Statistical Methods

### Core Analyses
- **Cohen's Kappa**: Inter-rater reliability measurement
- **Bootstrap Resampling**: Standard error estimation
- **Fisher's z Transformation**: For statistical comparisons
- **Independent Sample t-test**: Compare Kappa coefficients between conditions
- **Z-test**: AI-Human disagreement rate comparison

### Multiple Comparison Correction
- **Benjamini-Hochberg FDR**: Controls false discovery rate across multiple tests

### Validation
- **Mann-Whitney U Test**: Non-parametric verification of parametric results

## Output Interpretation

### Kappa Values
- **> 0.8**: Excellent agreement
- **0.6-0.8**: Good agreement  
- **0.4-0.6**: Moderate agreement
- **< 0.4**: Poor agreement

### Statistical Significance
- **p < 0.001**: *** (highly significant)
- **p < 0.01**: ** (very significant)
- **p < 0.05**: * (significant)
- **p ≥ 0.05**: ns (not significant)

## Example Output Structure

```
=== Kappa Analysis Results (Bootstrap Iterations: 1000) ===
Input Files: prompt1.csv vs prompt2.csv
Statistical Methods: Fisher's z transformation + Independent t-test

Prompt1 File: prompt1.csv
Data: 150 cases
Inter-rater Reliability (AI vs Human): μ=0.7234, σ=0.0456
Intra-rater Reliability (AI vs AI): μ=0.8123, σ=0.0312
AI-Human Disagreement Rate: 0.2133 (32/150 cases)

=== Statistical Comparison Results ===
Inter-rater Comparison: t=2.456, p=0.014532, Cohen's d=0.423
Multiple Comparison Corrected p-values (Benjamini-Hochberg):
Inter-rater Comparison (Corrected): p=0.021798 *
```

## Advanced Features

### Automatic Encoding Detection
The tool automatically detects character encoding, supporting various international datasets.

### Disagreement Analysis
Detailed breakdown of AI-Human disagreement patterns and distributions.

### Quality Assurance
Built-in validation checks and error handling for robust analysis.

## Recommended Workflow

1. **Data Preparation**: Ensure coding data is in proper CSV format
2. **Quality Check**: Use with coding quality assessment tools
3. **Analysis**: Run reliability analysis with appropriate Bootstrap iterations
4. **Interpretation**: Review both TXT and CSV outputs
5. **Prompt Optimization**: Use results to improve LLM prompting strategies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{kappa_reliability_analyzer,
  title={Kappa Reliability Analyzer: Statistical Tool for LLM Coding Reliability Assessment},
  author={Ko, Lu-Yen},
  year={2025},
  url={https://github.com/duress/kappa-reliability-analyzer}
}
```

## Support

For questions, bug reports, or feature requests, please open an issue on GitHub.

---

**Note**: This tool is designed for research purposes and statistical analysis of coding reliability. Ensure your data meets the assumptions of the statistical tests before interpretation.
