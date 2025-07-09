# dataflow
A easy-used and elegant framework dedicated to access big data ecosystem.


## Install
```bash
git clone https://git.midea.com/midea_ai_nlp/dataflow.git
cd dataflow && pip install .
```

## Pipeline example
see https://github.com/tornadoyi/dataflow/blob/master/examples/pipeline.py


## HTTP
Import http module
```python
from dataflow import http
```

Get method
```python
resp = http.get(url="http://www.baidu.com")
print(resp.status, resp.reason, resp.data)
```

Post method
```python
headers = {"Content-Type": "text"}
data = "hello world"
resp = http.get(url="http://httpbin.org/post", headers=headers, data=data)
print(resp.status, resp.reason, resp.data)
```


## Support

For any bugs or feature requests please:

File a new [issue](https://github.com/tornadoyi/dataflow/issues) or submit
a new [pull request](https://github.com/tornadoyi/dataflow/pulls) if you
have some code you'd like to contribute

For other questions and discussions please post a email to 390512308@qq.com


## License

We are releasing [dataflow](https://github.com/tornadoyi/dataflow) under an open source
[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0) License. We welcome you to contact us (390512308@qq.com) with your use cases.

