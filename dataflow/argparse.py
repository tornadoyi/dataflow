

def python_dict_type(string): return eval(string)

def python_code_type(string):
    # format code
    code = ''
    for ln in string.split(' '): code += ln + '\n'

    # get env keys
    global_dict = {}
    exec('', global_dict)

    # exec code
    code_dict = {}
    exec(code, code_dict)

    # pick new parameters from global
    args = {}
    for k, v in code_dict.items():
        if k in global_dict: continue
        args[k] = v

    return args
