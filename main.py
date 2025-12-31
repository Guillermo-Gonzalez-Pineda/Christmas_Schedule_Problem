"""
Main Entry Point - MODEL A (Maximization)
"""
import os
from solution_manager import SolutionManager
from generate_data import create_dummy_data

# Configuration
DATA_DIR = os.path.join(os.path.dirname(__file__), '.', 'data')
INPUT_FILE = 'test_data_5000.csv'
OUTPUT_FILE = 'submission_modelA.csv'

def main() -> None:
    print("========================================")
    print("   SANTA WORKSHOP OPTIMIZER - MODEL A   ")
    print("========================================")

    input_path = os.path.join(DATA_DIR, INPUT_FILE)
    output_path = os.path.join(DATA_DIR, OUTPUT_FILE)

    # Check input
    if not os.path.exists(input_path):
        print(f"⚠️  Input file not found: {input_path}")
        print("   Generating test data...")
        create_dummy_data(INPUT_FILE, num_families=5000, mode='stressed')

    # Run Process
    manager = SolutionManager()
    
    try:
        manager.load_data(input_path)
        manager.solve()
        manager.generate_submission(output_path)
    except Exception as e:
        print(f"❌ Critical Error: {e}")

if __name__ == "__main__":
    main()