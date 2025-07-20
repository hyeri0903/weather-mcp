### ⚒️Setting
~~~
$ mkdir weather-mcp
$ cd weather-mcp
$ python3 -m venv venv   
$ source venv/bin/activate
$ pip install 'mcp[cli]'  httpx
~~~

### Setting Cursor, Claude Desktop settings.json
~~~
{
  "mcpServers": {
    "weather-mcp": {
      "command": "${Pyhon-Path}",
      "args": ["${main.py file path"],
      "env": {
        "LOCATION": "Seoul"
      }
    }
  }
}

~~~


### Run dev mode mcp server
~~~
$ mcp dev main.py
~~~

### Run MCP Server Inspector
~~~
$ npx @modelcontextprotocol/inspector dist/index.js
~~~

### Call Function
~~~
# To get weather by location
await get_weather(location="New York")

# To get weather using latitude and longitude
await get_weather(latitude=35.6762, longitude=139.6503)

# Using Env
await get_weather()

# Seach Location tool
await search_location("paris")
~~~
