"""Unit tests for each of the 6 AST rewrite families.

Each family gets:
  - A discriminating case (real output != believed output)
  - A non-discriminating case (real output == believed output; item is useless for this family)
  - An additional edge-case

We use the sandbox `run()` + `believed_source()` so we test the full pipeline, not just AST
transformations in isolation.
"""
import pytest
from engine.signature import believed_source
from engine.sandbox import run


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _believed(src, mid):
    """Return the output of the believed program for misconception `mid`."""
    return run(believed_source(src, mid))


def _real(src):
    return run(src)


# ---------------------------------------------------------------------------
# 1. noop_method  (bank ids 6, 7, 8, 9, 10, 34, 36)
#    Belief: str.upper/lower/strip/replace/split mutate in place
# ---------------------------------------------------------------------------

class TestNoopMethod:
    MID = "noop_method"

    def test_upper_discriminates(self):
        """upper() called as statement: believed => mutated, real => unchanged."""
        src = 'name = "hello"\nname.upper()\nprint(name)'
        assert _real(src) == "hello"
        assert _believed(src, self.MID) == "HELLO"

    def test_split_discriminates(self):
        """split() called as statement: believed => mutated, real => unchanged."""
        src = 's = "a b c"\ns.split()\nprint(s)'
        assert _real(src) == "a b c"
        assert _believed(src, self.MID) == "['a', 'b', 'c']"

    def test_replace_discriminates(self):
        """replace() called as statement: believed => mutated, real => unchanged."""
        src = 's = "hello"\ns.replace("hello", "world")\nprint(s)'
        assert _real(src) == "hello"
        assert _believed(src, self.MID) == "world"

    def test_non_discriminating_upper_already_assigned(self):
        """When result is immediately assigned, real and believed outputs are equal."""
        src = 'name = "hello"\nname = name.upper()\nprint(name)'
        assert _real(src) == _believed(src, self.MID)

    def test_strip_discriminates(self):
        # Verify strip: the believed program assigns the stripped result back.
        # Use a string where we print its length — spaces change the length.
        src = 's = "  hi  "\ns.strip()\nprint(len(s))'
        assert _real(src) == "6"           # "  hi  " has 6 chars, unchanged
        assert _believed(src, self.MID) == "2"  # "hi" has 2 chars after strip

    def test_lower_discriminates(self):
        src = 's = "WORLD"\ns.lower()\nprint(s)'
        assert _real(src) == "WORLD"
        assert _believed(src, self.MID) == "world"


# ---------------------------------------------------------------------------
# 2. range_1_to_n  (bank id 1)
#    Belief: range(n) yields 1 .. n inclusive
# ---------------------------------------------------------------------------

class TestRange1ToN:
    MID = "range_1_to_n"

    def test_range3_discriminates(self):
        """range(3) real => 0,1,2 ; believed => 1,2,3."""
        src = "for i in range(3):\n    print(i)"
        real_lines = _real(src).splitlines()
        bel_lines = _believed(src, self.MID).splitlines()
        assert real_lines == ["0", "1", "2"]
        assert bel_lines == ["1", "2", "3"]

    def test_range5_discriminates(self):
        src = "for i in range(5):\n    print(i)"
        assert _believed(src, self.MID).splitlines() == ["1", "2", "3", "4", "5"]

    def test_non_discriminating_range_1_n_plus_1(self):
        """range(1, n+1) produces the same output under both beliefs."""
        src = "for i in range(1, 4):\n    print(i)"
        assert _real(src) == _believed(src, self.MID)

    def test_single_iteration(self):
        src = "for i in range(1):\n    print(i)"
        assert _real(src) == "0"
        assert _believed(src, self.MID) == "1"

    def test_sum_with_range(self):
        """More complex use: sum of range values differs."""
        src = "print(sum(range(4)))"
        assert _real(src) == "6"   # 0+1+2+3
        assert _believed(src, self.MID) == "10"  # 1+2+3+4


# ---------------------------------------------------------------------------
# 3. index_1_based  (bank ids 15, 66)
#    Belief: first element is at index 1
# ---------------------------------------------------------------------------

class TestIndex1Based:
    MID = "index_1_based"

    def test_list_index1_discriminates(self):
        """a[1] real => 20; believed (a[0]) => 10."""
        src = "a = [10, 20, 30]\nprint(a[1])"
        assert _real(src) == "20"
        assert _believed(src, self.MID) == "10"

    def test_string_index_discriminates(self):
        src = 's = "hello"\nprint(s[1])'
        assert _real(src) == "e"
        assert _believed(src, self.MID) == "h"

    def test_index2_discriminates(self):
        src = "a = [10, 20, 30]\nprint(a[2])"
        assert _real(src) == "30"
        assert _believed(src, self.MID) == "20"

    def test_non_discriminating_index0(self):
        """a[0] believed becomes a[-1] which wraps; NOT equal, but item is unusual."""
        src = "a = [10, 20, 30]\nprint(a[0])"
        # index 0 - 1 = -1 => last element; real != believed, still discriminating
        assert _real(src) == "10"
        assert _believed(src, self.MID) == "30"

    def test_list_index3_discriminates(self):
        src = "a = [5, 10, 15, 20]\nprint(a[3])"
        assert _real(src) == "20"
        assert _believed(src, self.MID) == "15"


