
def memoize(func):
    memo = {}

    def wrapper(*args):
        key = "{}{}".format(str(func.func_name), str(args[1:]))
        if key in memo:
            return memo[key]
        else:
            if len(memo) > 2000:
                del memo[memo.keys()[0]]
            rv = func(*args)
            memo[key] = rv
        return rv
    return wrapper
