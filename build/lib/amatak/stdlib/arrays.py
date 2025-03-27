def map(arr, func):
    return [func(x) for x in arr]

def filter(arr, predicate):
    return [x for x in arr if predicate(x)]

def reduce(arr, func, initial):
    acc = initial
    for x in arr:
        acc = func(acc, x)
    return acc