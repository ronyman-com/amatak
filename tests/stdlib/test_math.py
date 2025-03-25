import pytest
import math
from amatak.stdlib import mathlib
from amatak.errors import AmatakError

class TestMath:
    @pytest.fixture
    def m(self):
        return mathlib.Math()

    def test_constants(self, m):
        # Test mathematical constants
        assert m.PI == pytest.approx(math.pi)
        assert m.E == pytest.approx(math.e)
        assert m.TAU == pytest.approx(math.tau)

    def test_basic_ops(self, m):
        # Test basic operations
        assert m.abs(-5) == 5
        assert m.abs(3.14) == 3.14
        assert m.floor(3.9) == 3
        assert m.ceil(3.1) == 4
        assert m.round(3.5) == 4
        assert m.round(3.4) == 3

    def test_power_roots(self, m):
        # Test power and roots
        assert m.sqrt(16) == 4
        assert m.pow(2, 3) == 8
        assert m.pow(4, 0.5) == 2
        assert m.exp(1) == pytest.approx(math.e)
        
        with pytest.raises(AmatakError):
            m.sqrt(-1)

    def test_logarithms(self, m):
        # Test logarithmic functions
        assert m.log(math.e) == pytest.approx(1)
        assert m.log10(100) == 2
        assert m.log2(8) == 3
        
        with pytest.raises(AmatakError):
            m.log(0)

    def test_trigonometry(self, m):
        # Test trigonometric functions
        assert m.sin(math.pi/2) == pytest.approx(1)
        assert m.cos(math.pi) == pytest.approx(-1)
        assert m.tan(math.pi/4) == pytest.approx(1)
        
        # Test degrees conversion
        assert m.sin(m.radians(90)) == pytest.approx(1)
        assert m.degrees(math.pi) == pytest.approx(180)

    def test_random(self, m):
        # Test random number generation
        for _ in range(10):
            r = m.random()
            assert 0 <= r <= 1
        
        for _ in range(10):
            r = m.rand_int(1, 10)
            assert 1 <= r <= 10
        
        with pytest.raises(AmatakError):
            m.rand_int(10, 1)

    def test_statistics(self, m):
        # Test statistical functions
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        assert m.mean(data) == 3.0
        assert m.median(data) == 3.0
        assert m.stdev(data) == pytest.approx(1.5811, rel=1e-4)
        assert m.variance(data) == pytest.approx(2.5)

    def test_min_max(self, m):
        # Test min/max functions
        assert m.max(1, 2, 3) == 3
        assert m.min(1, 2, 3) == 1
        assert m.max([1, 2, 3]) == 3
        assert m.min([1, 2, 3]) == 1

    def test_clamp(self, m):
        # Test clamping function
        assert m.clamp(5, 0, 10) == 5
        assert m.clamp(-1, 0, 10) == 0
        assert m.clamp(11, 0, 10) == 10

    def test_lerp(self, m):
        # Test linear interpolation
        assert m.lerp(0, 10, 0.5) == 5
        assert m.lerp(10, 20, 0.25) == 12.5