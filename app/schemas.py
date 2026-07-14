from pydantic import BaseModel, Field


class RouletteGenerateRequest(BaseModel):
    prompt: str = Field(default="", description="사용자 자연어 요청")
    wanted_place: str = Field(default="", description="원하는 관광지 키워드")
    food_category: str = Field(default="", description="원하는 음식점 키워드")
    duration_days: int | None = Field(default=None, ge=1, le=7, description="여행 기간")


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