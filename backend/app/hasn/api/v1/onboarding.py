"""P0 HASN S2 onboarding endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Request

from backend.app.hasn.schema.hasn_onboarding import (
    OnboardingEnsureRequest,
    OnboardingEnsureResponse,
    PhoneSendCodeRequest,
    PhoneSendCodeResponse,
    PhoneVerifyRequest,
    PhoneVerifyResponse,
)
from backend.app.hasn.service.hasn_onboarding_service import hasn_onboarding_service, hasn_phone_auth_service
from backend.common.security.jwt import DependsJwtAuth, get_token, jwt_decode
from backend.database.db import CurrentSessionTransaction

router = APIRouter()


@router.post('/auth/phone/send_code', summary='Send phone login verification code')
async def send_phone_code(request: PhoneSendCodeRequest) -> PhoneSendCodeResponse:
    return await hasn_phone_auth_service.send_code(request)


@router.post('/auth/phone/verify', summary='Verify phone login code and issue HASN session token')
async def verify_phone_code(
    db: CurrentSessionTransaction,
    request: PhoneVerifyRequest,
) -> PhoneVerifyResponse:
    return await hasn_phone_auth_service.verify(db, request)


@router.post(
    '/onboarding/ensure',
    summary='Ensure Human, Node, OwnerBinding, default Agent, and bootstrap sync state',
    dependencies=[DependsJwtAuth],
)
async def ensure_onboarding(
    db: CurrentSessionTransaction,
    request_body: OnboardingEnsureRequest,
    request: Request,
) -> OnboardingEnsureResponse:
    token_payload = jwt_decode(get_token(request))
    return await hasn_onboarding_service.ensure(db, token_payload.id, request_body)
