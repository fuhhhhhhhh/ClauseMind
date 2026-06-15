from pathlib import Path

from fastapi import APIRouter, Depends, Form, UploadFile

from app.api.deps import get_current_active_user, get_db
from app.core.exceptions import AppError
from app.core.response import success
from app.models.contract import Contract
from app.models.user import User
from app.schemas.contract import (
    ContractListItem,
    ContractListResponse,
    ContractResponse,
)
from app.services.file_storage_service import FileStorageService

router = APIRouter()
storage = FileStorageService()


@router.post("/upload")
async def upload_contract(
    file: UploadFile,
    contract_type: str | None = Form(default=None),
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    stored_name, file_path, file_size = await storage.save_upload(file)

    contract = Contract(
        user_id=current_user.id,
        file_name=file.filename or "unknown",
        stored_file_name=stored_name,
        file_path=file_path,
        file_type=Path(file.filename or "").suffix.lower().lstrip("."),
        file_size=file_size,
        contract_type=contract_type,
        title=file.filename,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)

    return success(
        ContractResponse.model_validate(contract).model_dump(),
        "合同上传成功",
    )


@router.get("")
def list_contracts(
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    items = (
        db.query(Contract)
        .filter(Contract.user_id == current_user.id)
        .order_by(Contract.created_at.desc())
        .all()
    )
    return success(
        ContractListResponse(
            items=[ContractListItem.model_validate(c).model_dump() for c in items],
            total=len(items),
        ).model_dump(),
        "获取合同列表成功",
    )


@router.get("/{contract_id}")
def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise AppError("合同不存在", code=404, status_code=404)
    if contract.user_id != current_user.id:
        raise AppError("无权访问该合同", code=403, status_code=403)

    return success(
        ContractResponse.model_validate(contract).model_dump(),
        "获取合同详情成功",
    )


@router.delete("/{contract_id}")
def delete_contract(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db),
):
    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise AppError("合同不存在", code=404, status_code=404)
    if contract.user_id != current_user.id:
        raise AppError("无权删除该合同", code=403, status_code=403)

    db.delete(contract)
    db.commit()
    return success(None, "合同删除成功")
