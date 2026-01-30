import re
import sys
import csv

def validate_sku(sku):
    """
    Validates if a string follows the Nike SKU format:
    2 Letters + 4 Numbers + Hyphen + 3 Numbers
    Example: BA5403-010
    """
    pattern = r"^[A-Z]{2}[0-9]{4}-[0-9]{3}$"
    return bool(re.match(pattern, sku))

def check_csv(file_path):
    """
    Reads the master metadata CSV and checks every SKU.
    """
    print(f"🔍 Scanning {file_path} for errors...")
    errors = 0
    row_count = 0
    
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row_count += 1
                sku = row.get('sku', '').strip()
                if not validate_sku(sku):
                    print(f"❌ INVALID SKU at Row {row_count}: '{sku}' (Name: {row.get('name')})")
                    errors += 1
                else:
                    print(f"✅ Valid: {sku}")
        
        print("-" * 30)
        if errors == 0:
            print("🎉 SUCCESS: All SKUs are valid.")
            sys.exit(0)
        else:
            print(f"⚠️ FOUND {errors} ERRORS.")
            sys.exit(1)
            
    except FileNotFoundError:
        print("Error: data/master_metadata.csv not found.")

if __name__ == "__main__":
    # Default to checking the master file relative to root
    check_csv("data/master_metadata.csv")
