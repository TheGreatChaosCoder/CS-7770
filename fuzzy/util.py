import math

#given a sorted array, find the closest value (value will be lower than target)
def get_closest_value(arr, target):
    n = len(arr)
    left = 0
    right = n - 1
    mid = 0

    # edge case - last or above all
    if target >= arr[n - 1]:
        return arr[n - 1]
    # edge case - first or below all
    if target <= arr[0]:
        return arr[0]

    # uses binary search
    while left < right:
        mid = (left + right) // 2
        if target < arr[mid]:
            right = mid
        elif target > arr[mid]:
            left = mid + 1
        else:
            return arr[mid]

    if target < arr[mid]:
        return arr[mid - 1]
    else:
        return arr[mid]
    
#puts a number into a range if it is out of bounds
def into_range(min, max, x):
    return x if x<max and x>min else max if x>=max else min

#finds the max of a list
def max(x:[float]):
    max_num = -math.inf
    for n in x:
        if n>max_num:
            max_num = n

    return max_num

def max_array_idx(x_arr:[float]):
    max_idx = 0
    max_num = -math.inf
    for i in range(len(x_arr)):
        if x_arr[i]>max_num:
            max_num = x_arr[i]
            max_idx = i

    return max_idx

#finds the min of a list
def min(x:[float]):
    min_num = math.inf
    for n in x:
        if n<min_num:
            min_num = n

    return min_num

def min_array_idx(x_arr:[float]):
    min_idx = 0
    min_num = math.inf
    for i in range(len(x_arr)):
        if x_arr[i]<min_num:
            min_num = x_arr[i]
            min_idx = i

    return min_idx