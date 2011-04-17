# ANSI bling


def to_col(n):
    return "\033[%sG\033[K" % n


def colour(n=""):
    return "\033[%sm" % n


def para_to_col(n, string):
    return to_col(n) + string.replace("\n", "\n" + to_col(n))


def pad(n, string, fill):
    count = n - min(len(string), n)
    return string + (count * fill)
