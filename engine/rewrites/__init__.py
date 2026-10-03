from .add_before_div import PlusBeforeDiv
from .assign_copies import AssignmentCopies
from .index_from_m1 import IndexStartsAtMinus1
from .index_one_based import Index1Based
from .noop_method import NoOpMethodAssigned
from .range_one_to_n import RangeOneToN

REGISTRY = [
    {"id": "noop_method", "transformer": NoOpMethodAssigned, "bank_ids": [6, 7, 8, 9, 10, 34, 36], "description": "Methods mutate in place", "held_out": False},
    {"id": "range_1_to_n", "transformer": RangeOneToN, "bank_ids": [1], "description": "range starts at one and includes n", "held_out": False},
    {"id": "index_1_based", "transformer": Index1Based, "bank_ids": [15, 66], "description": "Indexing starts at one", "held_out": False},
    {"id": "index_from_m1", "transformer": IndexStartsAtMinus1, "bank_ids": [60], "description": "Index -1 is first", "held_out": True},
    {"id": "assign_copies", "transformer": AssignmentCopies, "bank_ids": [13, 55], "description": "Assignment copies values", "held_out": False},
    {"id": "add_before_div", "transformer": PlusBeforeDiv, "bank_ids": [63, 64, 65], "description": "Addition happens before division", "held_out": False},
]
LIVE_REGISTRY = [entry for entry in REGISTRY if not entry["held_out"]]
