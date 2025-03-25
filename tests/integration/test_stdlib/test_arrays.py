import pytest
from amatak.stdlib.arrays import Array

class TestArrays:
    @pytest.fixture
    def array(self):
        return Array()

    def test_basic_operations(self, array):
        # Test basic array operations
        arr = array.create(5)
        
        # Set and get items
        array.set(arr, 0, 10)
        array.set(arr, 1, 20)
        assert array.get(arr, 0) == 10
        assert array.get(arr, 1) == 20
        
        # Length
        assert array.length(arr) == 5
        
        # Resize
        array.resize(arr, 3)
        assert array.length(arr) == 3

    def test_sorting(self, array):
        # Test sorting
        arr = array.create(5)
        for i in range(5):
            array.set(arr, i, 5 - i)
        
        array.sort(arr)
        for i in range(5):
            assert array.get(arr, i) == i + 1

    def test_searching(self, array):
        # Test searching
        arr = array.create(10)
        for i in range(10):
            array.set(arr, i, i * 2)
        
        assert array.find(arr, 6) == 3
        assert array.find(arr, 7) == -1

    def test_map_filter_reduce(self, array):
        # Test higher-order functions
        arr = array.create(5)
        for i in range(5):
            array.set(arr, i, i + 1)
        
        # Map
        doubled = array.map(arr, lambda x: x * 2)
        for i in range(5):
            assert array.get(doubled, i) == (i + 1) * 2
        
        # Filter
        evens = array.filter(arr, lambda x: x % 2 == 0)
        assert array.length(evens) == 2
        assert array.get(evens, 0) == 2
        assert array.get(evens, 1) == 4
        
        # Reduce
        sum_result = array.reduce(arr, lambda acc, x: acc + x, 0)
        assert sum_result == 15

    def test_error_handling(self, array):
        # Test error cases
        arr = array.create(3)
        
        with pytest.raises(IndexError):
            array.get(arr, 5)
        
        with pytest.raises(IndexError):
            array.set(arr, 5, 10)
        
        with pytest.raises(ValueError):
            array.create(-1)