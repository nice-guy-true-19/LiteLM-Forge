def move_zeros_to_end(nums):
    return sorted(nums, key=lambda x: int(x) == 0)

# Test cases
print(move_zeros_to_end([0, 1, 0, 3, 12]))  # Output: [1, 3, 12, 0, 0]
print(move_zeros_to_end([0, 0, 0, 0]))    # Output: [0, 0, 0, 0]
print(move_zeros_to_end([1, 2, 3, 4]))     # Output: [1, 2, 3, 4]