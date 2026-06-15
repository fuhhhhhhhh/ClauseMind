from fastapi import APIRouter

from app.core.response import success

router = APIRouter()


@router.post("/{contract_id}/parse")
def start_parse_placeholder(contract_id: int):
    return success({"contract_id": contract_id, "implemented": False}, "解析任务接口骨架已创建")


@router.get("/{contract_id}/parse-status")
def parse_status_placeholder(contract_id: int):
    return success({"contract_id": contract_id, "status": "WAITING", "implemented": False})


@router.get("/{contract_id}/parse-result")
def parse_result_placeholder(contract_id: int):
    return success({"contract_id": contract_id, "markdown": "", "sections": [], "implemented": False})
