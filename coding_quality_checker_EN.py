import pandas as pd
import numpy as np
import os
import unicodedata
from typing import List, Tuple
from sklearn.metrics import cohen_kappa_score

def clean_path(path: str) -> str:
    """Remove Unicode control characters and normalize path"""
    cleaned = unicodedata.normalize('NFKC', path)
    cleaned = ''.join(c for c in cleaned if unicodedata.category(c)[0] != 'C')
    cleaned = os.path.normpath(cleaned)
    return cleaned

def validate_data(df: pd.DataFrame, ai_columns: List, human_column: str, valid_categories: List[str] = ['a', 'b']) -> bool:
    """Validate data format"""
    for i, row in df.iterrows():
        if not all(row[col] in valid_categories for col in ai_columns + [human_column]):
            print(f"Error: Row {i+1} contains invalid values: {[row[col] for col in ai_columns + [human_column]]}")
            return False
    return True

def calculate_ai_human_disagreement_rate(df: pd.DataFrame, ai_columns: List, human_column: str) -> Tuple[float, int, int, List[Tuple[int, str, List[str], str]]]:
    """
    Calculate AI-Human disagreement rate: proportion of cases where any AI disagrees with human
    """
    ai_codes = df[ai_columns].values
    human_codes = df[human_column].values
    comments = df.get('comment', pd.Series(["No comment available"] * len(df))).values
    
    total_cases = len(df)
    ai_human_disagreements = []
    disagreement_count = 0
    
    for i in range(len(ai_codes)):
        human_code = human_codes[i]
        ai_row = ai_codes[i]
        
        # Check if any AI disagrees with human
        if any(ai_code != human_code for ai_code in ai_row):
            disagreement_count += 1
            ai_human_disagreements.append((i + 1, comments[i], ai_row.tolist(), human_code))
    
    disagreement_rate = disagreement_count / total_cases if total_cases > 0 else 0.0
    
    return disagreement_rate, disagreement_count, total_cases, ai_human_disagreements

def calculate_inter_rater_reliability(df: pd.DataFrame, ai_columns: List, human_column: str) -> Tuple[float, List[float], float, List[float], List[Tuple[int, str, List[str]]], dict, Tuple[float, int, int, List]]:
    """Calculate inter-rater reliability (AI vs. Human) and intra-rater reliability (AI vs. AI)"""
    ai_codes = df[ai_columns].values
    human_codes = df[human_column].values
    comments = df.get('comment', pd.Series(["No comment available"] * len(df))).values
    
    # Inter-rater reliability: AI vs. Human
    inter_kappas = [cohen_kappa_score(human_codes, ai_codes[:, i]) for i in range(len(ai_columns))]
    inter_mean_kappa = np.mean(inter_kappas)
    
    # Intra-rater reliability: AI vs. AI
    intra_kappas = []
    for i in range(len(ai_columns)):
        for j in range(i + 1, len(ai_columns)):
            intra_kappas.append(cohen_kappa_score(ai_codes[:, i], ai_codes[:, j]))
    intra_mean_kappa = np.mean(intra_kappas) if intra_kappas else 0.0
    
    # AI internal disagreement cases (when AIs disagree among themselves)
    ai_internal_disagreements = []
    for i in range(len(ai_codes)):
        if len(set(ai_codes[i])) > 1:  # AIs disagree among themselves
            ai_internal_disagreements.append((i + 1, comments[i], ai_codes[i].tolist()))
    
    # Variability analysis: average Kappa for each coder
    coder_mean_kappa = {}
    for i, col in enumerate(ai_columns):
        coder_kappas = [cohen_kappa_score(ai_codes[:, i], ai_codes[:, j]) for j in range(len(ai_columns)) if j != i]
        coder_kappas.append(cohen_kappa_score(ai_codes[:, i], human_codes))  # Include Kappa with human
        coder_mean_kappa[col] = np.mean(coder_kappas) if coder_kappas else 0.0
    
    # Calculate AI-Human disagreement rate
    ai_human_disagreement_info = calculate_ai_human_disagreement_rate(df, ai_columns, human_column)
    
    return inter_mean_kappa, inter_kappas, intra_mean_kappa, intra_kappas, ai_internal_disagreements, coder_mean_kappa, ai_human_disagreement_info

