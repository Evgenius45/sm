from httpx import AsyncClient
from tests.schemas import schema_exceptions, schema_full_user_success


async def test_get_user_me_success(ac: AsyncClient):
    """Test for obtaining information about a user with valid data."""

    response = await ac.get("/api/users/me", headers={"api-key": "test"})
    print(response.json())
    assert response.status_code == 200
    result = response.json()
    schema_full_user_success.validate_python(result)
    assert result["user"]["name"] == "Start"


async def test_get_user_me_invalid(ac: AsyncClient):
    """Test for obtaining information about the
    user if the user is not in the database."""

    response = await ac.get("/api/users/me", headers={"api-key": "5454564646"})

    assert response.status_code == 404
    result = response.json()
    schema_exceptions.validate_python(result)


async def test_get_user_by_id_success(ac: AsyncClient):
    """Test for obtaining information about the user by ID."""
    response = await ac.get("/api/users/1", headers={"api-key": "test"})
    assert response.status_code == 200
    result = response.json()
    assert result["user"]["name"] == "Start"
    schema_full_user_success.validate_python(result)


async def test_get_user_by_id_not_invalid(ac: AsyncClient):
    """Test for obtaining information about a user by ID,
    if the ID does not exist or has been deleted."""
    response = await ac.get("/api/users/100", headers={"api-key": "test"})
    assert response.status_code == 404
    result = response.json()
    schema_exceptions.validate_python(result)


async def test_user_add_followed_success(ac: AsyncClient, prepare_database):
    """Test for adding a subscription to another user."""
    response = await ac.post("/api/users/3/follow", headers={"api-key": "test"})
    assert response.status_code == 201
    data = response.json()
    assert data.get("result")
    response_2 = await ac.get("/api/users/me", headers={"api-key": "test"})
    print(response_2.json())
    assert len(response_2.json()["user"]["following"]) == 2
    await ac.delete("/api/users/3/follow", headers={"api-key": "test"})


async def test_user_add_followed_invalid(ac: AsyncClient, prepare_database):
    """Добавление повторно или не сущ. пользователя"""
    response = await ac.post("/api/users/4/follow", headers={"api-key": "test"})
    assert response.status_code == 409
    result = response.json()
    assert result.get("error_type") == "Conflict"
    schema_exceptions.validate_python(result)


async def test_delete_follow_user_success(ac: AsyncClient, prepare_database):
    """Добавление повторно или не сущ. Пользователя"""

    response = await ac.delete("/api/users/4/follow", headers={"api-key": "test"})
    assert response.status_code == 201
    data = response.json()
    assert data.get("result")
    response_2 = await ac.get("/api/users/me", headers={"api-key": "test"})
    assert len(response_2.json()["user"]["following"]) == 0
    await ac.post("/api/users/4/follow", headers={"api-key": "test"})