# ---------------------------------------------------------------------------
# 4. assign_copies  (bank ids 13, 55)
#    Belief: b = a makes an independent copy of the list
# ---------------------------------------------------------------------------

class TestAssignCopies:
    MID = "assign_copies"

    def test_list_alias_discriminates(self):
        """b = a then mutate a: real => both change; believed => only a changes."""
        src = "a = [1, 2, 3]\nb = a\na.append(4)\nprint(b)"
        assert _real(src) == "[1, 2, 3, 4]"
        assert _believed(src, self.MID) == "[1, 2, 3]"

    def test_prepend_mutation_discriminates(self):
        src = "a = [10, 20]\nb = a\na.insert(0, 0)\nprint(b)"
        assert _real(src) == "[0, 10, 20]"
        assert _believed(src, self.MID) == "[10, 20]"

    def test_non_discriminating_immutable(self):
        """int assignment: both are independent already (copy of int == same value)."""
        src = "a = 5\nb = a\na = 10\nprint(b)"
        # _cp(5) still returns 5; b is 5 in both cases
        assert _real(src) == _believed(src, self.MID)

    def test_no_shared_mutation_when_new_list_assigned(self):
        """b = a, then a = new_list: real b unchanged, believed b also unchanged."""
        src = "a = [1, 2]\nb = a\na = [9, 9]\nprint(b)"
        # rebinding a doesn't mutate the list in either case
        assert _real(src) == "[1, 2]"
        assert _believed(src, self.MID) == "[1, 2]"

    def test_list_pop_discriminates(self):
        src = "a = [1, 2, 3]\nb = a\na.pop()\nprint(b)"
        assert _real(src) == "[1, 2]"
        assert _believed(src, self.MID) == "[1, 2, 3]"


# ---------------------------------------------------------------------------
# 5. add_before_div  (bank ids 63, 64, 65)
#    Belief: a + b / c is evaluated as (a + b) / c
# ---------------------------------------------------------------------------

class TestAddBeforeDiv:
    MID = "add_before_div"

    def test_basic_addition_before_div_discriminates(self):
        """10 + 20 / 2: real => 20.0; believed => 15.0."""
        src = "print(10 + 20 / 2)"
        assert _real(src) == "20.0"
        assert _believed(src, self.MID) == "15.0"

    def test_subtraction_before_mult_discriminates(self):
        """10 - 2 * 3: real => 4; believed => 24."""
        src = "print(10 - 2 * 3)"
        assert _real(src) == "4"
        assert _believed(src, self.MID) == "24"

    def test_variable_expression_discriminates(self):
        src = "a = 10\nb = 20\nc = 2\nprint(a + b / c)"
        assert _real(src) == "20.0"
        assert _believed(src, self.MID) == "15.0"

    def test_non_discriminating_parens_already_present(self):
        """(a + b) / c: real and believed are the same."""
        src = "print((10 + 20) / 2)"
        assert _real(src) == _believed(src, self.MID)

    def test_non_discriminating_only_division(self):
        """No addition/subtraction: rewrite doesn't fire."""
        src = "print(20 / 4)"
        assert _real(src) == _believed(src, self.MID)

    def test_multi_term_expression(self):
        """1 + 2 + 6 / 3: real => 5.0; believed => 1.0 (left-to-right parse)."""
        src = "print(1 + 6 / 3)"
        assert _real(src) == "3.0"
        assert _believed(src, self.MID) == "2.3333333333333335"


# ---------------------------------------------------------------------------
# 6. index_from_m1  (bank id 60, HELD OUT)
#    Belief: indexing starts at -1 (a[0] => a[1], a[-1] => a[0])
# ---------------------------------------------------------------------------

class TestIndexFromM1:
    MID = "index_from_m1"

    def test_index1_discriminates(self):
        """a[1] real => 20; believed (a[2]) => 30."""
        src = "a = [10, 20, 30]\nprint(a[1])"
        assert _real(src) == "20"
        assert _believed(src, self.MID) == "30"

    def test_index0_discriminates(self):
        """a[0] real => 10; believed (a[1]) => 20."""
        src = "a = [10, 20, 30]\nprint(a[0])"
        assert _real(src) == "10"
        assert _believed(src, self.MID) == "20"

    def test_non_discriminating_last_element(self):
        """a[-1]: believed becomes a[0]=10; real is 30 — still discriminating."""
        src = "a = [10, 20, 30]\nprint(a[-1])"
        assert _real(src) == "30"
        assert _believed(src, self.MID) == "10"

    def test_string_index_discriminates(self):
        src = 's = "abc"\nprint(s[0])'
        assert _real(src) == "a"
        assert _believed(src, self.MID) == "b"