def analyze_coding_agreement(file_path: str, delimiter='\t', encoding='utf-8', ai_columns=None, human_column=None, valid_categories=['a', 'b']):
    """
    Analyze coding agreement across multiple coders, prioritizing pairwise Cohen's Kappa,
    using human coding as final result when AI coders disagree.
    
    Parameters:
    file_path: Path to the file
    delimiter: Delimiter (default: tab)
    encoding: File encoding (default: utf-8)
    ai_columns: AI coding column indices or names (default: first five columns)
    human_column: Human coding column index or name (default: last column)
    valid_categories: List of valid categories (default: ['a', 'b'])
    """
    file_path = clean_path(file_path)
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: File '{file_path}' does not exist. Please check the file path.")
    
    # Read file
    try:
        df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, header=None)
        print(f"Successfully loaded file: {file_path}")
    except UnicodeDecodeError:
        print(f"Error: Cannot read file with {encoding} encoding, trying 'gbk' encoding...")
        try:
            df = pd.read_csv(file_path, delimiter=delimiter, encoding='gbk', header=None)
            print(f"Successfully loaded file (using gbk encoding): {file_path}")
        except Exception as e:
            raise Exception(f"Error: Cannot read file '{file_path}', please check encoding or file format. Error message: {str(e)}")
    except Exception as e:
        raise Exception(f"Error: Failed to read file '{file_path}'. Please check file format or delimiter. Error message: {str(e)}")
    
    if df.empty:
        raise ValueError("Error: File is empty, no data to analyze.")
    
    # Set AI and human coding columns
    if ai_columns is None:
        ai_columns = df.columns[:5].tolist()  # Default: first five columns as AI coding
    if human_column is None:
        human_column = df.columns[-1]  # Default: last column as human coding
    
    if not all(col in df.columns for col in ai_columns + [human_column]):
        raise ValueError(f"Error: Some specified coding columns {ai_columns + [human_column]} are not in the data.")
    
    # Assume the column after the last one (if exists) is the comment column
    comment_column = df.columns[-1] if len(df.columns) > len(ai_columns) + 1 else None
    if comment_column and comment_column != human_column:
        df = df.rename(columns={comment_column: 'comment'})
    else:
        df['comment'] = "No comment available"
    
    # Validate data
    if not validate_data(df, ai_columns, human_column, valid_categories):
        raise ValueError(f"Error: Invalid data format, only categories {valid_categories} are allowed.")
    
    # Remove missing values
    df = df.dropna(subset=ai_columns + [human_column])
    if df.empty:
        raise ValueError("Error: No valid data after removing missing values.")
    
    print(f"Loaded {len(df)} cases, AI coding columns: {ai_columns}, Human coding column: {human_column}")
    
    # Calculate reliability
    inter_mean_kappa, inter_kappas, intra_mean_kappa, intra_kappas, ai_internal_disagreements, coder_mean_kappa, ai_human_disagreement_info = calculate_inter_rater_reliability(df, ai_columns, human_column)
    
    # Unpack AI-Human disagreement info
    ai_human_disagreement_rate, ai_human_disagreement_count, total_cases, ai_human_disagreements = ai_human_disagreement_info
    
    # Calculate final coding (always use human coding as final result)
    df['final_coding'] = df[human_column]  # Always use human coding as final
    
    # Calculate agreement statistics
    ai_internal_unanimous = len(df) - len(ai_internal_disagreements)  # Cases where all AIs agree
    ai_human_agreement = total_cases - ai_human_disagreement_count  # Cases where all AIs agree with human
    
    # Output analysis results
    print("\n=== Analysis Summary ===")
    print(f"Number of AI coders: {len(ai_columns)}")
    print(f"Total cases: {total_cases}")
    
    print(f"\n=== Kappa Statistics ===")
    print(f"Average inter-rater Kappa (AI vs. Human): {inter_mean_kappa:.4f}")
    for i, kappa in enumerate(inter_kappas, 1):
        print(f"  AI{i} vs Human: {kappa:.4f}")
    
    print(f"\nAverage intra-rater Kappa (AI vs. AI): {intra_mean_kappa:.4f}")
    idx = 0
    for i in range(len(ai_columns)):
        for j in range(i + 1, len(ai_columns)):
            print(f"  AI{i+1} vs AI{j+1}: {intra_kappas[idx]:.4f}")
            idx += 1
    
    print(f"\nAverage Kappa for each coder (including comparison with human):")
    for col, mean_kappa in coder_mean_kappa.items():
        print(f"  Coder {col}: {mean_kappa:.4f}")
    
    print(f"\nOverall Kappa Statistics:")
    print(f"  Overall mean: {np.mean(list(coder_mean_kappa.values())):.4f}")
    print(f"  Standard deviation: {np.std(list(coder_mean_kappa.values())):.4f}")
    
    print(f"\n=== Disagreement Analysis ===")
    print(f"AI-Human Disagreement Rate: {ai_human_disagreement_rate:.4f} ({ai_human_disagreement_count}/{total_cases} cases)")
    print(f"  Definition: Proportion of cases where any AI rater disagrees with human rater")
    print(f"AI Internal Disagreement: {len(ai_internal_disagreements)}/{total_cases} cases where AIs disagree among themselves")
    print(f"AI Internal Agreement: {ai_internal_unanimous}/{total_cases} cases where all AIs agree")
    print(f"Perfect Agreement (All AIs + Human): {ai_human_agreement}/{total_cases} cases")
    
    if ai_human_disagreements:
        print(f"\nAI-Human disagreement cases (showing first 5 of {len(ai_human_disagreements)}):")
        for idx, comment, ai_codes, human_code in ai_human_disagreements[:5]:
            print(f"  Row {idx}: AI codes: {ai_codes}, Human code: {human_code}, Comment: {comment}")
    else:
        print("\nNo AI-Human disagreement cases found")
    
    if ai_internal_disagreements:
        print(f"\nAI internal disagreement cases (showing first 5 of {len(ai_internal_disagreements)}):")
        for idx, comment, ai_codes in ai_internal_disagreements[:5]:
            print(f"  Row {idx}: AI codes: {ai_codes}, Comment: {comment}")
    else:
        print("\nNo AI internal disagreement cases found")
    
    # Write report
    output_file = file_path.rsplit('.', 1)[0] + '_reliability_results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"=== Coding Reliability Analysis Results ===\n")
        f.write(f"Analysis date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"File: {os.path.basename(file_path)}\n")
        f.write(f"Total cases: {total_cases}\n")
        f.write(f"AI coders: {len(ai_columns)}, Human coder: 1\n\n")
        
        f.write(f"=== Kappa Statistics ===\n")
        f.write(f"Average inter-rater Kappa (AI vs. Human): {inter_mean_kappa:.4f}\n")
        for i, k in enumerate(inter_kappas, 1):
            f.write(f"AI{i}-Human Kappa: {k:.4f}\n")
        f.write(f"\nAverage intra-rater Kappa (AI vs. AI): {intra_mean_kappa:.4f}\n")
        idx = 0
        for i in range(len(ai_columns)):
            for j in range(i + 1, len(ai_columns)):
                f.write(f"AI{i+1}-AI{j+1} Kappa: {intra_kappas[idx]:.4f}\n")
                idx += 1
        f.write(f"\nAverage Kappa for each coder (including comparison with human):\n")
        for col, mean_kappa in coder_mean_kappa.items():
            f.write(f"Coder {col}: {mean_kappa:.4f}\n")
        f.write(f"\nOverall Kappa Statistics:\n")
        f.write(f"Overall mean: {np.mean(list(coder_mean_kappa.values())):.4f}\n")
        f.write(f"Standard deviation: {np.std(list(coder_mean_kappa.values())):.4f}\n")
        
        f.write(f"\n=== Disagreement Analysis ===\n")
        f.write(f"AI-Human Disagreement Rate: {ai_human_disagreement_rate:.4f} ({ai_human_disagreement_count}/{total_cases} cases)\n")
        f.write(f"Definition: Proportion of cases where any AI rater disagrees with human rater\n")
        f.write(f"AI Internal Disagreement: {len(ai_internal_disagreements)}/{total_cases} cases\n")
        f.write(f"AI Internal Agreement: {ai_internal_unanimous}/{total_cases} cases\n")
        f.write(f"Perfect Agreement (All AIs + Human): {ai_human_agreement}/{total_cases} cases\n\n")
        
        if ai_human_disagreements:
            f.write("=== AI-Human Disagreement Cases ===\n")
            for idx, comment, ai_codes, human_code in ai_human_disagreements:
                f.write(f"Row {idx}:\n")
                f.write(f"  AI codes: {ai_codes}\n")
                f.write(f"  Human code: {human_code}\n")
                f.write(f"  Comment: {comment}\n")
                f.write(f"  Final code: {human_code}\n\n")
        else:
            f.write("No AI-Human disagreement cases found\n")
        
        if ai_internal_disagreements:
            f.write("=== AI Internal Disagreement Cases ===\n")
            for idx, comment, ai_codes in ai_internal_disagreements:
                f.write(f"Row {idx}:\n")
                f.write(f"  AI codes: {ai_codes}\n")
                f.write(f"  Human code: {df.loc[idx-1, human_column]}\n")
                f.write(f"  Comment: {comment}\n")
                f.write(f"  Final code: {df.loc[idx-1, human_column]}\n\n")
        else:
            f.write("No AI internal disagreement cases found\n")
    
    # Output final coding to CSV
    output_csv = file_path.rsplit('.', 1)[0] + '_results.csv'
    result_df = pd.DataFrame({
        'final_coding': df['final_coding'],
        'ai_human_agreement': [human_codes[i] == ai_codes[i][0] and len(set(ai_codes[i])) == 1 for i in range(len(df))],
        'ai_internal_agreement': [len(set(ai_codes[i])) == 1 for i in range(len(df))],
        'comment': df['comment']
    })
    
    ai_codes = df[ai_columns].values
    human_codes = df[human_column].values
    
    for col in ai_columns + [human_column]:
        result_df[f'coder_{col}'] = df[col]
    result_df.to_csv(output_csv, index=True, index_label='row')
    
    print(f"\nResults saved to:")
    print(f"  - {output_csv} (final coding and agreement analysis)")
    print(f"  - {output_file} (detailed reliability analysis)")
    
    return df, (inter_mean_kappa, inter_kappas, intra_mean_kappa, intra_kappas, ai_internal_disagreements, ai_human_disagreement_info)

if __name__ == "__main__":
    try:
        file_path = input("Please enter your file path (e.g., C:/path/to/your_file.txt): ")
        df, reliability = analyze_coding_agreement(
            file_path=file_path,
            delimiter='\t',
            encoding='utf-8',
            ai_columns=None,  # Automatically select first five columns as AI coding
            human_column=None  # Automatically select last column as human coding
        )
    except Exception as e:
        print(e)