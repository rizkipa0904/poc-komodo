import json
from odoo.http import request

class ApiService:

    def _error(self, message, status):
        return request.make_response(
            json.dumps({"status": "error", "message": message}), status=status
        )

    def _simplify_many2one(self, records):
        for record in records:
            for k, v in record.items():
                if isinstance(v, (list, tuple)) and len(v) == 2 and isinstance(v[0], int):
                    record[k] = v[0]
        return records

    def _create_nested_records(self, model_name, values):
        model = request.env[model_name]
        processed_values = {}
        for field, val in values.items():
            rel_field = model._fields.get(field)

            if isinstance(val, dict) and rel_field and hasattr(rel_field, 'comodel_name'):
                nested_model = rel_field.comodel_name
                nested_rec = self._create_nested_records(nested_model, val)
                processed_values[field] = nested_rec.id

            elif isinstance(val, list) and rel_field and hasattr(rel_field, 'comodel_name'):
                nested_model = rel_field.comodel_name
                nested_ids = [self._create_nested_records(nested_model, v).id for v in val if isinstance(v, dict)]
                processed_values[field] = [(6, 0, nested_ids)]

            else:
                processed_values[field] = val

        return model.create(processed_values)

    # Example Payload for Nested Update
    #{
    #    "values": {
    #        "name": "Updated Parent",
    #        "child_ids": [
    #        {"id": 5, "name": "Updated Child"},        // Update
    #        {"name": "New Child"},                     // Create
    #        {"id": 6, "_delete": true}                 // Delete
    #        ]
    #    }
    #}
    def _update_nested_records(self, model_name, record, values):
        model = request.env[model_name]
        for field, val in values.items():
            rel_field = model._fields.get(field)

            if isinstance(val, dict) and rel_field and hasattr(rel_field, 'comodel_name'):
                nested_model = request.env[rel_field.comodel_name]
                if 'id' in val:
                    nested_record = nested_model.browse(val['id'])
                    if nested_record.exists():
                        nested_record.write(val)
                        values[field] = nested_record.id
                else:
                    nested_record = nested_model.create(val)
                    values[field] = nested_record.id

            elif isinstance(val, list) and rel_field and hasattr(rel_field, 'comodel_name'):
                nested_model = request.env[rel_field.comodel_name]
                commands = []
                for item in val:
                    if isinstance(item, dict):
                        if item.get('_delete') and 'id' in item:
                            commands.append((2, item['id'], 0))
                        elif 'id' in item:
                            existing = nested_model.browse(item['id'])
                            if existing.exists():
                                existing.write(item)
                                commands.append((1, existing.id, item))
                        else:
                            new = nested_model.create(item)
                            commands.append((4, new.id))
                values[field] = commands

        record.write(values)

    def _delete_nested_records(self, record, model_name):
        model = request.env[model_name]
        for field_name, field in model._fields.items():
            if hasattr(field, 'comodel_name') and field.type in ('many2one', 'one2many', 'many2many'):
                val = record[field_name]
                if val and hasattr(val, 'unlink'):
                    val.unlink()

    def generate_response(self, method, model, domain):
        from odoo.http import request
        import json

        option = request.env['connection.api'].search([('model_id', '=', model)], limit=1)
        if not option:
            return self._error("No record created for the model", 404)

        model_name = option.model_id.model
        data = {}
        if method != 'DELETE':
            try:
                data = json.loads(request.httprequest.data)
            except:
                return self._error("Invalid JSON Data", 400)

        fields = data.get('fields', []) if isinstance(data.get('fields', []), list) else []

        try:
            if method == 'GET':
                if not option.is_get:
                    return self._error("Method Not Allowed", 405)

                order_by = data.get('order_by', [])
                order = None
                if order_by and isinstance(order_by, list):
                    try:
                        order = ', '.join(f"{item['field']} {item['direction'].lower()}" for item in order_by)
                    except:
                        return self._error("Invalid format in 'order_by'", 400)

                result_records = request.env[model_name].search_read(domain=domain or [], fields=fields, order=order)
                records = self._simplify_many2one(result_records)
                return request.make_response(json.dumps({'records': records}, default=str), status=200)

            elif method == 'POST':
                if not option.is_post:
                    return self._error("Method Not Allowed", 405)

                new_record = self._create_nested_records(model_name, data.get('values', {}))
                result = request.env[model_name].search_read([('id', '=', new_record.id)], fields=fields)
                return request.make_response(json.dumps({'New record': result}, default=str), status=201)

            elif method == 'PUT':
                if not option.is_put:
                    return self._error("Method Not Allowed", 405)
                if not domain:
                    return self._error("No ID Provided", 400)

                record = request.env[model_name].browse(int(domain))
                if not record.exists():
                    return self._error("Record not found", 404)

                self._update_nested_records(model_name, record, data.get('values', {}))
                updated = request.env[model_name].search_read([('id', '=', record.id)], fields=fields)
                return request.make_response(json.dumps({'Updated record': updated}, default=str), status=200)

            elif method == 'DELETE':
                if not option.is_delete:
                    return self._error("Method Not Allowed", 405)
                if not domain:
                    return self._error("No ID Provided", 400)

                record = request.env[model_name].browse(int(domain))
                if not record.exists():
                    return self._error("Record not found", 404)

                self._delete_nested_records(record, model_name)
                deleted_info = request.env[model_name].search_read([('id', '=', record.id)], fields=['id', 'display_name'])
                record.unlink()
                return request.make_response(json.dumps({"Record deleted": deleted_info}, default=str), status=200)

            return self._error("Unsupported method", 405)

        except Exception as e:
            return self._error(f"Unexpected server error: {str(e)}", 500)
