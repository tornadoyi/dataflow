import json
from dataflow import application as app
from dataflow import http
from dataflow.multiprocessing.task import Task, TaskManager


class InputUrl(Task):
    def __call__(self, *args, **kwargs):
        return "http://httpbin.org/post"
    
class InputHeaders(Task):
    def __call__(self, *args, **kwargs):
        return {"Content-Type": "text"}
    
class InputData(Task):
    def __call__(self, *args, **kwargs):
        return "hello wolrd"


class FetchUrl(Task):

    def __init__(self, output_path, children=None):
        super().__init__(children)
        self._output_path = output_path

    def __call__(self, *args, **kwargs):
        url, headers, data = args
        resp = http.post(url, headers=headers, data=data)
        with open(self._output_path, 'w') as f:
            json.dump(resp.data.decode(), f)


class Cmds(object):

    class example(object):
        @staticmethod
        def add_parser(sparser):
            parser = sparser.add_parser('example', help='exmpale command')
            parser.add_argument('-o', "--output", type=str, default="output.json", help='output json file path')
            parser.add_argument('-v', action="store_true", help='verbose mode')

        @staticmethod
        def execute(args):
            manager = TaskManager([
                FetchUrl(
                    output_path=args.output,
                    children=[InputUrl(), InputHeaders(), InputData()])
            ])
            manager()
            manager.wait()


def main():
    app.initialize(
        name="my_pipeline",
        description="a example for pipeline",
        modules=Cmds
    )
    app.run()


if __name__ == '__main__':
    main()