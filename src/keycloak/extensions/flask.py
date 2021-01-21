# -*- coding: utf-8 -*-
import json
from typing import Dict, Callable, Any

from flask import Flask, Config, Request, redirect
from flask.sessions import SessionInterface

from werkzeug.wrappers import Response

from .. import Client


class ProxyApp:
    def __init__(self, config: Config):
        self.config = config

    @property
    def secret_key(self) -> str:
        return self.config["SECRET_KEY"]

    @property
    def session_cookie_name(self) -> str:
        return self.config["SESSION_COOKIE_NAME"]

    @property
    def permanent_session_lifetime(self) -> int:
        return self.config["PERMANENT_SESSION_LIFETIME"]  # pragma: nocover


class AuthenticationMiddleware:
    session_interface: SessionInterface = None  # type: ignore

    def __init__(
        self,
        app: Flask,
        config: Config,
        session_interface: SessionInterface,
        callback_url: str = "http://localhost:5000/kc/callback",
        redirect_uri: str = "/",
        logout_uri: str = "/kc/logout",
    ) -> None:
        self.app = app
        self.config = config
        self.session_interface = session_interface
        self.callback_url = callback_url
        self.redirect_uri = redirect_uri
        self.logout_uri = logout_uri
        self.kc = Client(callback_url)
        self.proxy_app = ProxyApp(config)

    def _response(
        self, environ: Dict, start_response: Callable, session: Any, response: Callable
    ) -> Callable:
        self.session_interface.save_session(self.proxy_app, session, response)
        return response(environ, start_response)

    def __call__(self, environ: Dict, start_response: Callable) -> Callable:
        response = None
        request = Request(environ)
        session = self.session_interface.open_session(  # type: ignore
            self.proxy_app, request
        )

        # callback request
        if request.base_url == self.callback_url:
            response = self.callback(session, request)
            return self._response(environ, start_response, session, response)

        # logout request
        elif request.path == self.logout_uri:
            self.logout(session)
            return self.app(environ, start_response)

        # unauthorized request
        elif "user" not in session:
            response = self.login(session)
            return self._response(environ, start_response, session, response)

        # authorized request
        else:
            return self.app(environ, start_response)

    def login(self, session: Dict) -> Response:
        """ Initiate authentication """
        url, state = self.kc.login()
        session["state"] = state
        return redirect(url)

    def callback(self, session: Dict, request: Request) -> Response:
        """ Authentication callback handler """

        # validate state
        state = request.args.get("state", "unknown")
        _state = session.pop("state", None)
        if state != _state:
            return Response("Invalid state", status=403)

        # fetch user tokens
        code: str = request.args.get("code", "unknown")
        tokens = self.kc.callback(code)
        session["tokens"] = json.dumps(tokens)

        # fetch user info
        access_token = tokens["access_token"]
        user = self.kc.fetch_userinfo(access_token)
        session["user"] = json.dumps(user)

        return redirect(self.redirect_uri)

    def logout(self, session: Dict) -> None:
        if "tokens" in session:
            tokens = json.loads(session["tokens"])
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            self.kc.logout(access_token, refresh_token)
            del session["tokens"]
        if "user" in session:
            del session["user"]
