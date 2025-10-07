"""
Handovers API Routes

Handles employee knowledge handovers with strict ACL.
Users can create, view, acknowledge, and complete handovers.
"""

from fastapi import APIRouter, Header, HTTPException, Path
from typing import Optional
from app.models.schemas import (
    CreateHandoverRequest,
    HandoverResponse,
    HandoversListResponse,
    UpdateHandoverStatusRequest
)
from app.services import auth
from app.services.db import (
    create_handover,
    get_user_handovers,
    get_handover_by_id,
    update_handover_status,
    delete_handover
)

router = APIRouter()


@router.post("/handovers", response_model=HandoverResponse, status_code=201)
async def create_handover_endpoint(
    request: CreateHandoverRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Create a new handover.

    The authenticated user becomes the sender (from_employee_id).
    Recipient must be a valid employee ID.

    Returns:
        HandoverResponse with the newly created handover details
    """
    # Authentication
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        user_id = auth.verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Validate: user can't send handover to themselves
    if user_id == request.to_employee_id:
        raise HTTPException(status_code=400, detail="Cannot create handover to yourself")

    # Create handover in database
    try:
        handover_id = await create_handover(
            from_employee_id=user_id,
            to_employee_id=request.to_employee_id,
            title=request.title,
            project_id=request.project_id,
            context=request.context,
            current_status=request.current_status,
            next_steps=request.next_steps,
            resources=request.resources,
            contacts=request.contacts,
            additional_notes=request.additional_notes,
            cc_employee_ids=request.cc_employee_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create handover: {str(e)}")

    # Fetch the created handover to return full details
    handover = await get_handover_by_id(handover_id, user_id)
    if not handover:
        raise HTTPException(status_code=500, detail="Handover created but could not be retrieved")

    return HandoverResponse(**handover)


@router.get("/handovers", response_model=HandoversListResponse)
async def list_handovers(
    authorization: Optional[str] = Header(None)
):
    """
    List all handovers for the authenticated user.

    Returns:
        {
            "received": [...],  // Handovers user received or was CC'd on
            "sent": [...]       // Handovers user sent
        }
    """
    # Authentication
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        user_id = auth.verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Get user's handovers
    try:
        handovers_data = await get_user_handovers(user_id)

        # Convert to response models
        received = [HandoverResponse(**h) for h in handovers_data["received"]]
        sent = [HandoverResponse(**h) for h in handovers_data["sent"]]

        return HandoversListResponse(received=received, sent=sent)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch handovers: {str(e)}")


@router.get("/handovers/{handover_id}", response_model=HandoverResponse)
async def get_handover(
    handover_id: int = Path(..., description="Handover ID"),
    authorization: Optional[str] = Header(None)
):
    """
    Get a single handover by ID.

    ACL: User must be sender, recipient, or CC'd to view.

    Returns:
        HandoverResponse with full handover details
    """
    # Authentication
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        user_id = auth.verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Fetch handover with ACL check
    handover = await get_handover_by_id(handover_id, user_id)

    if not handover:
        raise HTTPException(
            status_code=404,
            detail="Handover not found or you don't have access to it"
        )

    return HandoverResponse(**handover)


@router.patch("/handovers/{handover_id}", response_model=HandoverResponse)
async def update_handover_status_endpoint(
    handover_id: int = Path(..., description="Handover ID"),
    request: UpdateHandoverStatusRequest = ...,
    authorization: Optional[str] = Header(None)
):
    """
    Update handover status (acknowledge or complete).

    Only the recipient can acknowledge or complete a handover.

    Status transitions:
    - pending → acknowledged (recipient acknowledges receipt)
    - acknowledged → completed (recipient marks work as done)
    - pending → completed (skip acknowledgement, directly complete)

    Returns:
        Updated HandoverResponse
    """
    # Authentication
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        user_id = auth.verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Update status
    success = await update_handover_status(
        handover_id=handover_id,
        user_id=user_id,
        status=request.status.value
    )

    if not success:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update this handover, or invalid status transition"
        )

    # Fetch updated handover
    handover = await get_handover_by_id(handover_id, user_id)
    if not handover:
        raise HTTPException(status_code=500, detail="Handover updated but could not be retrieved")

    return HandoverResponse(**handover)


@router.delete("/handovers/{handover_id}", status_code=204)
async def delete_handover_endpoint(
    handover_id: int = Path(..., description="Handover ID"),
    authorization: Optional[str] = Header(None)
):
    """
    Delete a handover.

    Only the sender can delete a handover.
    This is a hard delete (removes from database).

    Returns:
        204 No Content on success
    """
    # Authentication
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        user_id = auth.verify_jwt(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Delete handover
    success = await delete_handover(handover_id, user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Handover not found or you are not authorized to delete it (only sender can delete)"
        )

    return None  # 204 No Content