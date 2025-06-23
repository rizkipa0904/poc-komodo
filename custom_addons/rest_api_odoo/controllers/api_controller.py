# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Ayana KP (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
# Modified by Galang 
# Latest Modified Date 2025-05-05


import json
import logging
from odoo import http
from odoo.http import request
from odoo.addons.rest_api_odoo.services.api_service import ApiService

_logger = logging.getLogger(__name__)


class ApiController(http.Controller):
    def __init__(self):
        self.api_service = ApiService()

    def auth_api_key(self, api_key):
        user_id = request.env['res.users'].sudo().search([('api_key', '=', api_key)])
        return bool(api_key and user_id)

    def authenticate_user(self):
        api_key = request.httprequest.headers.get('api-key')
        username = request.httprequest.headers.get('username')
        password = request.httprequest.headers.get('password')

        if not self.auth_api_key(api_key):
            return request.make_response(
                json.dumps({"status": "error", "message": "Invalid API Key"}), status=401
            )

        credential = {'login': username, 'password': password, 'type': 'password'}
        try:
            request.session.authenticate(request.session.db, credential)
        except Exception:
            return request.make_response(
                json.dumps({"status": "error", "message": "Invalid login credentials"}), status=401
            )

        return True

    def validate_model(self, model_name):
        model_id = request.env['ir.model'].search([('model', '=', model_name)])
        if not model_id:
            return request.make_response(
                json.dumps({"status": "error", "message": "Invalid model, check spelling or ensure the related module is installed"}),
                status=404
            )
        return model_id

    def build_domain(self, kw):
        domain = []
        for key in kw:
            if key == 'model':
                continue
            values = request.httprequest.args.getlist(key)
            if len(values) == 1:
                domain.append((key, '=', values[0]))
            elif len(values) > 1:
                domain.append((key, 'in', values))
        return domain

    @http.route(['/request/get'], type='http', auth='none', methods=['GET'], csrf=False)
    def fetch_data_get(self, **kw):
        if (auth := self.authenticate_user()) is not True:
            return auth

        model_id = self.validate_model(kw.get('model'))
        if isinstance(model_id, http.Response):
            return model_id

        domain = self.build_domain(kw)
        try:
            return self.api_service.generate_response('GET', model_id.id, domain)
        except:
            result = json.dumps({"status": "error",
                                "message": "Bad Request"})
            return request.make_response(data=result,status=400)

    @http.route(['/request/post'], type='http', auth='none', methods=['POST'], csrf=False)
    def fetch_data_post(self, **kw):
        if (auth := self.authenticate_user()) is not True:
            return auth

        model_id = self.validate_model(kw.get('model'))
        if isinstance(model_id, http.Response):
            return model_id

        domain = int(kw.get('id', 0))
        try:
            return self.api_service.generate_response('POST', model_id.id, domain)
        except:
            result = json.dumps({"status": "error",
                                "message": "Bad Request"})
            return request.make_response(data=result,status=400)

    @http.route(['/request/put'], type='http', auth='none', methods=['PUT'], csrf=False)
    def fetch_data_put(self, **kw):
        if (auth := self.authenticate_user()) is not True:
            return auth

        model_id = self.validate_model(kw.get('model'))
        if isinstance(model_id, http.Response):
            return model_id

        domain = int(kw.get('id', 0))
        try:
            return self.api_service.generate_response('PUT', model_id.id, domain)
        except:
            result = json.dumps({"status": "error",
                                "message": "Bad Request"})
            return request.make_response(data=result,status=400)

    @http.route(['/request/delete'], type='http', auth='none', methods=['DELETE'], csrf=False)
    def fetch_data_delete(self, **kw):
        if (auth := self.authenticate_user()) is not True:
            return auth

        model_id = self.validate_model(kw.get('model'))
        if isinstance(model_id, http.Response):
            return model_id

        domain = int(kw.get('id', 0))
        try:
            return self.api_service.generate_response('DELETE', model_id.id, domain)
        except:
            result = json.dumps({"status": "error",
                                "message": "Bad Request"})
            return request.make_response(data=result,status=400)

    @http.route(['/auth_odoo'], type="http", auth="none", csrf=False, methods=['GET'])
    def odoo_connect(self, **kw):
        username = request.httprequest.headers.get('username')
        password = request.httprequest.headers.get('password')
        db = request.httprequest.headers.get('db')
        try:
            request.session.update(http.get_default_session(), db=db)
            credential = {'login': username, 'password': password, 'type': 'password'}
            auth = request.session.authenticate(db, credential)
            user = request.env['res.users'].browse(auth['uid'])
            api_key = request.env.user.generate_api(username)
            return request.make_response(json.dumps({
                "status": "success",
                "message": "API Key Generated",
                "User": user.name,
                "api-key": api_key
            }), status=200)
        except:
            return request.make_response(json.dumps({"status": "error", "message": "Bad Request"}), status=400)
