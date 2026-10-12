from fastapi import APIRouter, HTTPException, Query, Request

from typing import Optional

from app.schemas import BasketRequest, RecommendRequest

router = APIRouter(prefix="/api", tags=["recommendations"])


def _rec(request: Request):
    return request.app.state.recommender


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/stats")
def stats(request: Request):
    return _rec(request).stats()


@router.get("/products")
def list_products(request: Request, category: Optional[str] = None,
                  page: int = Query(1, ge=1), size: int = Query(24, ge=1, le=60)):
    return _rec(request).list_products(category, page, size)


@router.post("/recommend/basket")
def recommend_basket(body: BasketRequest, request: Request):
    try:
        return _rec(request).recommend_basket(body.product_ids, body.top_n)
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.get("/products/random")
def random_products(request: Request, n: int = Query(8, ge=1, le=24)):
    return _rec(request).random(n)


@router.get("/products/{product_id}")
def get_product(product_id: str, request: Request):
    try:
        return _rec(request).get(product_id)
    except KeyError:
        raise HTTPException(404, f"Product '{product_id}' not found")


@router.post("/recommend")
def recommend(body: RecommendRequest, request: Request):
    try:
        return _rec(request).recommend(body.product_id, body.text, body.top_n, body.category)
    except KeyError:
        raise HTTPException(404, f"Product '{body.product_id}' not found")
    except ValueError as e:
        raise HTTPException(422, str(e))


@router.post("/explain")
def explain(body: RecommendRequest, request: Request):
    try:
        return _rec(request).explain(body.product_id, body.text, min(body.top_n, 10), body.category)
    except KeyError:
        raise HTTPException(404, f"Product '{body.product_id}' not found")
    except ValueError as e:
        raise HTTPException(422, str(e))
