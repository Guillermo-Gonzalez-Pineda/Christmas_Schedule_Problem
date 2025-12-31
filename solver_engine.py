"""
MIP Solver Engine - MODEL A (Strict / Semicontinuous)
Strategy: "Maximize Happiness" with strict Day Closing logic.
Rule: A day has either 0 people (Closed) OR between 100-300 (Open).
"""
import pyomo.environ as pyo
from pyomo.environ import SolverFactory, TerminationCondition
from typing import List, Dict, Any, Optional
from family import Family

class SantaSolver:
    # Happiness score per preference rank (Rank 0 = Top choice)
    HAPPINESS_POINTS = {
        0: 100, 1: 90, 2: 85, 3: 80, 4: 75, 
        5: 70, 6: 60, 7: 50, 8: 40, 9: 30
    }

    def __init__(self) -> None:
        self.model: Optional[pyo.ConcreteModel] = None
        self.results: Optional[Any] = None

    def solve(self, families: List[Family], days_range: List[int]) -> bool:
        print("   [Solver] Building Strict Model (Semicontinuous variables)...")
        self.model = pyo.ConcreteModel()

        # --- 1. SETS ---
        # Only create variables for valid preferences (Sparse Matrix approach)
        valid_assignments = []
        for fam in families:
            for day in fam.preferences:
                valid_assignments.append((fam.id, day))

        self.model.Assignments = pyo.Set(initialize=valid_assignments)
        self.model.Days = pyo.Set(initialize=days_range)
        self.model.Families = pyo.Set(initialize=[f.id for f in families])

        # --- 2. VARIABLES ---
        # x[fam_id, day]: 1 if family is assigned, 0 otherwise
        self.model.x = pyo.Var(self.model.Assignments, domain=pyo.Binary)

        # z[day]: 1 if Day is OPEN, 0 if CLOSED
        self.model.z = pyo.Var(self.model.Days, domain=pyo.Binary)

        # --- 3. OBJECTIVE (Maximize Happiness) ---
        def objective_rule(m):
            total_happiness = 0
            for f in families:
                for rank, day in enumerate(f.preferences):
                    # We only sum points if the assignment variable x is 1
                    total_happiness += m.x[f.id, day] * self.HAPPINESS_POINTS[rank]
            return total_happiness

        self.model.Obj = pyo.Objective(rule=objective_rule, sense=pyo.maximize)

        # --- 4. CONSTRAINTS ---

        # C1: Each family assigned to AT MOST 1 day (or none)
        def one_day_rule(m, fam_id):
            # We recover the family object to iterate only its preferences
            current_fam = next((f for f in families if f.id == fam_id), None)
            return sum(m.x[fam_id, d] for d in current_fam.preferences) <= 1
        
        self.model.OneDay = pyo.Constraint(self.model.Families, rule=one_day_rule)

        # Pre-calculate demand map for performance (Crucial for large datasets)
        day_demand_map = {d: [] for d in days_range}
        for f in families:
            for d in f.preferences:
                day_demand_map[d].append(f)

        # C2: Lower Bound (Opening Threshold)
        # Occupancy >= 100 * z[d]
        def min_opening_rule(m, d):
            if not day_demand_map[d]: 
                # If no one requests this day, force it closed (z=0)
                return 0 >= 100 * m.z[d]
            
            occupancy = sum(m.x[f.id, d] * f.n_members for f in day_demand_map[d])
            return occupancy >= 100 * m.z[d]
        
        self.model.MinOpen = pyo.Constraint(self.model.Days, rule=min_opening_rule)

        # C3: Upper Bound (Max Capacity)
        # Occupancy <= 300 * z[d]
        def max_opening_rule(m, d):
            if not day_demand_map[d]:
                return pyo.Constraint.Skip
            
            occupancy = sum(m.x[f.id, d] * f.n_members for f in day_demand_map[d])
            return occupancy <= 300 * m.z[d]
        
        self.model.MaxOpen = pyo.Constraint(self.model.Days, rule=max_opening_rule)

        # --- 5. EXECUTION ---
        print("   [Solver] Running CBC (Branch & Bound)...")
        optimizer = SolverFactory('cbc')
        optimizer.options['seconds'] = 450 
        optimizer.options['ratio'] = 0.01

        try:
            self.results = optimizer.solve(self.model, tee=True)
            status = self.results.solver.termination_condition
            print(f"   [Solver] Final Status: {status}")
            return status in [TerminationCondition.optimal, TerminationCondition.feasible, TerminationCondition.maxTimeLimit]
        except Exception as e:
            print(f"   [Error] Solver failed: {e}")
            return False

    def get_raw_assignments(self) -> Dict[int, int]:
        """Returns dictionary {fam_id: assigned_day}."""
        assignments = {}
        if self.model is None: return {}

        for (fam_id, day) in self.model.Assignments:
            if pyo.value(self.model.x[fam_id, day]) > 0.5:
                assignments[fam_id] = day
        return assignments