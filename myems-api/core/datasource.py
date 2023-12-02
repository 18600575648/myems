import uuid
from datetime import datetime, timezone, timedelta
import falcon
import mysql.connector
import simplejson as json
from core.useractivity import user_logger, admin_control
import config


class DataSourceCollection:
    @staticmethod
    def __init__():
        """"Initializes DataSourceCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        admin_control(req)
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid "
                 " FROM tbl_gateways ")
        cursor.execute(query)
        rows_gateways = cursor.fetchall()
        gateway_dict = dict()
        if rows_gateways is not None and len(rows_gateways) > 0:
            for row in rows_gateways:
                gateway_dict[row[0]] = {"id": row[0],
                                        "name": row[1],
                                        "uuid": row[2]}

        query = (" SELECT id, name, uuid, gateway_id, protocol, connection, last_seen_datetime_utc, description "
                 " FROM tbl_data_sources "
                 " ORDER BY id ")
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        cnx.close()

        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                if isinstance(row[6], datetime):
                    last_seen_datetime_local = row[6].replace(tzinfo=timezone.utc) + timedelta(minutes=timezone_offset)
                    last_seen_datetime = last_seen_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
                else:
                    last_seen_datetime = None
                meta_result = {"id": row[0],
                               "name": row[1],
                               "uuid": row[2],
                               "gateway": gateway_dict.get(row[3]),
                               "protocol": row[4],
                               "connection": row[5],
                               "last_seen_datetime": last_seen_datetime,
                               "description": row[7]
                               }

                result.append(meta_result)

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
                                   description='API.INVALID_DATA_SOURCE_NAME')
        name = str.strip(new_values['data']['name'])

        if 'gateway_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['gateway_id'], int) or \
                new_values['data']['gateway_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_GATEWAY_ID')
        gateway_id = new_values['data']['gateway_id']

        if 'protocol' not in new_values['data'].keys() \
                or new_values['data']['protocol'] not in \
                ('bacnet-ip',
                 'cassandra',
                 'clickhouse',
                 'coap',
                 'controllogix',
                 'dlt645',
                 'elexon-bmrs',
                 'iec104',
                 'influxdb',
                 'lora',
                 'modbus-rtu',
                 'modbus-tcp',
                 'mongodb',
                 'mqtt-md4220',
                 'mqtt-seg',
                 'mqtt',
                 'mysql',
                 'opc-ua',
                 'oracle',
                 'postgresql',
                 'profibus',
                 'profinet',
                 's7',
                 'simulation',
                 'sqlserver',
                 'tdengine',
                 'weather',):
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_PROTOCOL')
        protocol = new_values['data']['protocol']

        if 'connection' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['connection'], str) or \
                len(str.strip(new_values['data']['connection'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CONNECTION')
        connection = str.strip(new_values['data']['connection'])

        if 'description' in new_values['data'].keys() and \
                new_values['data']['description'] is not None and \
                len(str(new_values['data']['description'])) > 0:
            description = str.strip(new_values['data']['description'])
        else:
            description = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_data_sources "
                       " WHERE name = %s ", (name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.DATA_SOURCE_NAME_IS_ALREADY_IN_USE')

        cursor.execute(" SELECT name "
                       " FROM tbl_gateways "
                       " WHERE id = %s ", (gateway_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_GATEWAY_ID')

        add_values = (" INSERT INTO tbl_data_sources (name, uuid, gateway_id, protocol, connection, description) "
                      " VALUES (%s, %s, %s, %s, %s, %s) ")
        cursor.execute(add_values, (name,
                                    str(uuid.uuid4()),
                                    gateway_id,
                                    protocol,
                                    connection,
                                    description))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_201
        resp.location = '/datasources/' + str(new_id)


class DataSourceItem:
    @staticmethod
    def __init__():
        """"Initializes DataSourceItem"""
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        query = (" SELECT id, name, uuid "
                 " FROM tbl_gateways ")
        cursor.execute(query)
        rows_gateways = cursor.fetchall()
        gateway_dict = dict()
        if rows_gateways is not None and len(rows_gateways) > 0:
            for row in rows_gateways:
                gateway_dict[row[0]] = {"id": row[0],
                                        "name": row[1],
                                        "uuid": row[2]}

        query = (" SELECT id, name, uuid, gateway_id, protocol, connection, last_seen_datetime_utc, description "
                 " FROM tbl_data_sources "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()
        if row is None:
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

        if isinstance(row[6], datetime):
            last_seen_datetime_local = row[6].replace(tzinfo=timezone.utc) + \
                timedelta(minutes=timezone_offset)
            last_seen_datetime = last_seen_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            last_seen_datetime = None

        result = {"id": row[0],
                  "name": row[1],
                  "uuid": row[2],
                  "gateway": gateway_dict.get(row[3]),
                  "protocol": row[4],
                  "connection": row[5],
                  "last_seen_datetime": last_seen_datetime,
                  "description": row[7]
                  }

        resp.text = json.dumps(result)

    @staticmethod
    @user_logger
    def on_delete(req, resp, id_):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_data_sources "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        # check if this data source is being used by any meters
        cursor.execute(" SELECT DISTINCT(m.name) "
                       " FROM tbl_meters m, tbl_meters_points mp, tbl_points p, tbl_data_sources ds "
                       " WHERE m.id = mp.meter_id AND mp.point_id = p.id AND p.data_source_id = ds.id "
                       "       AND ds.id = %s "
                       " LIMIT 1 ",
                       (id_,))
        row_meter = cursor.fetchone()
        if row_meter is not None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400,
                                   title='API.BAD_REQUEST',
                                   description='API.THIS_DATA_SOURCE_IS_BEING_USED_BY_A_METER' + row_meter[0])

        cursor.execute(" DELETE FROM tbl_points WHERE data_source_id = %s ", (id_,))
        cursor.execute(" DELETE FROM tbl_data_sources WHERE id = %s ", (id_,))
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
                                   description='API.INVALID_DATA_SOURCE_ID')

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_NAME')
        name = str.strip(new_values['data']['name'])

        if 'gateway_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['gateway_id'], int) or \
                new_values['data']['gateway_id'] <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_GATEWAY_ID')
        gateway_id = new_values['data']['gateway_id']

        if 'protocol' not in new_values['data'].keys() \
                or new_values['data']['protocol'] not in \
                ('bacnet-ip',
                 'cassandra',
                 'clickhouse',
                 'coap',
                 'controllogix',
                 'dlt645',
                 'elexon-bmrs',
                 'iec104',
                 'influxdb',
                 'lora',
                 'modbus-rtu',
                 'modbus-tcp',
                 'mongodb',
                 'mqtt-md4220',
                 'mqtt-seg',
                 'mqtt',
                 'mysql',
                 'opc-ua',
                 'oracle',
                 'postgresql',
                 'profibus',
                 'profinet',
                 's7',
                 'simulation',
                 'sqlserver',
                 'tdengine',
                 'weather',):
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_PROTOCOL')
        protocol = new_values['data']['protocol']

        if 'connection' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['connection'], str) or \
                len(str.strip(new_values['data']['connection'])) == 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_CONNECTION')
        connection = str.strip(new_values['data']['connection'])

        if 'description' in new_values['data'].keys() and \
                new_values['data']['description'] is not None and \
                len(str(new_values['data']['description'])) > 0:
            description = str.strip(new_values['data']['description'])
        else:
            description = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_data_sources "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_gateways "
                       " WHERE id = %s ", (gateway_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_GATEWAY_ID')

        update_row = (" UPDATE tbl_data_sources "
                      " SET name = %s, gateway_id = %s, protocol = %s, connection = %s, description = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (name,
                                    gateway_id,
                                    protocol,
                                    connection,
                                    description,
                                    id_,))
        cnx.commit()

        cursor.close()
        cnx.close()

        resp.status = falcon.HTTP_200


