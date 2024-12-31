from fastapi import APIRouter
from pydantic import BaseModel

from snapdraft_server.services.base.result_list import ResultList

router = APIRouter()


class Generator(BaseModel):
    name: str


@router.get(
    "/read_all_generators",
    response_model=ResultList[Generator],
    operation_id="read_all_generators",
)
async def read_all_generators() -> ResultList[Generator]:
    return ResultList(items=[Generator(name="Default")])
