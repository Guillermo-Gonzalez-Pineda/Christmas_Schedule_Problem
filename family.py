from typing import List

class Family:
    """
    Represents a family entity with their preferences and size.
    """
    def __init__(self, family_id: int, n_members: int, preferences: List[int]) -> None:
        self.id: int = family_id
        self.n_members: int = n_members
        self.preferences: List[int] = preferences
        self.assigned_day: int = -1  # -1 implies 'Unassigned'

    def assign_to(self, day: int) -> None:
        """Assigns the family to a specific workshop day."""
        self.assigned_day = day