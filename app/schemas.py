from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class RouletteGenerateRequest(BaseModel):
    prompt: str = Field(default="", description="사용자 자연어 요청")
    wanted_place: str = Field(default="", description="원하는 관광지 키워드")
    food_category: str = Field(default="", description="원하는 음식점 키워드")
    duration_days: int | None = Field(default=None, ge=1, le=7, description="여행 기간")

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "prompt": "1박2일로 삼겹살 먹을 수 있는 코스 추천해줘",
                    "duration_days": 2,
                },
                {
                    "prompt": "무등산 근처로 가고 싶고 2박3일 일정이면 좋겠어",
                    "duration_days": 3,
                },
            ]
        }
    )


class RouteItem(BaseModel):
    sequence: int
    type: str
    name: str
    image_url: str | None = None
    mapx: str
    mapy: str
    description: str | None = None


class RouletteGenerateResponse(BaseModel):
    message: str
    duration_days: int
    route_items: list[RouteItem]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "새로운 여행 경로가 자동 생성되었습니다.",
                    "duration_days": 2,
                    "route_items": [
                        {
                            "sequence": 1,
                            "type": "관광지",
                            "name": "무등산국립공원",
                            "image_url": "http://example.com/image.jpg",
                            "mapx": "126.9692640546",
                            "mapy": "35.1519696177",
                            "description": "광주의 상징적인 산입니다.",
                        }
                    ],
                }
            ]
        }
    )