
from .env import _getenv
from dataflow import shell


def streaming(
    input,
    output,
    mapper = None,
    reducer = None,
    combiner = None,
    files = [],
    input_format = None,
    output_format = None,
    partitioner = None,
    num_reduce_tasks = None,
    input_reader = None,
    cmd_env = None,
    map_debug = None,
    reduce_debug = None,
    io = None,
    lazy_output = None,
    background = None,
    verbose = None,
    info = None,
    help = None,
    properties = [],
    job_confs = [],

):
    hadoop, streaming = _getenv('hadoop'), _getenv('streaming')

    args = []

    # add properties and job confs
    for a in properties: args.append('-D {}'.format(a))
    for a in job_confs: args.append('-D {}'.format(a))

    # add streaming args
    args.append('-input {}'.format(input))
    args.append('-output {}'.format(output))
    if mapper is not None: args.append('-mapper "{}"'.format(mapper))
    if reducer is not None: args.append('-reducer "{}"'.format(reducer))
    if combiner is not None: args.append('-combiner {}'.format(combiner))
    if input_format is not None: args.append('-inputformat {}'.format(input_format))
    if output_format is not None: args.append('-outputformat {}'.format(output_format))
    if partitioner is not None: args.append('-partitioner {}'.format(partitioner))
    if num_reduce_tasks is not None: args.append('-numReduceTasks {}'.format(num_reduce_tasks))
    if input_reader is not None: args.append('-inputreader {}'.format(input_reader))
    if cmd_env is not None: args.append('-cmdenv {}'.format(cmd_env))
    if map_debug is not None: args.append('-mapdebug {}'.format(map_debug))
    if reduce_debug is not None: args.append('-reducedebug {}'.format(reduce_debug))
    if io is not None: args.append('-io {}'.format(io))
    if lazy_output is not None: args.append('-lazyOutput {}'.format(lazy_output))
    if background is not None: args.append('-background {}'.format(background))
    #if verbose is not None: args.append('-verbose {}'.format(verbose))
    if info is not None: args.append('-info {}'.format(info))
    if help is not None: args.append('-help {}'.format(help))

    # add files
    for a in files: args.append('-file {}'.format(a))

    # generate command
    str_args = ''
    for a in args: str_args += a + ' '
    stream_cmd = '{} jar {} {}'.format(hadoop, streaming, str_args)
    p = shell.run(stream_cmd, verbose=int(verbose))
    if p.returncode != 0: raise Exception(p.read_error())






