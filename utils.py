
def read_text(file_name: str):
    with open(file_name) as f:
        ret = f.read().splitlines()
    return ret


def read_csv(file_name: str, sep=';', with_header: bool = False):
    text = read_text(file_name)
    ret = [line.split(sep) for line in text[int(not with_header):]]
    ret = [[line[0], float(line[1]), float(line[2])] for line in ret]
    return ret
