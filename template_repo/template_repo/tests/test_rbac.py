"""Tests for centralized role-based authorization."""

import pytest
from fastapi import HTTPException

from app.rbac import require_roles
from app.security import AuthenticatedUser


def test_allowed_role():
    user = AuthenticatedUser(tenant_id="company_a", roles=["employee"])
    require_roles(user, ["employee", "manager"])


def test_admin_role():
    user = AuthenticatedUser(tenant_id="company_a", roles=["admin"])
    require_roles(user, ["admin"])


def test_forbidden_role():
    user = AuthenticatedUser(tenant_id="company_a", roles=["reader"])

    with pytest.raises(HTTPException) as exc:
        require_roles(user, ["employee", "manager"])

    assert exc.value.status_code == 403


def test_empty_roles_are_forbidden():
    user = AuthenticatedUser(tenant_id="company_a", roles=[])

    with pytest.raises(HTTPException) as exc:
        require_roles(user, ["admin"])

    assert exc.value.status_code == 403
