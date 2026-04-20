from urllib.parse import urlparse

import os
import requests
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from database import get_session
from models import Link

app = FastAPI()

STEAM_API_KEY = os.environ.get("STEAM_API_KEY", "")


class BindRequest(BaseModel):
    telegramId: int
    steamLink: str


class BindResponse(BaseModel):
    status: str
    message: str
    steamId: str | None


class LinkResponse(BaseModel):
    status: str
    steamId: str | None


class BusinessError(Exception):
    def __init__(self, message: str):
        self.message = message


@app.get("/health")
def health():
    return {"status": "ok"}


def build_bind_response(status: str, message: str, steam_id: str | None) -> BindResponse:
    return BindResponse(status=status, message=message, steamId=steam_id)


def resolve_vanity_url(vanity_url: str) -> str | None:
    if not STEAM_API_KEY:
        return None
    url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
    params = {"key": STEAM_API_KEY, "vanityurl": vanity_url}
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        result = data.get("response", {})
        if result.get("success") == 1:
            return result.get("steamid")
    except Exception:
        pass
    return None


def parse_steam_id(url: str) -> str:
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        # Возможно, передан vanity URL или SteamID64 напрямую
        # Попробуем как vanity URL
        if STEAM_API_KEY:
            steam_id = resolve_vanity_url(url)
            if steam_id:
                return steam_id
        raise BusinessError("Неверная ссылка Steam")

    if parsed.netloc not in {"steamcommunity.com", "www.steamcommunity.com"}:
        # Попробуем распознать как vanity в query-параметрах
        if STEAM_API_KEY:
            steam_id = resolve_vanity_url(parsed.path.strip("/"))
            if steam_id:
                return steam_id
        raise BusinessError("Неверная ссылка Steam")

    path = parsed.path.strip("/")
    parts = path.split("/")

    if len(parts) == 2 and parts[0] == "id":
        # https://steamcommunity.com/id/coolnickname
        if STEAM_API_KEY:
            steam_id = resolve_vanity_url(parts[1])
            if steam_id:
                return steam_id
            raise BusinessError("Не удалось найти пользователя по нику")
        raise BusinessError("Сервис не настроен для обработки vanity URL")

    if len(parts) != 2 or parts[0] != "profiles":
        raise BusinessError("Неверная ссылка Steam")

    steam_id = parts[1]
    if not (steam_id.isdigit() and len(steam_id) == 17 and steam_id.startswith("765611")):
        raise BusinessError("Неверная ссылка Steam")

    return steam_id


@app.post("/bind")
def bind(data: BindRequest, session: Session = Depends(get_session)):
    try:
        steam_id = parse_steam_id(data.steamLink)

        existing_telegram_link = session.exec(
            select(Link).where(Link.telegram_id == data.telegramId)
        ).first()
        if existing_telegram_link:
            return JSONResponse(
                status_code=409,
                content=build_bind_response(
                    "error", "Этот Telegram уже привязан", None
                ).model_dump(),
            )

        if session.exec(select(Link).where(Link.steam_id64 == steam_id)).first():
            return JSONResponse(
                status_code=409,
                content=build_bind_response(
                    "error", "Этот Steam уже привязан", None
                ).model_dump(),
            )

        link = Link(telegram_id=data.telegramId, steam_id64=steam_id)
        session.add(link)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            return JSONResponse(
                status_code=409,
                content=build_bind_response(
                    "error", "Конфликт привязки", None
                ).model_dump(),
            )

        return JSONResponse(
            status_code=200,
            content=build_bind_response(
                "success", "Аккаунт привязан", steam_id
            ).model_dump(),
        )
    except BusinessError as exc:
        return JSONResponse(
            status_code=400,
            content=build_bind_response("error", exc.message, None).model_dump(),
        )


@app.get("/link/{telegramId}")
def get_link(telegramId: int, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.telegram_id == telegramId)).first()
    return LinkResponse(status="success", steamId=link.steam_id64 if link else None).model_dump()


@app.delete("/link/{telegramId}")
def delete_link(telegramId: int, session: Session = Depends(get_session)):
    link = session.exec(select(Link).where(Link.telegram_id == telegramId)).first()

    if not link:
        return JSONResponse(
            status_code=404,
            content={"status": "error", "message": "Привязка не найдена"},
        )

    session.delete(link)
    session.commit()
    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "Привязка удалена"},
    )
