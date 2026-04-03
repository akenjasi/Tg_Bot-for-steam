# сценарии успеха
def test_bind_success(client):
    response = client.post(
        "/bind",
        json={
            "telegramId": 1001,
            "steamLink": "https://steamcommunity.com/profiles/76561198000000001",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Аккаунт привязан",
        "steamId": "76561198000000001",
    }


# сценарии дубликатов
def test_bind_duplicate_telegram_returns_409(client):
    payload_first = {
        "telegramId": 1002,
        "steamLink": "https://steamcommunity.com/profiles/76561198000000002",
    }
    payload_second = {
        "telegramId": 1002,
        "steamLink": "https://steamcommunity.com/profiles/76561198000000003",
    }

    first_response = client.post("/bind", json=payload_first)
    second_response = client.post("/bind", json=payload_second)

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json() == {
        "status": "error",
        "message": "Этот Telegram уже привязан",
        "steamId": None,
    }


def test_bind_duplicate_steam_returns_409(client):
    payload_first = {
        "telegramId": 1003,
        "steamLink": "https://steamcommunity.com/profiles/76561198000000004",
    }
    payload_second = {
        "telegramId": 1004,
        "steamLink": "https://steamcommunity.com/profiles/76561198000000004",
    }

    first_response = client.post("/bind", json=payload_first)
    second_response = client.post("/bind", json=payload_second)

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert second_response.json() == {
        "status": "error",
        "message": "Этот Steam уже привязан",
        "steamId": None,
    }


# сценарии ошибок
def test_bind_invalid_steam_link_returns_400(client):
    response = client.post(
        "/bind",
        json={
            "telegramId": 1005,
            "steamLink": "https://example.com/profiles/76561198000000005",
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "status": "error",
        "message": "Неверная ссылка Steam",
        "steamId": None,
    }


def test_get_link_existing_returns_steam_id(client):
    bind_response = client.post(
        "/bind",
        json={
            "telegramId": 1006,
            "steamLink": "https://steamcommunity.com/profiles/76561198000000006",
        },
    )
    response = client.get("/link/1006")

    assert bind_response.status_code == 200
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "steamId": "76561198000000006",
    }


def test_get_link_missing_returns_success_with_null(client):
    response = client.get("/link/999999")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "steamId": None,
    }


def test_delete_link_existing_returns_success(client):
    bind_response = client.post(
        "/bind",
        json={
            "telegramId": 1007,
            "steamLink": "https://steamcommunity.com/profiles/76561198000000007",
        },
    )
    delete_response = client.delete("/link/1007")
    get_response = client.get("/link/1007")

    assert bind_response.status_code == 200
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "status": "success",
        "message": "Привязка удалена",
    }
    assert get_response.status_code == 200
    assert get_response.json() == {
        "status": "success",
        "steamId": None,
    }


def test_delete_link_missing_returns_404(client):
    response = client.delete("/link/888888")

    assert response.status_code == 404
    assert response.json() == {
        "status": "error",
        "message": "Привязка не найдена",
    }
