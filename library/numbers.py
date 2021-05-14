def human_format(num):
    num = float('{:.3g}'.format(num))
    suffixes = ['', 'K', ' Million', ' Billion', ' Trillion']
    len_suffixes = len(suffixes)
    magnitude = 0
    while abs(num) >= 1000:
        if magnitude+1 >= len_suffixes:
            break
        magnitude += 1
        num /= 1000.0

    str_num = str(num).rstrip("0").rstrip(".")
    return f"{str_num}{suffixes[magnitude]}"
