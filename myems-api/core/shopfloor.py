import uuid

import falcon
import mysql.connector
import simplejson as json

import config
from core.useractivity import user_logger, admin_control


class ShopfloorCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid "
                 " FROM tbl_contacts ")
        cursor.execute(query)
        rows_contacts = cursor.fetchall()

        contact_dict = dict()
        if rows_contacts is not None and len(rows_contacts) > 0:
            for row in rows_contacts:
                contact_dict[row[0]] = {"id": row[0],
                                        "name": row[1],
                                        "uuid": row[2]}

        query = (" SELECT id, name, uuid "
                 " FROM tbl_cost_centers ")
        cursor.execute(query)
        rows_cost_centers = cursor.fetchall()

        cost_center_dict = dict()
        if rows_cost_centers is not None and len(rows_cost_centers) > 0:
            for row in rows_cost_centers:
                cost_center_dict[row[0]] = {"id": row[0],
                                            "name": row[1],
                                            "uuid": row[2]}

        query = (" SELECT id, name, uuid, "
                 "        area, is_input_counted, "
                 "        contact_id, cost_center_id, description "
                 " FROM tbl_shopfloors "
                 " ORDER BY id ")
        cursor.execute(query)
        rows_shopfloors = cursor.fetchall()

        result = list()
        if rows_shopfloors is not None and len(rows_shopfloors) > 0:
            for row in rows_shopfloors:
                contact = contact_dict.get(row[5], None)
                cost_center = cost_center_dict.get(row[6], None)
                meta_result = {"id": row[0],
                               "name": row[1],
                               "uuid": row[2],
                               "area": row[3],
                               "is_input_counted": bool(row[4]),
                               "contact": contact,
                               "cost_center": cost_center,
                               "description": row[7],
                               "qrcode": "shopfloor:" + row[2]}
                result.append(meta_result)

        cursor.close()
        cnx.close()
        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_NAME')
        name = str.strip(new_values['data']['name'])

        if 'area' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['area'], float) or
                     isinstance(new_values['data']['area'], int)) or \
                new_values['data']['area'] <= 0.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_AREA_VALUE')
        area = new_values['data']['area']

        if 'is_input_counted' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['is_input_counted'], bool):
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_IS_INPUT_COUNTED_VALUE')
        is_input_counted = new_values['data']['is_input_counted']

        if 'contact_id' in new_values['data'].keys():
            if new_values['data']['contact_id'] <= 0:
                raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_CONTACT_ID')
            contact_id = new_values['data']['contact_id']
        else:
            contact_id = None

        if 'cost_center_id' in new_values['data'].keys():
            if new_values['data']['cost_center_id'] <= 0:
                raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_COST_CENTER_ID')
            cost_center_id = new_values['data']['cost_center_id']
        else:
            cost_center_id = None

        if 'description' in new_values['data'].keys() and \
                new_values['data']['description'] is not None and \
                len(str(new_values['data']['description'])) > 0:
            description = str.strip(new_values['data']['description'])
        else:
            description = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE name = %s ", (name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.SHOPFLOOR_NAME_IS_ALREADY_IN_USE')

        if contact_id is not None:
            cursor.execute(" SELECT name "
                           " FROM tbl_contacts "
                           " WHERE id = %s ",
                           (new_values['data']['contact_id'],))
            row = cursor.fetchone()
            if row is None:
                cursor.close()
                cnx.close()
                raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                       description='API.CONTACT_NOT_FOUND')

        if cost_center_id is not None:
            cursor.execute(" SELECT name "
                           " FROM tbl_cost_centers "
                           " WHERE id = %s ",
                           (new_values['data']['cost_center_id'],))
            row = cursor.fetchone()
            if row is None:
                cursor.close()
                cnx.close()
                raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                       description='API.COST_CENTER_NOT_FOUND')

        add_values = (" INSERT INTO tbl_shopfloors "
                      "    (name, uuid, area, is_input_counted, "
                      "     contact_id, cost_center_id, description) "
                      " VALUES (%s, %s, %s, %s, %s, %s, %s) ")
        cursor.execute(add_values, (name,
                                    str(uuid.uuid4()),
                                    area,
                                    is_input_counted,
                                    contact_id,
                                    cost_center_id,
                                    description))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(new_id)


class ShopfloorItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid "
                 " FROM tbl_contacts ")
        cursor.execute(query)
        rows_contacts = cursor.fetchall()

        contact_dict = dict()
        if rows_contacts is not None and len(rows_contacts) > 0:
            for row in rows_contacts:
                contact_dict[row[0]] = {"id": row[0],
                                        "name": row[1],
                                        "uuid": row[2]}

        query = (" SELECT id, name, uuid "
                 " FROM tbl_cost_centers ")
        cursor.execute(query)
        rows_cost_centers = cursor.fetchall()

        cost_center_dict = dict()
        if rows_cost_centers is not None and len(rows_cost_centers) > 0:
            for row in rows_cost_centers:
                cost_center_dict[row[0]] = {"id": row[0],
                                            "name": row[1],
                                            "uuid": row[2]}

        query = (" SELECT id, name, uuid, "
                 "        area, is_input_counted, contact_id, cost_center_id, description "
                 " FROM tbl_shopfloors "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()

        if row is None:
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')
        else:
            contact = contact_dict.get(row[5], None)
            cost_center = cost_center_dict.get(row[6], None)
            meta_result = {"id": row[0],
                           "name": row[1],
                           "uuid": row[2],
                           "area": row[3],
                           "is_input_counted": bool(row[4]),
                           "contact": contact,
                           "cost_center": cost_center,
                           "description": row[7],
                           "qrcode": "shopfloor:" + row[2]}

        resp.text = json.dumps(meta_result)

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        # check relation with spaces
        cursor.execute(" SELECT space_id "
                       " FROM tbl_spaces_shopfloors "
                       " WHERE shopfloor_id = %s ",
                       (id_,))
        rows_spaces = cursor.fetchall()
        if rows_spaces is not None and len(rows_spaces) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_SPACES')

        # check relation with equipments
        cursor.execute(" SELECT equipment_id "
                       " FROM tbl_shopfloors_equipments "
                       " WHERE shopfloor_id = %s ",
                       (id_,))
        rows_equipments = cursor.fetchall()
        if rows_equipments is not None and len(rows_equipments) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_EQUIPMENTS')

        # check relation with meters
        cursor.execute(" SELECT meter_id "
                       " FROM tbl_shopfloors_meters "
                       " WHERE shopfloor_id = %s ",
                       (id_,))
        rows_meters = cursor.fetchall()
        if rows_meters is not None and len(rows_meters) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_METERS')

        # check relation with offline meters
        cursor.execute(" SELECT offline_meter_id "
                       " FROM tbl_shopfloors_offline_meters "
                       " WHERE shopfloor_id = %s ",
                       (id_,))
        rows_offline_meters = cursor.fetchall()
        if rows_offline_meters is not None and len(rows_offline_meters) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_OFFLINE_METERS')

        # check relation with points
        cursor.execute(" SELECT point_id "
                       " FROM tbl_shopfloors_points "
                       " WHERE shopfloor_id = %s ", (id_,))
        rows_points = cursor.fetchall()
        if rows_points is not None and len(rows_points) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_POINTS')

        # check relation with sensor
        cursor.execute(" SELECT sensor_id "
                       " FROM tbl_shopfloors_sensors "
                       " WHERE shopfloor_id = %s ",
                       (id_,))
        rows_sensors = cursor.fetchall()
        if rows_sensors is not None and len(rows_sensors) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_SENSORS')

        # check relation with virtual meter
        cursor.execute(" SELECT virtual_meter_id "
                       " FROM tbl_shopfloors_virtual_meters "
                       " WHERE shopfloor_id = %s ",
                       (id_,))
        rows_virtual_meters = cursor.fetchall()
        if rows_virtual_meters is not None and len(rows_virtual_meters) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_VIRTUAL_METERS')

        # check relation with command
        cursor.execute(" SELECT command_id "
                       " FROM tbl_shopfloors_commands "
                       " WHERE command_id = %s ",
                       (id_,))
        rows_commands = cursor.fetchall()
        if rows_commands is not None and len(rows_commands) > 0:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THERE_IS_RELATION_WITH_COMMANDS')

        cursor.execute(" DELETE FROM tbl_shopfloors WHERE id = %s ", (id_,))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204

    @staticmethod
    @user_logger
    def on_put(req, resp, id_):
        """Handles PUT requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_NAME')
        name = str.strip(new_values['data']['name'])

        if 'area' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['area'], float) or
                     isinstance(new_values['data']['area'], int)) or \
                new_values['data']['area'] <= 0.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_AREA_VALUE')
        area = new_values['data']['area']

        if 'is_input_counted' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['is_input_counted'], bool):
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_IS_INPUT_COUNTED_VALUE')
        is_input_counted = new_values['data']['is_input_counted']

        if 'contact_id' in new_values['data'].keys():
            if new_values['data']['contact_id'] <= 0:
                raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_CONTACT_ID')
            contact_id = new_values['data']['contact_id']
        else:
            contact_id = None

        if 'cost_center_id' in new_values['data'].keys():
            if new_values['data']['cost_center_id'] <= 0:
                raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description='API.INVALID_COST_CENTER_ID')
            cost_center_id = new_values['data']['cost_center_id']
        else:
            cost_center_id = None

        if 'description' in new_values['data'].keys() and \
                new_values['data']['description'] is not None and \
                len(str(new_values['data']['description'])) > 0:
            description = str.strip(new_values['data']['description'])
        else:
            description = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE name = %s AND id != %s ", (name, id_))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.SHOPFLOOR_NAME_IS_ALREADY_IN_USE')

        if contact_id is not None:
            cursor.execute(" SELECT name "
                           " FROM tbl_contacts "
                           " WHERE id = %s ",
                           (new_values['data']['contact_id'],))
            row = cursor.fetchone()
            if row is None:
                cursor.close()
                cnx.close()
                raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                       description='API.CONTACT_NOT_FOUND')

        if cost_center_id is not None:
            cursor.execute(" SELECT name "
                           " FROM tbl_cost_centers "
                           " WHERE id = %s ",
                           (new_values['data']['cost_center_id'],))
            row = cursor.fetchone()
            if row is None:
                cursor.close()
                cnx.close()
                raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                       description='API.COST_CENTER_NOT_FOUND')

        update_row = (" UPDATE tbl_shopfloors "
                      " SET name = %s, area = %s, is_input_counted = %s, contact_id = %s, cost_center_id = %s, "
                      "     description = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (name,
                                    area,
                                    is_input_counted,
                                    contact_id,
                                    cost_center_id,
                                    description,
                                    id_))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_200


class ShopfloorEquipmentCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorEquipmentCollection"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT e.id, e.name, e.uuid "
                 " FROM tbl_shopfloors s, tbl_shopfloors_equipments se, tbl_equipments e "
                 " WHERE se.shopfloor_id = s.id AND e.id = se.equipment_id AND s.id = %s "
                 " ORDER BY e.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2]}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'equipment_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['equipment_id'], int) or \
                new_values['data']['equipment_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_EQUIPMENT_ID')
        equipment_id = new_values['data']['equipment_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_equipments "
                       " WHERE id = %s ", (equipment_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.EQUIPMENT_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_equipments "
                 " WHERE shopfloor_id = %s AND equipment_id = %s")
        cursor.execute(query, (id_, equipment_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_EQUIPMENT_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_equipments (shopfloor_id, equipment_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, equipment_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/equipments/' + str(equipment_id)


class ShopfloorEquipmentItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorEquipmentItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_, eid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, eid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not eid.isdigit() or int(eid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_EQUIPMENT_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_equipments "
                       " WHERE id = %s ", (eid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.EQUIPMENT_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_equipments "
                       " WHERE shopfloor_id = %s AND equipment_id = %s ", (id_, eid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_EQUIPMENT_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_equipments "
                       " WHERE shopfloor_id = %s AND equipment_id = %s ", (id_, eid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204


class ShopfloorMeterCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorMeterCollection"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT id, name, uuid "
                 " FROM tbl_energy_categories ")
        cursor.execute(query)
        rows_energy_categories = cursor.fetchall()

        energy_category_dict = dict()
        if rows_energy_categories is not None and len(rows_energy_categories) > 0:
            for row in rows_energy_categories:
                energy_category_dict[row[0]] = {"id": row[0],
                                                "name": row[1],
                                                "uuid": row[2]}

        query = (" SELECT m.id, m.name, m.uuid, m.energy_category_id "
                 " FROM tbl_shopfloors s, tbl_shopfloors_meters sm, tbl_meters m "
                 " WHERE sm.shopfloor_id = s.id AND m.id = sm.meter_id AND s.id = %s "
                 " ORDER BY m.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                energy_category = energy_category_dict.get(row[3], None)
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "energy_category": energy_category}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'meter_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['meter_id'], int) or \
                new_values['data']['meter_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_METER_ID')
        meter_id = new_values['data']['meter_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_meters "
                       " WHERE id = %s ", (meter_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.METER_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_meters "
                 " WHERE shopfloor_id = %s AND meter_id = %s")
        cursor.execute(query, (id_, meter_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_METER_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_meters (shopfloor_id, meter_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, meter_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/meters/' + str(meter_id)


class ShopfloorMeterItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorMeterItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_, mid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, mid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not mid.isdigit() or int(mid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_meters "
                       " WHERE id = %s ", (mid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.METER_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_meters "
                       " WHERE shopfloor_id = %s AND meter_id = %s ", (id_, mid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_METER_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_meters WHERE shopfloor_id = %s AND meter_id = %s ", (id_, mid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204


class ShopfloorOfflineMeterCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorOfflineMeterCollection"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT id, name, uuid "
                 " FROM tbl_energy_categories ")
        cursor.execute(query)
        rows_energy_categories = cursor.fetchall()

        energy_category_dict = dict()
        if rows_energy_categories is not None and len(rows_energy_categories) > 0:
            for row in rows_energy_categories:
                energy_category_dict[row[0]] = {"id": row[0],
                                                "name": row[1],
                                                "uuid": row[2]}

        query = (" SELECT m.id, m.name, m.uuid, m.energy_category_id "
                 " FROM tbl_shopfloors s, tbl_shopfloors_offline_meters sm, tbl_offline_meters m "
                 " WHERE sm.shopfloor_id = s.id AND m.id = sm.offline_meter_id AND s.id = %s "
                 " ORDER BY m.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                energy_category = energy_category_dict.get(row[3], None)
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "energy_category": energy_category}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'offline_meter_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['offline_meter_id'], int) or \
                new_values['data']['offline_meter_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_OFFLINE_METER_ID')
        offline_meter_id = new_values['data']['offline_meter_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_offline_meters "
                       " WHERE id = %s ", (offline_meter_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.OFFLINE_METER_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_offline_meters "
                 " WHERE shopfloor_id = %s AND offline_meter_id = %s")
        cursor.execute(query, (id_, offline_meter_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_OFFLINE_METER_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_offline_meters (shopfloor_id, offline_meter_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, offline_meter_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/offlinemeters/' + str(offline_meter_id)


class ShopfloorOfflineMeterItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorOfflineMeterItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_, mid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, mid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not mid.isdigit() or int(mid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_OFFLINE_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_offline_meters "
                       " WHERE id = %s ", (mid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.OFFLINE_METER_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_offline_meters "
                       " WHERE shopfloor_id = %s AND offline_meter_id = %s ", (id_, mid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_OFFLINE_METER_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_offline_meters "
                       " WHERE shopfloor_id = %s AND offline_meter_id = %s ", (id_, mid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204


class ShopfloorPointCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorPointCollection"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT id, name, uuid "
                 " FROM tbl_data_sources ")
        cursor.execute(query)
        rows_data_sources = cursor.fetchall()

        data_source_dict = dict()
        if rows_data_sources is not None and len(rows_data_sources) > 0:
            for row in rows_data_sources:
                data_source_dict[row[0]] = {"id": row[0],
                                            "name": row[1],
                                            "uuid": row[2]}

        query = (" SELECT p.id, p.name, p.data_source_id "
                 " FROM tbl_shopfloors s, tbl_shopfloors_points sp, tbl_points p "
                 " WHERE sp.shopfloor_id = s.id AND p.id = sp.point_id AND s.id = %s "
                 " ORDER BY p.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                data_source = data_source_dict.get(row[2], None)
                meta_result = {"id": row[0], "name": row[1], "data_source": data_source}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'point_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['point_id'], int) or \
                new_values['data']['point_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POINT_ID')
        point_id = new_values['data']['point_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_points "
                       " WHERE id = %s ", (point_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.POINT_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_points "
                 " WHERE shopfloor_id = %s AND point_id = %s")
        cursor.execute(query, (id_, point_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_POINT_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_points (shopfloor_id, point_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, point_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/points/' + str(point_id)


class ShopfloorPointItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorPointItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_, pid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, pid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not pid.isdigit() or int(pid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POINT_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_points "
                       " WHERE id = %s ", (pid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.POINT_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_points "
                       " WHERE shopfloor_id = %s AND point_id = %s ", (id_, pid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_POINT_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_points "
                       " WHERE shopfloor_id = %s AND point_id = %s ", (id_, pid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204


class ShopfloorSensorCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorSensorCollection"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT se.id, se.name, se.uuid "
                 " FROM tbl_shopfloors sp, tbl_shopfloors_sensors ss, tbl_sensors se "
                 " WHERE ss.shopfloor_id = sp.id AND se.id = ss.sensor_id AND sp.id = %s "
                 " ORDER BY se.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2]}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'sensor_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['sensor_id'], int) or \
                new_values['data']['sensor_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SENSOR_ID')
        sensor_id = new_values['data']['sensor_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_sensors "
                       " WHERE id = %s ", (sensor_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SENSOR_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_sensors "
                 " WHERE shopfloor_id = %s AND sensor_id = %s")
        cursor.execute(query, (id_, sensor_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_SENSOR_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_sensors (shopfloor_id, sensor_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, sensor_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/sensors/' + str(sensor_id)


class ShopfloorSensorItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorSensorItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_, sid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, sid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not sid.isdigit() or int(sid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SENSOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_sensors "
                       " WHERE id = %s ", (sid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SENSOR_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_sensors "
                       " WHERE shopfloor_id = %s AND sensor_id = %s ", (id_, sid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_SENSOR_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_sensors WHERE shopfloor_id = %s AND sensor_id = %s ", (id_, sid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204


class ShopfloorVirtualMeterCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorVirtualMeterCollection"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT id, name, uuid "
                 " FROM tbl_energy_categories ")
        cursor.execute(query)
        rows_energy_categories = cursor.fetchall()

        energy_category_dict = dict()
        if rows_energy_categories is not None and len(rows_energy_categories) > 0:
            for row in rows_energy_categories:
                energy_category_dict[row[0]] = {"id": row[0],
                                                "name": row[1],
                                                "uuid": row[2]}

        query = (" SELECT m.id, m.name, m.uuid, m.energy_category_id "
                 " FROM tbl_shopfloors s, tbl_shopfloors_virtual_meters sm, tbl_virtual_meters m "
                 " WHERE sm.shopfloor_id = s.id AND m.id = sm.virtual_meter_id AND s.id = %s "
                 " ORDER BY m.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                energy_category = energy_category_dict.get(row[3], None)
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2],
                               "energy_category": energy_category}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'virtual_meter_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['virtual_meter_id'], int) or \
                new_values['data']['virtual_meter_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_VIRTUAL_METER_ID')
        virtual_meter_id = new_values['data']['virtual_meter_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_virtual_meters "
                       " WHERE id = %s ", (virtual_meter_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.VIRTUAL_METER_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_virtual_meters "
                 " WHERE shopfloor_id = %s AND virtual_meter_id = %s")
        cursor.execute(query, (id_, virtual_meter_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_VIRTUAL_METER_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_virtual_meters (shopfloor_id, virtual_meter_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, virtual_meter_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/virtualmeters/' + str(virtual_meter_id)


class ShopfloorVirtualMeterItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorVirtualMeterItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_, mid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, mid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not mid.isdigit() or int(mid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_VIRTUAL_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_virtual_meters "
                       " WHERE id = %s ", (mid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.VIRTUAL_METER_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_virtual_meters "
                       " WHERE shopfloor_id = %s AND virtual_meter_id = %s ", (id_, mid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_VIRTUAL_METER_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_virtual_meters "
                       " WHERE shopfloor_id = %s AND virtual_meter_id = %s ", (id_, mid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204


class ShopfloorWorkingCalendarCollection:
    @staticmethod
    def __init__():
        """Initializes ShopfloorWorkingCalendarCollection Class"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT wc.id, wc.name, wc.description "
                 " FROM tbl_shopfloors s, tbl_shopfloors_working_calendars swc, tbl_working_calendars wc "
                 " WHERE swc.shopfloor_id = s.id AND wc.id = swc.working_calendar_id AND s.id = %s "
                 " ORDER BY wc.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row[0], "name": row[1], "description": row[2]}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'working_calendar_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['working_calendar_id'], int) or \
                new_values['data']['working_calendar_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_WORKING_CALENDAR_ID')
        working_calendar_id = new_values['data']['working_calendar_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_working_calendars "
                       " WHERE id = %s ", (working_calendar_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.WORKING_CALENDAR_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_working_calendars "
                 " WHERE shopfloor_id = %s AND working_calendar_id = %s")
        cursor.execute(query, (id_, working_calendar_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_WORKING_CALENDAR_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_working_calendars (shopfloor_id, working_calendar_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, working_calendar_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/workingcalendars/' + str(working_calendar_id)


class ShopfloorWorkingCalendarItem:
    @staticmethod
    def __init__():
        """Initializes ShopfloorWorkingCalendarItem Class"""
        pass

    @staticmethod
    def on_options(req, resp, id_, wcid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, wcid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not wcid.isdigit() or int(wcid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_WORKING_CALENDAR_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_working_calendars "
                       " WHERE id = %s ", (wcid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.WORKING_CALENDAR_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_working_calendars "
                       " WHERE shopfloor_id = %s AND working_calendar_id = %s ", (id_, wcid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_WORKING_CALENDAR_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_working_calendars WHERE shopfloor_id = %s AND working_calendar_id = %s ", (id_, wcid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204


class ShopfloorCommandCollection:
    @staticmethod
    def __init__():
        """Initializes Class"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_STORE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        query = (" SELECT c.id, c.name, c.uuid "
                 " FROM tbl_shopfloors s, tbl_shopfloors_commands sc, tbl_commands c "
                 " WHERE sc.shopfloor_id = s.id AND c.id = sc.command_id AND s.id = %s "
                 " ORDER BY c.id ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row[0], "name": row[1], "uuid": row[2]}
                result.append(meta_result)

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        """Handles POST requests"""
        admin_control(req)
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.FAILED_TO_READ_REQUEST_STREAM')

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        new_values = json.loads(raw_json)

        if 'command_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['command_id'], int) or \
                new_values['data']['command_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COMMAND_ID')
        command_id = new_values['data']['command_id']

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_commands "
                       " WHERE id = %s ", (command_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.COMMAND_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_shopfloors_commands "
                 " WHERE shopfloor_id = %s AND command_id = %s")
        cursor.execute(query, (id_, command_id,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.ERROR',
                                   description='API.SHOPFLOOR_COMMAND_RELATION_EXISTS')

        add_row = (" INSERT INTO tbl_shopfloors_commands (shopfloor_id, command_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, command_id,))
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/shopfloors/' + str(id_) + '/commands/' + str(command_id)


class ShopfloorCommandItem:
    @staticmethod
    def __init__():
        """Initializes Class"""
        pass

    @staticmethod
    def on_options(req, resp, id_, cid):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_, cid):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SHOPFLOOR_ID')

        if not cid.isdigit() or int(cid) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COMMAND_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_shopfloors "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_commands "
                       " WHERE id = %s ", (cid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.COMMAND_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_shopfloors_commands "
                       " WHERE shopfloor_id = %s AND command_id = %s ", (id_, cid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.SHOPFLOOR_COMMAND_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_shopfloors_commands WHERE shopfloor_id = %s AND command_id = %s ", (id_, cid))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_204
