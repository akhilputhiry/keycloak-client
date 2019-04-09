#! -*- coding: utf-8 -*-
from flask import Flask, redirect, request, jsonify
from keycloak import KeycloakClient


api = Flask(__name__)
keycloak_client = KeycloakClient()


@api.route('/auth', methods=['GET'])
def auth():
    """ Initiate authentication """
    return redirect(keycloak_client.authentication_url)


@api.route('/auth/callback', methods=['GET'])
def auth_callback():
    """ Authentication callback handler """
    code = request.args.get('code')
    aat = keycloak_client.authentication_callback(code)
    return jsonify(aat)


@api.route('/auth/permission-ticket', methods=['GET'])
def auth_permission_ticket():
    """ Generate permission ticket """
    return jsonify(keycloak_client.permission_ticket)


@api.route('/auth/rpt', methods=['POST'])
def auth_rpt():
    """ Generate RPT (request party token) """
    aat = request.headers.get('Authorization')
    permission_ticket = request.json.get('permission_ticket')
    rpt = keycloak_client.retrieve_rpt(aat, permission_ticket)
    return jsonify(rpt)


@api.route('/auth/refresh', methods=['POST'])
def auth_refresh():
    refresh_token = request.json.get('refresh_token')
    token = keycloak_client.refresh_access_token(refresh_token)
    return jsonify(token)


if __name__ == '__main__':
    api.run()