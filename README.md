### ⚒️Setting
~~~
$ mkdir weather-mcp
$ cd weather-mcp
$ python3 -m venv venv   
$ source venv/bin/activate
$ pip install 'mcp[cli]'  httpx
~~~


### Run dev mode mcp server
~~~
$ mcp dev main.py
~~~

### Run MCP Server Inspector
~~~
$ npx @modelcontextprotocol/inspector dist/index.js
~~~
