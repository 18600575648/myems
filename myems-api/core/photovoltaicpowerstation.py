import uuid
from datetime import datetime, timezone, timedelta
import falcon
import mysql.connector
import simplejson as json
from core.useractivity import user_logger, admin_control, access_control
import config


class PhotovoltaicPowerStationCollection:
    @staticmethod
    def __init__():
        """"Initializes PhotovoltaicPowerStationCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        access_control(req)
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
                 "        address, postal_code, latitude, longitude, capacity, "
                 "        contact_id, cost_center_id, svg, description "
                 " FROM tbl_photovoltaic_power_stations "
                 " ORDER BY id ")
        cursor.execute(query)
        rows_spaces = cursor.fetchall()

        result = list()
        if rows_spaces is not None and len(rows_spaces) > 0:
            for row in rows_spaces:
                contact = contact_dict.get(row[8], None)
                cost_center = cost_center_dict.get(row[9], None)

                meta_result = {"id": row[0],
                               "name": row[1],
                               "uuid": row[2],
                               "address": row[3],
                               "postal_code": row[4],
                               "latitude": row[5],
                               "longitude": row[6],
                               "capacity": row[7],
                               "contact": contact,
                               "cost_center": cost_center,
                               "svg": row[10],
                               "description": row[11],
                               "qrcode": 'photovoltaicpowerstation:' + row[2]}
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
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_NAME')
        name = str.strip(new_values['data']['name'])

        if 'address' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['address'], str) or \
                len(str.strip(new_values['data']['address'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ADDRESS_VALUE')
        address = str.strip(new_values['data']['address'])

        if 'postal_code' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['postal_code'], str) or \
                len(str.strip(new_values['data']['postal_code'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POSTAL_CODE_VALUE')
        postal_code = str.strip(new_values['data']['postal_code'])

        if 'latitude' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['latitude'], float) or
                     isinstance(new_values['data']['latitude'], int)) or \
                new_values['data']['latitude'] < -90.0 or \
                new_values['data']['latitude'] > 90.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_LATITUDE_VALUE')
        latitude = new_values['data']['latitude']

        if 'longitude' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['longitude'], float) or
                     isinstance(new_values['data']['longitude'], int)) or \
                new_values['data']['longitude'] < -180.0 or \
                new_values['data']['longitude'] > 180.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_LONGITUDE_VALUE')
        longitude = new_values['data']['longitude']

        if 'capacity' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['capacity'], float) or
                     isinstance(new_values['data']['capacity'], int)) or \
                new_values['data']['capacity'] <= 0.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CAPACITY_VALUE')
        capacity = new_values['data']['capacity']

        if 'contact_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['contact_id'], int) or \
                new_values['data']['contact_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CONTACT_ID')
        contact_id = new_values['data']['contact_id']

        if 'cost_center_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['cost_center_id'], int) or \
                new_values['data']['cost_center_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COST_CENTER_ID')
        cost_center_id = new_values['data']['cost_center_id']

        if 'svg' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['svg'], str) or \
                len(str.strip(new_values['data']['svg'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SVG')
        svg = str.strip(new_values['data']['svg'])

        if 'description' in new_values['data'].keys() and \
                new_values['data']['description'] is not None and \
                len(str(new_values['data']['description'])) > 0:
            description = str.strip(new_values['data']['description'])
        else:
            description = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_photovoltaic_power_stations "
                       " WHERE name = %s ", (name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NAME_IS_ALREADY_IN_USE')

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

        add_values = (" INSERT INTO tbl_photovoltaic_power_stations "
                      "    (name, uuid, address, postal_code, latitude, longitude, capacity, "
                      "     contact_id, cost_center_id, svg, description) "
                      " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ")
        cursor.execute(add_values, (name,
                                    str(uuid.uuid4()),
                                    address,
                                    postal_code,
                                    latitude,
                                    longitude,
                                    capacity,
                                    contact_id,
                                    cost_center_id,
                                    svg,
                                    description))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/photovoltaicpowerstations/' + str(new_id)


class PhotovoltaicPowerStationItem:
    @staticmethod
    def __init__():
        """"Initializes PhotovoltaicPowerStationItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        access_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_ID')

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
                 "        address, postal_code, latitude, longitude, capacity, "
                 "        contact_id, cost_center_id, svg, description "
                 " FROM tbl_photovoltaic_power_stations "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()

        if row is None:
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NOT_FOUND')
        else:
            contact = contact_dict.get(row[8], None)
            cost_center = cost_center_dict.get(row[9], None)
            meta_result = {"id": row[0],
                           "name": row[1],
                           "uuid": row[2],
                           "address": row[3],
                           "postal_code": row[4],
                           "latitude": row[5],
                           "longitude": row[6],
                           "capacity": row[7],
                           "contact": contact,
                           "cost_center": cost_center,
                           "svg": row[10],
                           "description": row[11],
                           "qrcode": 'photovoltaicpowerstation:' + row[2]}

        resp.text = json.dumps(meta_result)

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_photovoltaic_power_stations "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_photovoltaic_power_stations WHERE id = %s ", (id_,))
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
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_ID')

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_NAME')
        name = str.strip(new_values['data']['name'])

        if 'address' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['address'], str) or \
                len(str.strip(new_values['data']['address'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ADDRESS_VALUE')
        address = str.strip(new_values['data']['address'])

        if 'postal_code' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['postal_code'], str) or \
                len(str.strip(new_values['data']['postal_code'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POSTAL_CODE_VALUE')
        postal_code = str.strip(new_values['data']['postal_code'])

        if 'latitude' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['latitude'], float) or
                     isinstance(new_values['data']['latitude'], int)) or \
                new_values['data']['latitude'] < -90.0 or \
                new_values['data']['latitude'] > 90.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_LATITUDE_VALUE')
        latitude = new_values['data']['latitude']

        if 'longitude' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['longitude'], float) or
                     isinstance(new_values['data']['longitude'], int)) or \
                new_values['data']['longitude'] < -180.0 or \
                new_values['data']['longitude'] > 180.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_LONGITUDE_VALUE')
        longitude = new_values['data']['longitude']

        if 'capacity' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['capacity'], float) or
                     isinstance(new_values['data']['capacity'], int)) or \
                new_values['data']['capacity'] <= 0.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CAPACITY_VALUE')
        capacity = new_values['data']['capacity']

        if 'contact_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['contact_id'], int) or \
                new_values['data']['contact_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CONTACT_ID')
        contact_id = new_values['data']['contact_id']

        if 'cost_center_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['cost_center_id'], int) or \
                new_values['data']['cost_center_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COST_CENTER_ID')
        cost_center_id = new_values['data']['cost_center_id']

        if 'svg' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['svg'], str) or \
                len(str.strip(new_values['data']['svg'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SVG')
        svg = str.strip(new_values['data']['svg'])

        if 'description' in new_values['data'].keys() and \
                new_values['data']['description'] is not None and \
                len(str(new_values['data']['description'])) > 0:
            description = str.strip(new_values['data']['description'])
        else:
            description = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_photovoltaic_power_stations "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_photovoltaic_power_stations "
                       " WHERE name = %s AND id != %s ", (name, id_))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NAME_IS_ALREADY_IN_USE')

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

        update_row = (" UPDATE tbl_photovoltaic_power_stations "
                      " SET name = %s, address = %s, postal_code = %s, latitude = %s, longitude = %s, capacity = %s, "
                      "     contact_id = %s, cost_center_id = %s, "
                      "     svg = %s, description = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (name,
                                    address,
                                    postal_code,
                                    latitude,
                                    longitude,
                                    capacity,
                                    contact_id,
                                    cost_center_id,
                                    svg,
                                    description,
                                    id_))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_200


class PhotovoltaicPowerStationExport:
    @staticmethod
    def __init__():
        """"Initializes PhotovoltaicPowerStationExport"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        access_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_ID')

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
                 "        address, postal_code, latitude, longitude, capacity, "
                 "        contact_id, cost_center_id, svg, description "
                 " FROM tbl_photovoltaic_power_stations "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()

        if row is None:
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NOT_FOUND')
        else:
            contact = contact_dict.get(row[8], None)
            cost_center = cost_center_dict.get(row[9], None)
            meta_result = {"id": row[0],
                           "name": row[1],
                           "uuid": row[2],
                           "address": row[3],
                           "postal_code": row[4],
                           "latitude": row[5],
                           "longitude": row[6],
                           "capacity": row[7],
                           "contact": contact,
                           "cost_center": cost_center,
                           "svg": row[10],
                           "description": row[11]}

        resp.text = json.dumps(meta_result)


class PhotovoltaicPowerStationImport:
    @staticmethod
    def __init__():
        """"Initializes PhotovoltaicPowerStationImport"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

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

        if 'name' not in new_values.keys() or \
                not isinstance(new_values['name'], str) or \
                len(str.strip(new_values['name'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_NAME')
        name = str.strip(new_values['name'])

        if 'address' not in new_values.keys() or \
                not isinstance(new_values['address'], str) or \
                len(str.strip(new_values['address'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_ADDRESS_VALUE')
        address = str.strip(new_values['address'])

        if 'postal_code' not in new_values.keys() or \
                not isinstance(new_values['postal_code'], str) or \
                len(str.strip(new_values['postal_code'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POSTAL_CODE_VALUE')
        postal_code = str.strip(new_values['postal_code'])

        if 'latitude' not in new_values.keys() or \
                not (isinstance(new_values['latitude'], float) or
                     isinstance(new_values['latitude'], int)) or \
                new_values['latitude'] < -90.0 or \
                new_values['latitude'] > 90.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_LATITUDE_VALUE')
        latitude = new_values['latitude']

        if 'longitude' not in new_values.keys() or \
                not (isinstance(new_values['longitude'], float) or
                     isinstance(new_values['longitude'], int)) or \
                new_values['longitude'] < -180.0 or \
                new_values['longitude'] > 180.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_LONGITUDE_VALUE')
        longitude = new_values['longitude']

        if 'capacity' not in new_values.keys() or \
                not (isinstance(new_values['capacity'], float) or
                     isinstance(new_values['capacity'], int)) or \
                new_values['capacity'] <= 0.0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CAPACITY_VALUE')
        capacity = new_values['capacity']

        if 'id' not in new_values['contact'].keys() or \
                not isinstance(new_values['contact']['id'], int) or \
                new_values['contact']['id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CONTACT_ID')
        contact_id = new_values['contact']['id']

        if 'id' not in new_values['cost_center'].keys() or \
                not isinstance(new_values['cost_center']['id'], int) or \
                new_values['cost_center']['id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_COST_CENTER_ID')
        cost_center_id = new_values['cost_center']['id']

        if 'svg' not in new_values.keys() or \
                not isinstance(new_values['svg'], str) or \
                len(str.strip(new_values['svg'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SVG')
        svg = str.strip(new_values['svg'])

        if 'description' in new_values.keys() and \
                new_values['description'] is not None and \
                len(str(new_values['description'])) > 0:
            description = str.strip(new_values['description'])
        else:
            description = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_photovoltaic_power_stations "
                       " WHERE name = %s ", (name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NAME_IS_ALREADY_IN_USE')

        cursor.execute(" SELECT name "
                       " FROM tbl_contacts "
                       " WHERE id = %s ",
                       (new_values['contact']['id'],))
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.CONTACT_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_cost_centers "
                       " WHERE id = %s ",
                       (new_values['cost_center']['id'],))
        row = cursor.fetchone()
        if row is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.COST_CENTER_NOT_FOUND')

        add_values = (" INSERT INTO tbl_photovoltaic_power_stations "
                      "    (name, uuid, address, postal_code, latitude, longitude, capacity, "
                      "     contact_id, cost_center_id, svg, description) "
                      " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ")
        cursor.execute(add_values, (name,
                                    str(uuid.uuid4()),
                                    address,
                                    postal_code,
                                    latitude,
                                    longitude,
                                    capacity,
                                    contact_id,
                                    cost_center_id,
                                    svg,
                                    description))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/photovoltaicpowerstations/' + str(new_id)


class PhotovoltaicPowerStationClone:
    @staticmethod
    def __init__():
        """"Initializes PhotovoltaicPowerStationClone"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    @user_logger
    def on_post(req, resp, id_):
        access_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PHOTOVOLTAIC_POWER_STATION_ID')

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
                 "        address, postal_code, latitude, longitude, capacity, "
                 "        contact_id, cost_center_id, svg, description "
                 " FROM tbl_photovoltaic_power_stations "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()

        if row is None:
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.PHOTOVOLTAIC_POWER_STATION_NOT_FOUND')
        else:
            contact = contact_dict.get(row[8], None)
            cost_center = cost_center_dict.get(row[9], None)
            meta_result = {"id": row[0],
                           "name": row[1],
                           "uuid": row[2],
                           "address": row[3],
                           "postal_code": row[4],
                           "latitude": row[5],
                           "longitude": row[6],
                           "capacity": row[7],
                           "contact": contact,
                           "cost_center": cost_center,
                           "svg": row[10],
                           "description": row[11]}
            timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
            if config.utc_offset[0] == '-':
                timezone_offset = -timezone_offset
            new_name = (str.strip(meta_result['name'])
                        + (datetime.now()
                           + timedelta(minutes=timezone_offset)).isoformat(sep='-', timespec='seconds'))
            add_values = (" INSERT INTO tbl_photovoltaic_power_stations "
                          "    (name, uuid, address, postal_code, latitude, longitude, capacity, "
                          "     contact_id, cost_center_id, svg, description) "
                          " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ")
            cursor.execute(add_values, (new_name,
                                        str(uuid.uuid4()),
                                        meta_result['address'],
                                        meta_result['postal_code'],
                                        meta_result['latitude'],
                                        meta_result['longitude'],
                                        meta_result['capacity'],
                                        meta_result['contact']['id'],
                                        meta_result['cost_center']['id'],
                                        meta_result['svg'],
                                        meta_result['description']))
            new_id = cursor.lastrowid
            cnx.commit()
            cursor.close()
            cnx.close()

            resp.status = falcon.HTTP_201
            resp.location = '/photovoltaicpowerstations/' + str(new_id)

