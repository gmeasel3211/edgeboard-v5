from ..db import SessionLocal
from ..services.grading import grade_official_picks


def main() -> None:
    with SessionLocal() as db:
        print(grade_official_picks(db))


if __name__ == "__main__":
    main()
