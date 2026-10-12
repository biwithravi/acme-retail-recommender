from fastapi.testclient import TestClient

from app.main import app


def test_endpoints():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["status"] == "ok"
        r = c.post("/api/recommend", json={"product_id": "ACME_000001", "top_n": 5}).json()
        scores = [x["similarity_score"] for x in r["results"]]
        assert len(scores) == 5 and scores == sorted(scores, reverse=True)
        assert all(x["product_id"] != "ACME_000001" for x in r["results"])
        # unseen / misspelt word must not break the system
        assert c.post("/api/recommend", json={"text": "runnning shooes xyzzyq"}).status_code == 200
        assert c.post("/api/recommend", json={"text": "123 !!!"}).status_code == 422
        assert c.post("/api/recommend", json={"product_id": "NOPE"}).status_code == 404
        assert c.post("/api/explain", json={"text": "cotton shirt"}).status_code == 200
