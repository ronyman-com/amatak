import pytest
import math
from amatak.stdlib.math import Math

class TestMath:
    @pytest.fixture
    def math_lib(self):
        return Math()

    def test_basic_functions(self, math_lib):
        # Test basic math functions
        assert math_lib.sqrt(16) == 4.0
        assert math_lib.pow(2, 3) == 8.0
        assert math_lib.abs(-5) == 5
        assert math_lib.round(3.6) == 4

    def test_trigonometry(self, math_lib):
        # Test trigonometric functions
        assert math_lib.sin(math.pi/2) == pytest.approx(1.0)
        assert math_lib.cos(math.pi) == pytest.approx(-1.0)
        assert math_lib.tan(math.pi/4) == pytest.approx(1.0)

    def test_logarithmic(self, math_lib):
        # Test logarithmic functions
        assert math_lib.log(math.e) == pytest.approx(1.0)
        assert math_lib.log10(100) == pytest.approx(2.0)
        assert math_lib.exp(1) == pytest.approx(math.e)

    def test_statistics(self, math_lib):
        # Test statistical functions
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        assert math_lib.mean(data) == 3.0
        assert math_lib.median(data) == 3.0
        assert math_lib.stdev(data) == pytest.approx(1.5811, rel=1e-4)
        assert math_lib.variance(data) == pytest.approx(2.5)

    def test_random(self, math_lib):
        # Test random number generation
        for _ in range(10):
            val = math_lib.random()
            assert 0 <= val <= 1.0
        
        for _ in range(10):
            val = math_lib.rand_int(1, 10)
            assert 1 <= val <= 10

    def test_constants(self, math_lib):
        # Test mathematical constants
        assert math_lib.PI == pytest.approx(math.pi)
        assert math_lib.E == pytest.approx(math.e)
        assert math_lib.TAU == pytest.approx(2 * math.pi)

    def test_error_handling(self, math_lib):
        # Test error cases
        with pytest.raises(ValueError):
            math_lib.sqrt(-1)
        
        with pytest.raises(ValueError):
            math_lib.log(0)
        
        with pytest.raises(ValueError):
            math_lib.rand_int(10, 1)