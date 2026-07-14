import json
from pathlib import Path

from app.database import SessionLocal, engine
from app.models import Base, Place


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILES = [
    DATA_DIR / "gwangju_spot.json",
    DATA_DIR / "gwangju_restaurant.json",
]


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def seed_places() -> int:
    session = SessionLocal()
    inserted_count = 0

    try:
        existing_keys = {
            (place.contenttypeid, place.title, place.mapx, place.mapy)
            for place in session.query(Place).all()
        }

        for file_path in DATA_FILES:
            if not file_path.exists():
                continue

            with file_path.open("r", encoding="utf-8") as file:
                payload = json.load(file)

            for item in payload.get("items", []):
                key = (
                    item.get("contenttypeid", ""),
                    item.get("title", ""),
                    item.get("mapx", ""),
                    item.get("mapy", ""),
                )

                if key in existing_keys:
                    continue

                place = Place(
                    contenttypeid=str(item.get("contenttypeid", "")),
                    title=item.get("title", ""),
                    addr1=item.get("addr1", ""),
                    firstimage=item.get("firstimage") or None,
                    mapx=str(item.get("mapx", "")),
                    mapy=str(item.get("mapy", "")),
                    cat3=item.get("cat3") or None,
                )
                session.add(place)
                existing_keys.add(key)
                inserted_count += 1

        session.commit()
        return inserted_count
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_db()
    count = seed_places()
    print(f"Inserted {count} place records.")