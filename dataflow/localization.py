
__LOC_START = '<LOC>'
__LOC_END = '</LOC>'

def id(s): return __LOC_START + s + __LOC_END

L = id


def translate(s, d, miss_error=True):
    d = d or {}
    start = True

    ret = ''
    i = 0

    while(i < len(s)):
        j = s.find(__LOC_START if start else __LOC_END, i)
        if j < 0:
            if not start: raise Exception('Invalid localization format, {}'.format(s))
            ret += s[i:len(s)]
            break

        if start:
            ret += s[i:j]
            i = j + len(__LOC_START)
        else:
            w = s[i:j]
            if w not in d and miss_error: raise Exception('Can not find word {} in dictionary'.format(w))
            ret += d.get(w, w)
            i = j + len(__LOC_END)

        start = not start

    return ret



if __name__ == '__main__':
    # case 1
    text = 'hello {} world {} what is{}'.format(id('id1'), id('id2'), id('id3'))
    print(translate(text, {'id1': 'ID1', 'id2': 'ID2', 'id3': 'ID3'}))


    # case 2
    text = '123'
    print(translate(text, {}))