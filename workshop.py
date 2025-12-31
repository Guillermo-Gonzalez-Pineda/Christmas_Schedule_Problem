from typing import List
from family import Family

class WorkshopDay:
    """
    Manages the daily capacity and assigned families for a specific workshop day.
    """
    MAX_CAPACITY: int = 300
    MIN_CAPACITY: int = 100

    def __init__(self, day_id: int) -> None:
        self.day_id: int = day_id
        self.assigned_families: List[Family] = []
        self.current_occupancy: int = 0

    def add_family(self, family: Family) -> None:
        """Registers a family to this day and updates occupancy."""
        self.assigned_families.append(family)
        self.current_occupancy += family.n_members