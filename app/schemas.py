from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class RouletteGenerateRequest(BaseModel):
    stop_count: int | None = Field(
        default=None,
        ge=2,
        le=20,
        description="경로에 포함할 장소 수. 생략하거나 null이면 4~8 중 랜덤으로 정한다.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"stop_count": 5},
                {"stop_count": None},
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
    route_items: list[RouteItem]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "message": "새로운 여행 경로가 자동 생성되었습니다.",
                    "route_items": [
                        {
                            "sequence": 1,
                            "type": "관광지",
                            "name": "무등산국립공원",
                            "image_url": "http://example.com/image.jpg",
                            "mapx": "126.9692640546",
                            "mapy": "35.1519696177",
                            "description": "광주광역시 동구 무등산",
                        }
                    ],
                }
            ]
        }
    )
