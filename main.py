import os
import httpx
from typing import Any, Dict
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-mcp")
print('Starting weather-mcp...')

@mcp.tool()
async def get_weather(latitude: float = None, longitude: float = None) -> Dict[str, Any]:
    """
    위도(latitude), 경도(longitude)를 받아 현재 날씨 정보를 반환합니다.
    
    Args:
        latitude: 위도 (기본값: 서울 37.5665)
        longitude: 경도 (기본값: 서울 126.978)
    
    Returns:
        현재 날씨 정보 (온도, 풍속, 날씨코드)
    """
    # 기본값 설정 (서울)
    if latitude is None:
        latitude = float(os.getenv("LATITUDE", "37.5665"))
    if longitude is None:
        longitude = float(os.getenv("LONGITUDE", "126.978"))
    
    try:
        async with httpx.AsyncClient() as client:
            # 무료 오픈 API (Open-Meteo)
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={latitude}&longitude={longitude}&current_weather=true"
            )
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

            current = data.get("current_weather", {})
            return {
                "latitude": latitude,
                "longitude": longitude,
                "temperature": current.get("temperature"),
                "windspeed": current.get("windspeed"),
                "weathercode": current.get("weathercode"),
                "time": current.get("time"),
                "winddirection": current.get("winddirection")
            }
    except Exception as e:
        return {
            "error": f"날씨 정보를 가져오는데 실패했습니다: {str(e)}"
        }

if __name__ == "__main__":
    # stdio 방식으로 MCP 서버 실행
    mcp.run()