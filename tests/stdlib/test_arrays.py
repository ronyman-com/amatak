import pytest
from amatak.stdlib import arrays
from amatak.errors import AmatakError

class TestArrays:
    @pytest.fixture
    def arr(self):
        return arrays.Array()

    def test_create_and_length(self, arr):
        # Test array creation and length
        a = arr.create(5)
        assert arr.length(a) == 5

        # Test empty array
        empty = arr.create(0)
        assert arr.length(empty) == 0

    def test_get_set(self, arr):
        # Test get/set operations
        a = arr.create(3)
        arr.set(a, 0, "first")
        arr.set(a, 1, 42)
        arr.set(a, 2, [1, 2, 3])

        assert arr.get(a, 0) == "first"
        assert arr.get(a, 1) == 42
        assert arr.get(a, 2) == [1, 2, 3]

    def test_out_of_bounds(self, arr):
        # Test index error handling
        a = arr.create(2)
        with pytest.raises(AmatakError):
            arr.get(a, 2)
        with pytest.raises(AmatakError):
            arr.set(a, -1, "value")

    def test_push_pop(self, arr):
        # Test push/pop operations
        a = arr.create(0)
        arr.push(a, "item1")
        arr.push(a, "item2")
        
        assert arr.length(a) == 2
        assert arr.pop(a) == "item2"
        assert arr.length(a) == 1

    def test_shift_unshift(self, arr):
        # Test shift/unshift operations
        a = arr.create(0)
        arr.unshift(a, "end")
        arr.unshift(a, "start")
        
        assert arr.length(a) == 2
        assert arr.shift(a) == "start"
        assert arr.length(a) == 1

    def test_slice_splice(self, arr):
        # Test slice/splice operations
        a = arr.create(5)
        for i in range(5):
            arr.set(a, i, i+1)
        
        # Test slice
        sliced = arr.slice(a, 1, 4)
        assert arr.length(sliced) == 3
        assert arr.get(sliced, 0) == 2

        # Test splice
        removed = arr.splice(a, 1, 2, "a", "b")
        assert arr.length(a) == 5  # 5 - 2 + 2
        assert arr.get(a, 1) == "a"
        assert arr.length(removed) == 2

    def test_sort(self, arr):
        # Test sorting
        a = arr.create(5)
        for i in range(5):
            arr.set(a, i, 5 - i)
        
        arr.sort(a)
        for i in range(5):
            assert arr.get(a, i) == i + 1

    def test_map_filter_reduce(self, arr):
        # Test higher-order functions
        a = arr.create(5)
        for i in range(5):
            arr.set(a, i, i+1)
        
        # Map
        doubled = arr.map(a, lambda x: x * 2)
        assert arr.get(doubled, 0) == 2
        
        # Filter
        evens = arr.filter(a, lambda x: x % 2 == 0)
        assert arr.length(evens) == 2
        
        # Reduce
        sum = arr.reduce(a, lambda acc, x: acc + x, 0)
        assert sum == 15

    def test_find_index(self, arr):
        # Test search operations
        a = arr.create(5)
        for i in range(5):
            arr.set(a, i, i*2)
        
        assert arr.find_index(a, lambda x: x == 4) == 2
        assert arr.find_index(a, lambda x: x > 10) == -1

    def test_join(self, arr):
        # Test join operation
        a = arr.create(3)
        arr.set(a, 0, "a")
        arr.set(a, 1, "b")
        arr.set(a, 2, "c")
        
        assert arr.join(a, ",") == "a,b,c"
        assert arr.join(a, "") == "abc"