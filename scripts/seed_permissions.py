import json

from models.entities import UnpermittedQuery, PermittedQuery
from utils.db_utils import get_db_session


def seed():
    with open("permission_data.json") as f:
        data = json.load(f)
    db = get_db_session()
    for pat in data.get("unpermitted", []):
        db.add(UnpermittedQuery(pattern=pat))
    for pat in data.get("permitted", []):
        db.add(PermittedQuery(pattern=pat))
    db.commit()

if __name__ == "__main__":
    seed()
