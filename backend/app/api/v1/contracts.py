from fastapi import APIRouter, UploadFile

from app.core.response import success

router = APIRouter()


@router.post("/upload")
async def upload_contract_placeholder(file: UploadFile):
    return success(
        {
            "implemented": False,
            "file_name": file.filename,
        },
        "合同上传接口骨架已创建",
    )


@router.get("")
def list_contracts_placeholder():
    return success({"items": [], "implemented": False})


@router.get("/{contract_id}")
def get_contract_placeholder(contract_id: int):
    return success({"contract_id": contract_id, "implemented": False})


@router.delete("/{contract_id}")
def delete_contract_placeholder(contract_id: int):
    return success({"contract_id": contract_id, "implemented": False}, "合同删除接口骨架已创建")
