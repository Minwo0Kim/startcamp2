import math
import random

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Place
from ..schemas import RouletteGenerateRequest, RouletteGenerateResponse, RouteItem


router = APIRouter(prefix="/api/roulette", tags=["roulette"])


# 한국관광공사 contenttypeid 분류. 새 종류를 적재하면 여기에만 추가하면 경로에 함께 섞인다.
CONTENT_TYPE_LABELS = {
    "12": "관광지",
    "14": "문화시설",
    "15": "축제공연행사",
    "25": "여행코스",
    "28": "레포츠",
    "32": "숙박",
    "38": "쇼핑",
    "39": "음식점",
}

NEAREST_K = 10

# stop_count를 지정하지 않았을 때 무작위로 고르는 범위.
MIN_STOPS = 4
MAX_STOPS = 8

# 관광공사 원본에 좌표가 (117.99, 19.69)로 채워진 결측치가 섞여 있어 한반도 남부 밖은 제외한다.
LAT_MIN, LAT_MAX = 33.0, 38.5
LON_MIN, LON_MAX = 125.0, 130.0


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _to_point(place: Place) -> tuple[float, float] | None:
    try:
        lon, lat = float(place.mapx), float(place.mapy)
    except (TypeError, ValueError):
        return None

    if not (LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX):
        return None

    return lon, lat


def _distance_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lon1, lat1 = a
    lon2, lat2 = b
    dy = (lat2 - lat1) * 111.0
    dx = (lon2 - lon1) * 111.0 * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot(dx, dy)


def _load_places(db: Session) -> tuple[list[Place], dict[int, tuple[float, float]]]:
    places: list[Place] = []
    points: dict[int, tuple[float, float]] = {}

    for place in db.query(Place).all():
        point = _to_point(place)
        if point is None:
            continue
        places.append(place)
        points[place.id] = point

    return places, points


def _walk_nearest(
    places: list[Place],
    points: dict[int, tuple[float, float]],
    stop_count: int,
) -> list[Place]:
    """랜덤한 시작점에서 출발해 매번 가장 가까운 NEAREST_K곳 중 하나로 이동한다.

    반경을 고정하지 않고 k개를 고르므로 지점이 조밀한 도심과 희박한 군 지역에서
    모두 동작한다. 반경 방식은 희박한 지역에서 후보가 0개가 되어 경로가 끊긴다.
    """
    current = random.choice(places)
    route = [current]
    visited = {current.id}

    while len(route) < stop_count:
        candidates = [place for place in places if place.id not in visited]
        if not candidates:
            break

        origin = points[current.id]
        candidates.sort(key=lambda place: _distance_km(origin, points[place.id]))

        current = random.choice(candidates[:NEAREST_K])
        route.append(current)
        visited.add(current.id)

    return route


def _build_route_items(route: list[Place]) -> list[RouteItem]:
    return [
        RouteItem(
            sequence=sequence,
            type=CONTENT_TYPE_LABELS.get(place.contenttypeid, "기타"),
            name=place.title,
            image_url=place.firstimage,
            mapx=place.mapx,
            mapy=place.mapy,
            description=place.addr1,
        )
        for sequence, place in enumerate(route, start=1)
    ]


@router.post(
    "/generate",
    response_model=RouletteGenerateResponse,
    summary="랜덤 여행 경로 생성",
    description=(
        "랜덤한 지점에서 출발해 인접한 장소를 이어 붙여 경로를 만든다. "
        "매번 가장 가까운 10곳 중 하나를 무작위로 골라 이동한다. "
        "stop_count를 생략하면 4~8곳 중 랜덤으로 정한다."
    ),
)
def generate_route(
    payload: RouletteGenerateRequest | None = None,
    db: Session = Depends(get_db),
):
    places, points = _load_places(db)

    if len(places) < 2:
        raise HTTPException(status_code=404, detail="경로를 만들 장소 데이터가 부족합니다.")

    requested = payload.stop_count if payload else None
    if requested is None:
        requested = random.randint(MIN_STOPS, MAX_STOPS)

    stop_count = min(requested, len(places))
    route = _walk_nearest(places, points, stop_count)

    return RouletteGenerateResponse(
        message="새로운 여행 경로가 자동 생성되었습니다.",
        route_items=_build_route_items(route),
    )
