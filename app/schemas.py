from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from datetime import datetime

class RouletteGenerateRequest(BaseModel):
    stop_count: int | None = Field(
        default=None,
        ge=3,
        le=8,
        description="경로에 포함할 장소 수. 생략하거나 null이면 3~8 중 랜덤으로 정한다.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"stop_count": 3},
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

class RouletteSaveRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="저장할 경로 제목")
    password: str = Field(..., min_length=1, max_length=100, description="경로 불러오기용 비밀번호")
    route_items: list[RouteItem] = Field(..., min_length=1, description="생성된 경로 항목 목록")


class RouletteSaveResponse(BaseModel):
    status: str
    route_id: int
    message: str


class RouletteRouteListItem(BaseModel):
    route_id: int
    title: str
    created_at: str


class RouletteRouteListResponse(BaseModel):
    items: list[RouletteRouteListItem]
    page: int
    page_size: int
    total_count: int
    total_pages: int
    has_next: bool


class RouletteLoadRequest(BaseModel):
    route_id: int = Field(..., ge=1, description="불러올 저장 경로 ID")
    password: str = Field(..., min_length=1, max_length=100, description="저장 시 설정한 비밀번호")


class RouletteLoadResponse(BaseModel):
    route_id: int
    title: str
    route_items: list[RouteItem]

#post.py의 schema
##post 생성 요청 시 request body
class C_Post(BaseModel):
    title : str
    content : str
    password : str
    route_id : int | None = None
##post 생성 요청에 대한 response
class C_PostResponse(BaseModel):
    post_id : int
    message : str

##post 전체 불러오기용 response
class AllPostDict(BaseModel):
    post_id : int
    title : str
    route_id : int | None = None
    created_at : datetime

class R_AllPostResponse(BaseModel):
    post_info : list[AllPostDict]

##post 상세 조회 response
class R_PostResponse(BaseModel):
    post_id : int
    title : str
    content : str
    route_id : int | None = None 
    created_at : datetime

##post 수정 요청 시 request body
class U_Post(BaseModel):
    title : str
    content : str
    password : str

##post 삭제 요청 시 request body
class D_Post(BaseModel):
    password : str