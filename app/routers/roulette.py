import random
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Place
from ..schemas import RouletteGenerateRequest, RouletteGenerateResponse, RouteItem


router = APIRouter(prefix="/api/roulette", tags=["roulette"])


SPOT_KEYWORDS = ["무등산", "전망", "공원", "산", "호수", "유원지", "사찰", "미술관", "전시"]
FOOD_KEYWORDS = ["삼겹살", "한식", "떡갈비", "고기", "회", "국밥", "카페", "디저트", "분식"]


def _extract_hint(prompt: str, keywords: list[str]) -> str:
    for keyword in keywords:
        if keyword in prompt:
            return keyword
    return ""


def _parse_duration(prompt: str, explicit_duration: int | None) -> int:
    if explicit_duration is not None:
        return explicit_duration

    text = prompt.replace(" ", "")
    if "당일" in text or "하루" in text:
        return 1

    match = re.search(r"(\d+)박(\d+)일", text)
    if match:
        return int(match.group(2))

    return 1


def _sample_weighted_count(minimum: int, maximum: int, preferred: int) -> int:
    value = int(round(random.gauss(preferred, 0.8)))
    return max(minimum, min(maximum, value))


def _choose_route_counts(duration_days: int) -> tuple[int, int]:
    spot_count = _sample_weighted_count(1, 3, 2)
    restaurant_count = _sample_weighted_count(1, 6, 3)

    if duration_days > 1:
        spot_count = max(spot_count, min(3, duration_days))
        restaurant_count = max(restaurant_count, min(6, duration_days * 2))

    return spot_count, restaurant_count


def _build_route_items(spots: list[Place], restaurants: list[Place]) -> list[RouteItem]:
    route_items: list[RouteItem] = []
    sequence = 1

    for index in range(max(len(spots), len(restaurants))):
        if index < len(spots):
            spot = spots[index]
            route_items.append(
                RouteItem(
                    sequence=sequence,
                    type="관광지",
                    name=spot.title,
                    image_url=spot.firstimage,
                    mapx=spot.mapx,
                    mapy=spot.mapy,
                    description=spot.addr1,
                )
            )
            sequence += 1

        if index < len(restaurants):
            restaurant = restaurants[index]
            route_items.append(
                RouteItem(
                    sequence=sequence,
                    type="음식점",
                    name=restaurant.title,
                    image_url=restaurant.firstimage,
                    mapx=restaurant.mapx,
                    mapy=restaurant.mapy,
                    description=restaurant.addr1,
                )
            )
            sequence += 1

    return route_items


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _pick_places(places: list[Place], count: int) -> list[Place]:
    if not places:
        return []

    if len(places) >= count:
        return random.sample(places, count)

    picks: list[Place] = []
    while len(picks) < count:
        picks.append(random.choice(places))
    return picks


def _filter_places(db: Session, contenttypeid: str, keyword: str) -> list[Place]:
    query = db.query(Place).filter(Place.contenttypeid == contenttypeid)

    if keyword:
        like_pattern = f"%{keyword}%"
        filtered = query.filter(
            (Place.title.like(like_pattern))
            | (Place.addr1.like(like_pattern))
            | (Place.cat3.like(like_pattern))
        ).all()

        if filtered:
            return filtered

    return query.all()


def _get_preferences(payload: RouletteGenerateRequest) -> tuple[str, str, int]:
    prompt = payload.prompt or ""

    # TODO: 내일 OpenAI key가 들어오면 여기서 자연어를 구조화된 조건으로 변환한다.
    wanted_place = payload.wanted_place or _extract_hint(prompt, SPOT_KEYWORDS)
    food_category = payload.food_category or _extract_hint(prompt, FOOD_KEYWORDS)
    duration_days = _parse_duration(prompt, payload.duration_days)

    return wanted_place, food_category, duration_days


@router.post(
    "/generate",
    response_model=RouletteGenerateResponse,
    summary="자연어 기반 랜덤 여행 경로 생성",
    description="사용자의 자연어 프롬프트를 바탕으로 관광지와 음식점 경로를 자동 생성한다. OpenAI 연동 전에는 키워드 힌트와 랜덤 가중치로 동작한다.",
)
def generate_route(payload: RouletteGenerateRequest, db: Session = Depends(get_db)):
    wanted_place, food_category, duration_days = _get_preferences(payload)
    spot_count, restaurant_count = _choose_route_counts(duration_days)

    spots = _filter_places(db, "12", wanted_place)
    restaurants = _filter_places(db, "39", food_category)

    if not spots:
        raise HTTPException(status_code=404, detail="관광지 데이터가 없습니다.")
    if not restaurants:
        raise HTTPException(status_code=404, detail="음식점 데이터가 없습니다.")

    selected_spots = _pick_places(spots, spot_count)
    selected_restaurants = _pick_places(restaurants, restaurant_count)

    route_items = _build_route_items(selected_spots, selected_restaurants)

    return RouletteGenerateResponse(
        message="새로운 여행 경로가 자동 생성되었습니다.",
        duration_days=duration_days,
        route_items=route_items,
    )