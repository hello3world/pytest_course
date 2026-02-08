from more_itertools import partition, windowed, interleave, rolling_aggregate
import pytest

class TestPartition:
    def test_happy_path(self):
        is_odd = lambda x: x % 2 != 0
        iterable = range(10)
        even_items, odd_items = partition(is_odd, iterable)
        actual_even_items = list(even_items)
        actual_odd_items = list(odd_items)
        expected_even_items = [0, 2, 4, 6, 8]
        expected_odd_items = [1, 3, 5, 7, 9]
        assert expected_even_items == actual_even_items
        assert expected_odd_items == actual_odd_items
       
    def test_different_values(self):
        iterable = [0, 1, False, True, '', ' ']
        false_items, true_items = partition(None, iterable)
        actual_false_result = list(false_items)
        actual_true_result = list(true_items)
        expected_false_items = [0, False, '']
        expected_true_items = [1, True, ' ']
        assert expected_false_items == actual_false_result
        assert expected_true_items == actual_true_result
        
    def test_partition_raises_error_if_not_iterable(self):
        not_iterable = 123
        with pytest.raises(TypeError):
            partition(None, not_iterable)
            
class TestWindowed:
    def test_happy_path(self):
            windowed_iter = windowed(seq=range(5), n=2, fillvalue=None, step=1)
            slices = list(windowed_iter)
            expected_slices = [(0, 1), (1, 2), (2, 3), (3, 4)]
            assert slices == expected_slices
            
    def test_step_two(self):
            windowed_iter = windowed(seq=range(5), n=2, fillvalue=None, step=2)
            slices = list(windowed_iter)
            expected_slices = [(0, 1), (2, 3), (4, None)]
            assert slices == expected_slices
            
    def test_window_size_is_equal_to_input_iter(self):
            windowed_iter = windowed(seq=range(5), n=5, fillvalue=None, step=2)
            slices = list(windowed_iter)
            expected_slices = [(0, 1, 2, 3, 4)]
            assert slices == expected_slices
            
class TestInterleave:
    def test_happy_path(self):
        interleave_iter = interleave(range(1,3), range(3,5), range(-1, 8))
        actual_result = list(interleave_iter)
        expected_result = [1, 3, -1, 2, 4, 0]
        assert actual_result == expected_result 
    
    def test_single_input(self):
        interleave_iter = interleave(range(3))
        actual_result = list(interleave_iter)
        expected_result = [0, 1, 2]
        assert actual_result == expected_result
        
    def test_float(self):
        interleave_iter = interleave([1.1, 2.2, 3.3])
        actual_result = list(interleave_iter)
        expected_result = [1.1, 2.2, 3.3]
        assert actual_result == pytest.approx(expected_result)

class TestRollingAggregate:
    def test_identity(self):
        rolling_iter = rolling_aggregate(range(5), window_size=3, agg_fn=lambda x: x)
        actual_result = list(rolling_iter)
        expected_result = [(0, (0, 1, 2)), (1, (1, 2, 3)), (2, (2, 3, 4))]
        assert actual_result == expected_result
    
    def test_sum(self):
        agg_res = rolling_aggregate(range(5), window_size=3, agg_fn=sum)
        actual_result = list(agg_res)
        expected_result = [(0, 3), (1, 6), (2, 9)]
        assert actual_result == expected_result
    
# pytest F:\py_prepare\more-itertools\tests\test_custom.py -v