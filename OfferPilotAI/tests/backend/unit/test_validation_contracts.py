"""Unit tests for validators and configuration contracts."""

import pytest
from pydantic import ValidationError

from app.core.config import Environment, Settings
from app.schemas.coding import CodeRunRequest
from app.schemas.interview_engine import StartInterviewRequest
from app.schemas.resume import ResumeTextAnalyzeRequest

pytestmark = pytest.mark.unit


def test_start_interview_request_rejects_duplicate_categories():
    with pytest.raises(ValidationError):
        StartInterviewRequest(
            role="Backend Engineer",
            difficulty="medium",
            duration_minutes=30,
            categories=["python", "python"],
        )


def test_code_run_request_rejects_blank_source_code():
    with pytest.raises(ValidationError):
        CodeRunRequest(language="python", source_code="   ")


def test_resume_text_request_requires_enough_signal():
    with pytest.raises(ValidationError):
        ResumeTextAnalyzeRequest(resume_text="too short for analysis", filename="resume.txt")


def test_production_settings_require_secure_jwt_secret():
    with pytest.raises(ValueError):
        Settings(environment=Environment.PRODUCTION)
