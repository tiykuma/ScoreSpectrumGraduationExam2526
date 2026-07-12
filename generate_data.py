import csv
import random

def clip(val, min_val, max_val):
    return max(min_val, min(val, max_val))

def round_grading(val):
    # Round to the nearest 0.25
    return round(val * 4) / 4

def generate_mock_data(num_students=1000):
    random.seed(42)
    
    headers = [
        'A00', 'A01', 'D01', 'A00 TOAN X2', 'A01 TOAN X2',
        'A00 2025', 'A01 2025', 'D01 2025', 'A00 TOAN X2 2025', 'A01 TOAN X2 2025'
    ]
    
    rows = []
    for i in range(num_students):
        # Base Subject Scores for 2026
        math_26 = clip(random.normalvariate(6.8, 1.4), 0, 10)
        phys_26 = clip(random.normalvariate(6.6, 1.3), 0, 10)
        chem_26 = clip(random.normalvariate(6.3, 1.3), 0, 10)
        eng_26 = clip(random.normalvariate(6.0, 1.7), 0, 10)
        lit_26 = clip(random.normalvariate(7.0, 0.9), 0, 10)
        
        # Base Subject Scores for 2025 (slightly different distribution)
        math_25 = clip(random.normalvariate(6.5, 1.5), 0, 10)
        phys_25 = clip(random.normalvariate(6.3, 1.4), 0, 10)
        chem_25 = clip(random.normalvariate(6.1, 1.4), 0, 10)
        eng_25 = clip(random.normalvariate(5.5, 1.8), 0, 10)
        lit_25 = clip(random.normalvariate(6.7, 1.0), 0, 10)
        
        # Round individual subjects (though we sum them first, then round the blocks)
        # 2026 Blocks
        a00_26 = round_grading(math_26 + phys_26 + chem_26)
        a01_26 = round_grading(math_26 + phys_26 + eng_26)
        d01_26 = round_grading(math_26 + lit_26 + eng_26)
        a00_t2_26 = round_grading(math_26 * 2 + phys_26 + chem_26)
        a01_t2_26 = round_grading(math_26 * 2 + phys_26 + eng_26)
        
        # 2025 Blocks
        a00_25 = round_grading(math_25 + phys_25 + chem_25)
        a01_25 = round_grading(math_25 + phys_25 + eng_25)
        d01_25 = round_grading(math_25 + lit_25 + eng_25)
        a00_t2_25 = round_grading(math_25 * 2 + phys_25 + chem_25)
        a01_t2_25 = round_grading(math_25 * 2 + phys_25 + eng_25)
        
        row = [
            a00_26, a01_26, d01_26, a00_t2_26, a01_t2_26,
            a00_25, a01_25, d01_25, a00_t2_25, a01_t2_25
        ]
        rows.append(row)
        
    with open('Diem20252026.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
        
    print("Generated Diem20252026.csv with 1000 rows successfully.")

if __name__ == '__main__':
    generate_mock_data()
