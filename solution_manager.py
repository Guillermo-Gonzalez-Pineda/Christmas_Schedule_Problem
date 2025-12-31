"""
Solution Manager - MODEL A (Top 10 Only)
Simplified single-stage orchestrator.
"""
import pandas as pd
from typing import Dict, List
from family import Family
from workshop import WorkshopDay
from solver_engine import SantaSolver

class SolutionManager:
    def __init__(self) -> None:
        self.families: Dict[int, Family] = {}
        self.days: Dict[int, WorkshopDay] = {}
        self.solver_engine = SantaSolver()
        self.input_data: pd.DataFrame = None

    def load_data(self, filepath: str) -> None:
        print(f"   [Manager] Loading data from {filepath}...")
        df = pd.read_csv(filepath)
        df.columns = [c.strip() for c in df.columns]
        
        self.input_data = df.copy()

        for _, row in df.iterrows():
            prefs = [int(row[f'day{i}']) for i in range(10)]
            fam_id = row['familyID']
            n_members = int(row['nrMembers'])
            self.families[fam_id] = Family(fam_id, n_members, prefs)

        for d in range(1, 101):
            self.days[d] = WorkshopDay(d)
        
        print(f"   [Manager] {len(self.families)} families loaded.")

    def solve(self) -> None:
        """Execute the single optimization stage."""
        print("\n   --- STARTING MODEL A: HAPPINESS MAXIMIZATION ---")
        print("   Strategy: Top 10 or Nothing. No minimum occupancy restriction.")
        print("   ------------------------------------------------------\n")
        
        success = self.solver_engine.solve(
            list(self.families.values()), 
            list(self.days.keys())
        )

        if success:
            self._apply_results()
            self.print_occupancy_stats()
        else:
            print("   [Manager] ❌ No feasible solution found.")

    def _apply_results(self) -> None:
        raw_assignments = self.solver_engine.get_raw_assignments()
        
        assigned_count = 0
        unassigned_count = 0

        for fam in self.families.values():
            fam.assigned_day = -1

        for fam_id, day in raw_assignments.items():
            if fam_id in self.families:
                fam = self.families[fam_id]
                fam.assign_to(day)
                self.days[day].add_family(fam)
                assigned_count += 1

        unassigned_count = len(self.families) - assigned_count

        print(f"   [Manager] Optimization completed.")
        print(f"   - Families Assigned: {assigned_count}")
        print(f"   - Families Without Slot: {unassigned_count}")
        
        if unassigned_count > 0:
            print(f"   [NOTE] {unassigned_count} families will be marked with 'x' in the solution")

    def generate_submission(self, output_path: str) -> None:
        print(f"   [Manager] Saving results to {output_path}...")
        
        if self.input_data is None:
            print("   [Error] No input data available. Call load_data first.")
            return
        
        output_df = self.input_data.copy()
        
        solution_map = {fam_id: fam.assigned_day for fam_id, fam in self.families.items()}
        output_df['solution'] = output_df['familyID'].map(solution_map)
        
        output_df['solution'] = output_df['solution'].apply(
            lambda x: 'x' if x == -1 else x
        )
        
        column_order = ['familyID', 'nrMembers'] + [f'day{i}' for i in range(10)] + ['solution']
        output_df = output_df[column_order]
        
        output_df.to_csv(output_path, index=False)
        print(f"   [Manager] ✅ Submission file saved successfully.")
        print(f"   Format: Comma-separated with all input columns + solution")

    def print_occupancy_stats(self) -> None:
        """Display detailed occupancy statistics for diagnostics."""
        occupancies = [d.current_occupancy for d in self.days.values()]
        min_occ = min(occupancies)
        max_occ = max(occupancies)
        avg_occ = sum(occupancies) / len(occupancies)
        
        empty_days = sum(1 for x in occupancies if x == 0)
        days_below_100 = sum(1 for x in occupancies if 0 < x < 100)
        days_over_300 = sum(1 for x in occupancies if x > 300)
        
        print("\n   --- WORKSHOP CAPACITY REPORT ---")
        print(f"   Minimum Occupancy: {min_occ}")
        print(f"   Maximum Occupancy: {max_occ} (Constraint: <= 300)")
        print(f"   Average Occupancy: {avg_occ:.1f}")
        print(f"   Empty Days (0 people): {empty_days}")
        print(f"   Days Below Minimum (1-99): {days_below_100}")
        print(f"   Days Over Maximum (>300): {days_over_300}")
        print("   ---------------------------------\n")