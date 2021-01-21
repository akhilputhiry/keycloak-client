# -*- coding: utf-8 -*-
import json
from typing import Any
from urllib.parse import urlparse

from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.requests import Request
from starlette.responses import Response, RedirectResponse, PlainTextResponse
from starlette.endpoints import HTTPEndpoint

from .. import Client


class EndpointHandler(HTTPEndpoint):
    def __init__(self, *args: Any, **kwargs: Any):
        self.kc = kwargs.pop("kc")
        self.redirect_uri = kwargs.pop("redirect_uri", "/")
        super().__init__(*args, **kwargs)


class Login(EndpointHandler):
    async def get(self, request: Request) -> Response:
        url, state = self.kc.login()
        request.session["state"] = state
        return RedirectResponse(url)


class Logout(EndpointHandler):
    async def get(self, request: Request) -> Response:
        # _tokens = request.session["tokens"]
        # tokens = json.loads(_tokens)
        # access_token = tokens["access_token"]
        # refresh_token = tokens["refresh_token"]
        # self.kc.logout(access_token, refresh_token)
        # del request.session["tokens"]
        if "user" in request.session:
            del request.session["user"]
        return Response("User logged out successfully", status_code=200)


class Callback(EndpointHandler):
    async def get(self, request: Request) -> Response:

        # validate state
        state = request.query_params["state"]
        _state = request.session.pop("state", "unknown")
        if state != _state:
            return PlainTextResponse("Invalid state", status_code=403)

        # retrieve tokens
        code = request.query_params["code"]
        tokens = self.kc.callback(code)
        # request.session["tokens"] = json.dumps(tokens)

        # retrieve user info
        access_token = tokens["access_token"]
        user = self.kc.fetch_userinfo(access_token)
        request.session["user"] = json.dumps(user)

        return RedirectResponse(self.redirect_uri)


class AuthenticationMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        callback_url: str = "https://localhost:8000/kc/callback",
        redirect_uri: str = "/",
        logout_uri: str = "/kc/logout",
    ) -> None:
        self.app = app
        self.callback_url = callback_url
        self.redirect_uri = redirect_uri
        self.logout_uri = logout_uri
        self.kc = Client(callback_url)

    @staticmethod
    def get_url(request: Request) -> str:
        return f"{request.url.scheme}://{request.url.netloc}{request.url.path}"

    @staticmethod
    def is_http(scope: Any) -> bool:
        return scope["type"] == "http"

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        # handle http requests
        if self.is_http(scope):
            request = Request(scope, receive)

            # handle callback request
            if self.get_url(request) == self.callback_url:
                await Callback(
                    scope, receive, send, kc=self.kc, redirect_uri=self.redirect_uri
                )
                return

            # handle logout request
            elif request.url.path == self.logout_uri:
                await Logout(scope, receive, send, kc=self.kc)
                return

            # handle unauthorized requests
            elif "user" not in request.session:
                await Login(scope, receive, send, kc=self.kc)
                return

            # handle authorized requests
            else:
                await self.app(scope, receive, send)
                return

        # handle non http requests
        await self.app(scope, receive, send)
