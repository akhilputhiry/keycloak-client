# -*- coding: utf-8 -*-
import json
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from keycloak import Client


class AuthenticationMiddleware:
    def __init__(self, get_response: Callable):
        self.get_response = get_response
        self.kc = Client(self.callback_url)

    @property
    def redirect_uri(self) -> str:
        return settings.KEYCLOAK_REDIRECT_URI

    @property
    def logout_uri(self) -> str:
        return settings.KEYCLOAK_LOGOUT_URI

    @property
    def callback_url(self) -> str:
        return settings.KEYCLOAK_CALLBACK_URL

    def callback(self, request: HttpRequest) -> HttpResponse:

        # validate state
        state = request.GET.get("state", "unknown")
        _state = request.session.pop("state", None)
        if state != _state:
            return HttpResponse("Invalid state", status=403)

        # fetch user tokens
        code: str = request.GET.get("code", "unknown")
        tokens = self.kc.callback(code)
        request.session["tokens"] = json.dumps(tokens)

        # fetch user info
        access_token = tokens["access_token"]
        user = self.kc.fetch_userinfo(access_token)
        request.session["user"] = json.dumps(user)

        return HttpResponseRedirect(self.redirect_uri)

    def login(self, request: HttpRequest) -> HttpResponse:
        """ Initiate authentication """
        url, state = self.kc.login()
        request.session["state"] = state
        return HttpResponseRedirect(url)

    def logout(self, request: HttpRequest) -> None:
        if "tokens" in request.session
            tokens = json.loads(request.session["tokens"])
            access_token = tokens["access_token"]
            refresh_token = tokens["refresh_token"]
            self.kc.logout(access_token, refresh_token)
            del request.session["tokens"]
        if "user" in request.session:
            del request.session["user"]

    def __call__(self, request: HttpRequest) -> HttpResponse:

        # callback request
        if request.build_absolute_uri(request.path) == self.callback_url:
            return self.callback(request)

        # logout request
        elif request.path == self.logout_uri:
            self.logout(request)
            return self.get_response(request)

        # unauthorized request
        elif "user" not in request.session:
            return self.login(request)

        # authorized request
        else:
            return self.get_response(request)