class DataSourcePointCollection:
    @staticmethod
    def __init__():
        """"Initializes DataSourcePointCollection"""
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        admin_control(req)
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(status=falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DATA_SOURCE_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_data_sources "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.close()
            raise falcon.HTTPError(status=falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DATA_SOURCE_NOT_FOUND')

        result = list()
        # Get points of the data source
        # NOTE: there is no uuid in tbl_points
        query_point = (" SELECT id, name, object_type, "
                       "        units, high_limit, low_limit, higher_limit, lower_limit, ratio, "
                       "        is_trend, is_virtual, address, description "
                       " FROM tbl_points "
                       " WHERE data_source_id = %s "
                       " ORDER BY id ")
        cursor.execute(query_point, (id_,))
        rows_point = cursor.fetchall()

        if rows_point is not None and len(rows_point) > 0:
            for row in rows_point:
                meta_result = {"id": row[0],
                               "name": row[1],
                               "object_type": row[2],
                               "units": row[3],
                               "high_limit": row[4],
                               "low_limit": row[5],
                               "higher_limit": row[6],
                               "lower_limit": row[7],
                               "ratio": float(row[8]),
                               "is_trend": bool(row[9]),
                               "is_virtual": bool(row[10]),
                               "address": row[11],
                               "description": row[12]}
                result.append(meta_result)

        cursor.close()
        cnx.close()
        resp.text = json.dumps(result)
