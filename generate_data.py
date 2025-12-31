"""
Test data generator for Santa Workshop Scheduling Problem.

Creates synthetic CSV datasets with configurable demand patterns
to stress-test the optimization pipeline.
"""

import pandas as pd
import random
import os
from typing import Literal


def create_dummy_data(
    filename: str, 
    num_families: int = 5000, 
    mode: Literal['uniform', 'stressed', 'blind_spot'] = 'stressed'
) -> None:
    """
    Generate synthetic family preference data for testing.
    
    Args:
        filename: Output CSV filename (e.g., 'test_data_5000.csv')
        num_families: Number of families to generate
        mode: Demand distribution pattern:
            - 'uniform': Random distribution across all days (easy)
            - 'stressed': 75% demand concentrated in days 1-25 (realistic/hard)
            - 'blind_spot': Limited to days 1-60 (specific constraint testing)
    """
    print(f"--- Generating {num_families} families in {mode.upper()} mode ---")
    
    data = []
    
    for i in range(num_families):
        fam_id = f"F{i:04d}"
        n_members = random.randint(2, 9)
        
        # Generate 10 unique preferred days based on mode
        prefs_set = set()
        
        while len(prefs_set) < 10:
            if mode == 'stressed':
                # Realistic scenario: heavy demand for holidays (days 1-25)
                day = random.randint(1, 25) if random.random() < 0.75 else random.randint(26, 100)
            elif mode == 'blind_spot':
                day = random.randint(1, 60)
            else:  # uniform
                day = random.randint(1, 100)
            
            prefs_set.add(day)
        
        prefs = list(prefs_set)
        random.shuffle(prefs)
        
        row = {
            'familyID': fam_id,
            'nrMembers': n_members,
            'solution': ''
        }
        
        for rank, day in enumerate(prefs):
            row[f'day{rank}'] = day
            
        data.append(row)

    df = pd.DataFrame(data)
    
    # Calculate total people
    total_people = df['nrMembers'].sum()
    
    # Write to data directory
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    
    df.to_csv(output_path, index=False)
    print(f"✅ File saved to: {output_path}")
    print(f"📊 Total people generated: {total_people:,}")


if __name__ == "__main__":
    NUM_FAMILIES = 5000
    FILENAME = "test_data_5000.csv"
    MODE = 'stressed'  # Options: 'uniform', 'stressed', 'blind_spot'
    
    create_dummy_data(FILENAME, NUM_FAMILIES, MODE)