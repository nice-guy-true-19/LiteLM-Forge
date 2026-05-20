The function should not use any additional data structures.

```python
def move_zeros_to_end(nums):
    """
    Moves all zeros to the end of the given list of integers.
    
    :param nums: List of integers
    :return: None
    """
    # Count the number of zeros in the list
    zero_count = nums.count(0)
    
    # Remove all zeros from the list
    for _ in range(zero_count):
        nums.remove(0)
    
    # Append zeros to the end of the list
    nums.extend([0] * zero_count)

# Example usage
nums = [1, 3, 4, 0, 5, 6, 7, 0]
move_zeros_to_end(nums)
print(nums)  # Output: [1, 3, 4, 5, 6, 7, 0, 0]
```

This solution modifies the original list in place by