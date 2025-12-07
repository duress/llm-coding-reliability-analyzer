LACA Reliability Analysis Toolkit
A user-friendly toolkit for LLM Annotation Consistency Assessment (LACA), featuring two tools designed for prompt optimization and statistical analysis. Perfect for researchers and non-programmers working with small datasets.Overview
This toolkit helps evaluate how consistent Large Language Models (LLMs) are when coding data compared to human coders. It includes two tools:Coding Quality Check Tool: For quick testing and improving LLM prompts.
Statistical Comparison Analysis Tool: For detailed statistical analysis of LLM performance across different conditions.
The toolkit supports the full workflow, from testing prompts to producing research-ready statistical reports.Toolkit ComponentsCoding Quality Check Tool
A simple Python program for testing and improving LLM prompts. It processes tab-separated text files with six columns (five LLM codings + one human coding) and calculates agreement metrics like Cohen's Kappa.

Key Features:Easy to Use: Designed for quick prompt testing, no coding expertise needed.
Instant Feedback: Shows how well LLMs agree with humans and each other.
Detailed Reports: Lists cases where coders disagree, with sample IDs and comments.
Dual Outputs: Saves results as a text report (.txt) and a spreadsheet (.csv).
Problem Spotting: Highlights cases needing prompt improvement.
2. Statistical Comparison Analysis Tool
A powerful tool for researchers to compare LLM coding performance across two datasets (e.g., different prompts or conditions). It provides detailed statistical analysis for formal studies.Key Features:Advanced Stats: Measures agreement (Cohen's Kappa), compares datasets, and checks reliability.
Error Correction: Adjusts results to avoid false positives (Benjamini-Hochberg method).
Compare Two Datasets: Analyzes differences between two sets of coding results.
Detailed Reports: Includes agreement stats, category distributions, and significance tests.
Extra Validation: Uses non-parametric tests to confirm results.
Customizable: Adjust the number of iterations for more robust analysis.
Input Data Format
Your data file should be tab-separated (.txt or .tsv) with exactly 6 or 7 columns:Columns 1-5: LLM coding results (e.g., 'a' or 'b')
Column 6: Human expert coding (e.g., 'a' or 'b')
Column 7 (optional): Comments or sample descriptions
Example data file (sample_data.txt):a	a	b	a	a	a	Sample comment here
b	b	b	a	b	b	Another sample
a	a	a	a	a	a	Perfect agreement case
b	a	b	b	b	b	Challenging case
a	b	a	a	a	a	Mixed agreement
Important Notes:Use tabs (not spaces) to separate columns
Only 'a' and 'b' categories are currently supported
Save as plain text file with .txt extension
No headers needed - data starts from row 1
Output Files
Coding Quality Check Tool
Text Report (*_reliability_results.txt): Detailed report with disagreement cases, including sample IDs, coder results, and comments.
CSV File (*_results.csv): Final coding results with original data for further analysis.
Statistical Comparison Analysis Tool
Text Report (Reliability_Analysis_*_vs_*_*.txt): Comprehensive stats, including:
Agreement scores (Kappa)
Category distributions
Statistical comparisons
Adjusted p-values
Non-parametric test results
CSV File (Reliability_Analysis_*_vs_*_*.csv): Agreement scores and errors for each coder pair.
Note: Running the tools multiple times may overwrite output files. To avoid this, rename files after each run or move them to a different folder.Requirements
Python Version: 3.7 or higher
Required Packages:
numpy
scipy
pandas
scikit-learn
pathlib (included with Python)
itertools (included with Python)
logging (included with Python)
Installation
For non-programmers, follow these steps to set up the toolkit:Install Python
Download Python 3.7 or higher from python.org
Run the installer and check "Add Python to PATH" during installation
Open a terminal (Command Prompt on Windows, Terminal on Mac/Linux) and type:
python --version
If it shows Python 3.7 or higher, you're ready.
Download the Toolkit
Download the ZIP file from GitHub: llm-coding-reliability-analyzer
Extract the ZIP file to a folder on your computer
Or, if you have Git installed:
git clone https://github.com/duress/llm-coding-reliability-analyzer.git
cd llm-coding-reliability-analyzer
Install Required Packages
In the terminal, navigate to the toolkit folder and run:

pip install numpy scipy pandas scikit-learn
If you see errors, try updating pip first:pip install --upgrade pip
pip install numpy scipy pandas scikit-learn
Quick Start Guide
For the Coding Quality Check Tool
Prepare your data as a tab-separated text file (see Input Data Format above)
Place the file in the same folder as the Python scripts
Open terminal in the toolkit folder
Run the tool:
python coding_quality_check.py
Enter file path when prompted (e.g., sample_data.txt)
Check results in the generated .txt and .csv files
For the Statistical Comparison Analysis Tool
Prepare two data files (e.g., different prompts or conditions)
Place both files in the toolkit folder
Run the tool:
python statistical_comparison_analysis.py
Follow prompts to select your two files
Choose bootstrap iterations (default: 1000, more = more accurate but slower)
Review results in the generated statistical report
Example Use CasesPrompt Development
Test different prompts to see which gives better agreement with human coders:

Create datasets with the same samples but different LLM prompts
Use the Coding Quality Check Tool to quickly assess each prompt
Use the Statistical Comparison Tool to formally compare the best candidates
2. Reliability Assessment
Measure how consistent your LLM is before using it for large-scale coding:Run your LLM 5 times on the same dataset
Use the Coding Quality Check Tool to assess reliability
Aim for Cohen's Kappa > 0.7 for good reliability
3. Method Comparison
Compare two different LLMs or prompt strategies statistically:Generate coding results from both methods
Use the Statistical Comparison Tool for formal statistical testing
Report results with confidence intervals and significance tests
Troubleshooting
Common Issues
"File not found" error:Check that your file is in the same folder as the Python scripts
Use the full file path (e.g., C:\Users\YourName\Documents\data.txt)
Make sure the file extension is correct (.txt)
"Invalid data format" error:Ensure you're using tabs (not spaces) to separate columns
Check that all coding values are 'a' or 'b'
Remove any extra spaces or special characters
Import errors:Make sure you've installed all required packages: pip install numpy scipy pandas scikit-learn
Try updating Python to the latest version
No output files generated:Check file permissions in the folder
Make sure the script ran without errors
Look for error messages in the terminal
Getting Help
If you encounter issues:Check the error message in the terminal
Verify your data format matches the examples
Try running with a smaller test dataset
Open an issue on the GitHub repository with your error message
Citation
If you use this toolkit in your research, please cite:[Your Name]. (2025). LACA Reliability Analysis Toolkit. 
GitHub repository: https://github.com/duress/llm-coding-reliability-analyzer
License
This project is open source and available under the MIT License.Contributing
Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests on GitHub.

