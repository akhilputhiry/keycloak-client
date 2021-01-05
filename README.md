[![Documentation Status](https://readthedocs.org/projects/keycloak-client/badge/?version=latest)](https://keycloak-client.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.com/akhilputhiry/keycloak-client.svg?branch=master)](https://travis-ci.com/akhilputhiry/keycloak-client)
![CI](https://github.com/akhilputhiry/keycloak-client/workflows/CI/badge.svg?branch=master)
[![PyPI version](https://badge.fury.io/py/keycloak.svg)](https://badge.fury.io/py/keycloak)
[![codecov](https://codecov.io/gh/akhilputhiry/keycloak-client/branch/master/graph/badge.svg)](https://codecov.io/gh/akhilputhiry/keycloak-client)
[![Maintainability](https://api.codeclimate.com/v1/badges/3c0d666b018207a00d27/maintainability)](https://codeclimate.com/github/akhilputhiry/keycloak-client/maintainability)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/keycloak.svg)](https://pypistats.org/packages/keycloak)

This repo contains a python client for [Keycloak](https://www.keycloak.org/).
Documentation is available in [https://keycloak-client.readthedocs.io](https://keycloak-client.readthedocs.io)


### Installation

```
pip install keycloak                # install only client   
pip install "keycloak[docs]"        # install client + sphinx   
pip install "keycloak[extensions]"  # install client + django/flask/starlette   
pip install "keycloak[complete]"    # insgall client + sphinx + django/flask/starlette   
```

### Web Framework Support

We provide prebuilt middlewares for the following frameworks

* Flask
* Starlette
* Django
