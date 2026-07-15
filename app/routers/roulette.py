import math
import random
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import Place, Route
from ..schemas import (
    RouletteGenerateRequest,
    RouletteGenerateResponse,
    RouletteRouteListItem,
    RouletteSaveRequest,
    RouletteSaveResponse,
    RouteItem,
)


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

# 타입별로 허용할 최대 연속 등장 횟수.
# 음식점은 연속 1회까지만, 나머지는 2회까지 허용한다.
TYPE_CONSECUTIVE_LIMITS = {
    "관광지": 2,
    "문화시설": 2,
    "레포츠": 2,
    "음식점": 1,
}

DEFAULT_CONSECUTIVE_LIMIT = 2

NEAREST_K = 10

# stop_count를 지정하지 않았을 때 무작위로 고르는 범위.
MIN_STOPS = 3
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


def _place_type(place: Place) -> str:
    return CONTENT_TYPE_LABELS.get(place.contenttypeid, "기타")


def _consecutive_limit(place_type: str) -> int:
    return TYPE_CONSECUTIVE_LIMITS.get(place_type, DEFAULT_CONSECUTIVE_LIMIT)


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
    current_type = _place_type(current)
    consecutive_same_type = 1

    while len(route) < stop_count:
        candidates = [place for place in places if place.id not in visited]
        if not candidates:
            break

        origin = points[current.id]
        candidates.sort(key=lambda place: _distance_km(origin, points[place.id]))

        remaining_slots = stop_count - len(route)

        def is_valid_next(place: Place) -> bool:
            next_type = _place_type(place)
            limit = _consecutive_limit(next_type)

            if next_type == current_type and consecutive_same_type >= limit:
                return False

            return True

        nearest_window = candidates[:NEAREST_K]
        valid_candidates = [place for place in nearest_window if is_valid_next(place)]

        if not valid_candidates:
            valid_candidates = [place for place in candidates if is_valid_next(place)]

        if not valid_candidates:
            break

        current = random.choice(valid_candidates)
        route.append(current)
        visited.add(current.id)
        next_type = _place_type(current)
        if next_type == current_type:
            consecutive_same_type += 1
        else:
            current_type = next_type
            consecutive_same_type = 1

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
    "/save",
    response_model=RouletteSaveResponse,
    summary="랜덤 경로 저장",
    description="생성된 경로와 제목, 비밀번호를 저장한다.",
)
def save_route(
    payload: RouletteSaveRequest,
    db: Session = Depends(get_db),
):
    if not payload.route_items:
        raise HTTPException(status_code=400, detail="저장할 경로 항목이 없습니다.")

    ordered_route_items = sorted(payload.route_items, key=lambda item: item.sequence)
    route_json = json.dumps(
        [item.model_dump() for item in ordered_route_items],
        ensure_ascii=False,
    )

    route = Route(
        title=payload.title,
        password=payload.password,
        route_json=route_json,
    )
    db.add(route)
    db.commit()
    db.refresh(route)

    return RouletteSaveResponse(
        status="success",
        route_id=route.id,
        message="경로 데이터가 성공적으로 저장되었습니다.",
    )


@router.get(
    "",
    response_model=list[RouletteRouteListItem],
    summary="저장된 경로 목록 조회",
    description="저장된 룰렛 경로의 요약 목록을 최신순으로 반환한다.",
)
def list_routes(
    db: Session = Depends(get_db),
):
    routes = db.query(Route).order_by(Route.created_at.desc(), Route.id.desc()).all()

    return [
        RouletteRouteListItem(
            route_id=route.id,
            title=route.title,
            created_at=route.created_at.isoformat() if route.created_at else "",
        )
        for route in routes
    ]


@router.post(
    "/generate",
    response_model=RouletteGenerateResponse,
    summary="랜덤 여행 경로 생성",
    description=(
        "랜덤한 지점에서 출발해 인접한 장소를 이어 붙여 경로를 만든다. "
        "매번 가장 가까운 10곳 중 하나를 무작위로 고르되, 타입별 연속 제한을 적용한다. "
        "stop_count를 생략하면 3~8곳 중 랜덤으로 정한다."
    ),
)
def generate_route(
    payload: RouletteGenerateRequest | None = None,
    db: Session = Depends(get_db),
):
    places, points = _load_places(db)

    if len(places) < MIN_STOPS:
        raise HTTPException(status_code=404, detail="경로를 만들 장소 데이터가 부족합니다.")

    requested = payload.stop_count if payload else None
    if requested is None:
        requested = random.randint(MIN_STOPS, MAX_STOPS)

    stop_count = min(requested, len(places), MAX_STOPS)
    route = _walk_nearest(places, points, stop_count)

    return RouletteGenerateResponse(
        message="새로운 여행 경로가 자동 생성되었습니다.",
        route_items=_build_route_items(route),
    )
