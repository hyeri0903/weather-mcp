import os
import httpx
from typing import Any
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-mcp")

async def geocode_location(location: str) -> dict[str, Any] | None:
    """
    위치명을 위도/경도로 변환합니다.
    
    Args:
        location: 위치명 (예: "Seoul", "New York", "Tokyo")
    
    Returns:
        {"latitude": float, "longitude": float} 또는 None
    """
    try:
        async with httpx.AsyncClient() as client:
            # Open-Meteo의 Geocoding API 사용 (무료)
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            results = data.get("results", [])
            if results:
                result = results[0]
                return {
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "name": result.get("name"),
                    "country": result.get("country")
                }
    except Exception as e:
        print(f"Geocoding 실패: {str(e)}")
    
    return None

@mcp.tool()
async def get_weather(latitude: float = None, longitude: float = None, location: str = None) -> dict[str, Any]:
    """
    위도/경도 또는 위치명을 받아 현재 날씨 정보를 반환합니다.
    
    Args:
        latitude: 위도 (기본값: 환경변수 LATITUDE 또는 서울 37.5665)
        longitude: 경도 (기본값: 환경변수 LONGITUDE 또는 서울 126.978)
        location: 위치명 (기본값: 환경변수 LOCATION 또는 "Seoul")
    
    Returns:
        현재 날씨 정보 (온도, 풍속, 날씨코드)
    """
    # 우선순위: 직접 입력된 좌표 > 직접 입력된 위치명 > 환경변수
    if latitude is not None and longitude is not None:
        # 좌표가 직접 제공된 경우
        final_lat, final_lon = latitude, longitude
        location_name = "Custom Location"
    elif location is not None:
        # 위치명이 직접 제공된 경우
        geo_result = await geocode_location(location)
        if not geo_result:
            return {"error": f"위치 '{location}'를 찾을 수 없습니다."}
        final_lat = geo_result["latitude"]
        final_lon = geo_result["longitude"]
        location_name = f"{geo_result['name']}, {geo_result['country']}"
    else:
        # 환경변수에서 가져오기
        env_location = os.getenv("LOCATION")
        if env_location:
            # 환경변수에 위치명이 설정된 경우
            geo_result = await geocode_location(env_location)
            if not geo_result:
                return {"error": f"환경변수 LOCATION '{env_location}'을 찾을 수 없습니다."}
            final_lat = geo_result["latitude"]
            final_lon = geo_result["longitude"]
            location_name = f"{geo_result['name']}, {geo_result['country']}"
        else:
            # 환경변수에서 좌표 가져오기 (기존 방식)
            final_lat = float(os.getenv("LATITUDE", "37.5665"))
            final_lon = float(os.getenv("LONGITUDE", "126.978"))
            location_name = "Seoul, South Korea"  # 기본값
    
    try:
        async with httpx.AsyncClient() as client:
            # 무료 오픈 API (Open-Meteo)
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={final_lat}&longitude={final_lon}&current_weather=true"
            )
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()

            current = data.get("current_weather", {})
            return {
                "location": location_name,
                "latitude": final_lat,
                "longitude": final_lon,
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

@mcp.tool()
async def search_location(query: str) -> dict[str, Any]:
    """
    위치명으로 검색하여 가능한 위치들을 반환합니다.
    
    Args:
        query: 검색할 위치명
    
    Returns:
        검색된 위치들의 목록
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5"
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            
            results = data.get("results", [])
            locations = []
            
            for result in results:
                locations.append({
                    "name": result.get("name"),
                    "country": result.get("country"),
                    "admin1": result.get("admin1"),  # 주/도
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude")
                })
            
            return {
                "query": query,
                "locations": locations
            }
    except Exception as e:
        return {
            "error": f"위치 검색에 실패했습니다: {str(e)}"
        }

if __name__ == "__main__":
    print('Starting weather-mcp...')
     # stdio 방식으로 MCP 서버 실행
    mcp.run()