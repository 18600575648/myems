import falcon
import simplejson as json
import mysql.connector
import config
import uuid


class DistributionCircuitCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp):
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor(dictionary=True)

        query = (" SELECT id, name, uuid "
                 " FROM tbl_distribution_systems ")
        cursor.execute(query)
        rows_distribution_systems = cursor.fetchall()

        distribution_system_dict = dict()
        if rows_distribution_systems is not None and len(rows_distribution_systems) > 0:
            for row in rows_distribution_systems:
                distribution_system_dict[row['id']] = {"id": row['id'],
                                                       "name": row['name'],
                                                       "uuid": row['uuid']}
        query = (" SELECT id, name, uuid, distribution_system_id, "
                 "        distribution_room, switchgear, peak_load, peak_current, customers, meters "
                 " FROM tbl_distribution_circuits "
                 " ORDER BY id ")
        cursor.execute(query)
        rows_distribution_circuits = cursor.fetchall()

        result = list()
        if rows_distribution_circuits is not None and len(rows_distribution_circuits) > 0:
            for row in rows_distribution_circuits:
                distribution_system = distribution_system_dict.get(row['distribution_system_id'])
                meta_result = {"id": row['id'],
                               "name": row['name'],
                               "uuid": row['uuid'],
                               "distribution_system": distribution_system,
                               "distribution_room": row['distribution_room'],
                               "switchgear": row['switchgear'],
                               "peak_load": row['peak_load'],
                               "peak_current": row['peak_current'],
                               "customers": row['customers'],
                               "meters": row['meters']}
                result.append(meta_result)

        cursor.close()
        cnx.disconnect()
        resp.body = json.dumps(result)

    @staticmethod
    def on_post(req, resp):
        """Handles POST requests"""
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.ERROR', description=ex)

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_CIRCUIT_NAME')
        name = str.strip(new_values['data']['name'])

        if 'distribution_system_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['distribution_system_id'], int) or \
                new_values['data']['distribution_system_id'] <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_SYSTEM_ID')
        distribution_system_id = new_values['data']['distribution_system_id']

        if 'distribution_room' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['distribution_room'], str) or \
                len(str.strip(new_values['data']['distribution_room'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_ROOM')
        distribution_room = str.strip(new_values['data']['distribution_room'])

        if 'switchgear' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['switchgear'], str) or \
                len(str.strip(new_values['data']['switchgear'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SWITCHGEAR')
        switchgear = str.strip(new_values['data']['switchgear'])

        if 'peak_load' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['peak_load'], float) or
                     isinstance(new_values['data']['peak_load'], int)):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PEAK_LOAD')
        peak_load = float(new_values['data']['peak_load'])

        if 'peak_current' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['peak_current'], float) or
                     isinstance(new_values['data']['peak_current'], int)):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PEAK_CURRENT')
        peak_current = float(new_values['data']['peak_current'])

        if 'customers' in new_values['data'].keys() and \
                new_values['data']['customers'] is not None and \
                len(str(new_values['data']['customers'])) > 0:
            customers = str.strip(new_values['data']['customers'])
        else:
            customers = None

        if 'meters' in new_values['data'].keys() and \
                new_values['data']['meters'] is not None and \
                len(str(new_values['data']['meters'])) > 0:
            meters = str.strip(new_values['data']['meters'])
        else:
            meters = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_distribution_systems "
                       " WHERE id = %s ",
                       (distribution_system_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_SYSTEM_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_distribution_circuits "
                       " WHERE distribution_system_id = %s AND name = %s ",
                       (distribution_system_id, name,))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.BAD_REQUEST',
                                   description='API.DISTRIBUTION_CIRCUIT_NAME_IS_ALREADY_IN_USE')

        add_values = (" INSERT INTO tbl_distribution_circuits "
                      "    (name, uuid, distribution_system_id,"
                      "     distribution_room, switchgear, peak_load, peak_current, customers, meters) "
                      " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ")
        cursor.execute(add_values, (name,
                                    str(uuid.uuid4()),
                                    distribution_system_id,
                                    distribution_room,
                                    switchgear,
                                    peak_load,
                                    peak_current,
                                    customers,
                                    meters))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_201
        resp.location = '/distributioncircuits/' + str(new_id)


class DistributionCircuitItem:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_METER_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor(dictionary=True)

        query = (" SELECT id, name, uuid "
                 " FROM tbl_distribution_systems ")
        cursor.execute(query)
        rows_distribution_systems = cursor.fetchall()

        distribution_system_dict = dict()
        if rows_distribution_systems is not None and len(rows_distribution_systems) > 0:
            for row in rows_distribution_systems:
                distribution_system_dict[row['id']] = {"id": row['id'],
                                                       "name": row['name'],
                                                       "uuid": row['uuid']}

        query = (" SELECT id, name, uuid, distribution_system_id, "
                 "        distribution_room, switchgear, peak_load, peak_current, customers, meters "
                 " FROM tbl_distribution_circuits "
                 " WHERE id = %s ")
        cursor.execute(query, (id_,))
        row = cursor.fetchone()
        cursor.close()
        cnx.disconnect()

        if row is None:
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_CIRCUIT_NOT_FOUND')
        else:
            distribution_system = distribution_system_dict.get(row['distribution_system_id'])
            meta_result = {"id": row['id'],
                           "name": row['name'],
                           "uuid": row['uuid'],
                           "distribution_system": distribution_system,
                           "distribution_room": row['distribution_room'],
                           "switchgear": row['switchgear'],
                           "peak_load": row['peak_load'],
                           "peak_current": row['peak_current'],
                           "customers": row['customers'],
                           "meters": row['meters']}

        resp.body = json.dumps(meta_result)

    @staticmethod
    def on_delete(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_CIRCUIT_ID')
        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_distribution_circuits "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_CIRCUIT_NOT_FOUND')

        # delete relation with points
        cursor.execute(" DELETE FROM tbl_distribution_circuits_points "
                       " WHERE distribution_circuit_id = %s ", (id_,))
        # delete distribution circuit itself
        cursor.execute(" DELETE FROM tbl_distribution_circuits "
                       " WHERE id = %s ", (id_,))
        cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_204

    @staticmethod
    def on_put(req, resp, id_):
        """Handles PUT requests"""
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.EXCEPTION', description=ex)

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_CIRCUIT_ID')

        new_values = json.loads(raw_json)

        if 'name' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['name'], str) or \
                len(str.strip(new_values['data']['name'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_CIRCUIT_NAME')
        name = str.strip(new_values['data']['name'])

        if 'distribution_system_id' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['distribution_system_id'], int) or \
                new_values['data']['distribution_system_id'] <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_SYSTEM_ID')
        distribution_system_id = new_values['data']['distribution_system_id']

        if 'distribution_room' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['distribution_room'], str) or \
                len(str.strip(new_values['data']['distribution_room'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_ROOM')
        distribution_room = str.strip(new_values['data']['distribution_room'])

        if 'switchgear' not in new_values['data'].keys() or \
                not isinstance(new_values['data']['switchgear'], str) or \
                len(str.strip(new_values['data']['switchgear'])) == 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_SWITCHGEAR')
        switchgear = str.strip(new_values['data']['switchgear'])

        if 'peak_load' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['peak_load'], float) or
                     isinstance(new_values['data']['peak_load'], int)):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PEAK_LOAD')
        peak_load = float(new_values['data']['peak_load'])

        if 'peak_current' not in new_values['data'].keys() or \
                not (isinstance(new_values['data']['peak_current'], float) or
                     isinstance(new_values['data']['peak_current'], int)):
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_PEAK_CURRENT')
        peak_current = float(new_values['data']['peak_current'])

        if 'customers' in new_values['data'].keys() and \
                new_values['data']['customers'] is not None and \
                len(str(new_values['data']['customers'])) > 0:
            customers = str.strip(new_values['data']['customers'])
        else:
            customers = None

        if 'meters' in new_values['data'].keys() and \
                new_values['data']['meters'] is not None and \
                len(str(new_values['data']['meters'])) > 0:
            meters = str.strip(new_values['data']['meters'])
        else:
            meters = None

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_distribution_systems "
                       " WHERE id = %s ",
                       (distribution_system_id,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_SYSTEM_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_distribution_circuits "
                       " WHERE distribution_system_id = %s AND name = %s AND id != %s ",
                       (distribution_system_id, name, id_))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.BAD_REQUEST',
                                   description='API.DISTRIBUTION_CIRCUIT_NAME_IS_ALREADY_IN_USE')

        update_row = (" UPDATE tbl_distribution_circuits "
                      " SET name = %s, distribution_system_id = %s, distribution_room = %s, switchgear = %s, "
                      "     peak_load = %s, peak_current = %s, customers = %s, meters = %s "
                      " WHERE id = %s ")
        cursor.execute(update_row, (name,
                                    distribution_system_id,
                                    distribution_room,
                                    switchgear,
                                    peak_load,
                                    peak_current,
                                    customers,
                                    meters,
                                    id_))
        cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_200


class DistributionCircuitPointCollection:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp, id_):
        resp.status = falcon.HTTP_200

    @staticmethod
    def on_get(req, resp, id_):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_CIRCUIT_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor(dictionary=True)

        query = (" SELECT id, name, uuid "
                 " FROM tbl_distribution_systems ")
        cursor.execute(query)
        rows_distribution_systems = cursor.fetchall()

        distribution_system_dict = dict()
        if rows_distribution_systems is not None and len(rows_distribution_systems) > 0:
            for row in rows_distribution_systems:
                distribution_system_dict[row['uuid']] = {"id": row['id'],
                                                         "name": row['name'],
                                                         "uuid": row['uuid']}

        cursor.execute(" SELECT name "
                       " FROM tbl_distribution_circuits "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_CIRCUIT_NOT_FOUND')

        query = (" SELECT p.id AS point_id, p.name AS point_name, p.address AS point_address, "
                 "        dc.id AS distribution_circuit_id, dc.name AS distribution_circuit_name, "
                 "        dc.uuid AS distribution_circuit_uuid "
                 " FROM tbl_points p, tbl_distribution_circuits_points dcp, tbl_distribution_circuits dc "
                 " WHERE dcp.distribution_circuit_id = %s AND p.id = dcp.point_id "
                 "       AND dcp.distribution_circuit_id = dc.id "
                 " ORDER BY p.name ")
        cursor.execute(query, (id_,))
        rows = cursor.fetchall()

        result = list()
        if rows is not None and len(rows) > 0:
            for row in rows:
                meta_result = {"id": row['point_id'], "name": row['point_name'], "address": row['point_address'],
                               "distribution_circuit": {"id": row['distribution_circuit_id'],
                                                        "name": row['distribution_circuit_name'],
                                                        "uuid": row['distribution_circuit_uuid']}}
                result.append(meta_result)

        resp.body = json.dumps(result)

    @staticmethod
    def on_post(req, resp, id_):
        """Handles POST requests"""
        try:
            raw_json = req.stream.read().decode('utf-8')
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.EXCEPTION', description=ex)

        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_CIRCUIT_ID')

        new_values = json.loads(raw_json)

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " from tbl_distribution_circuits "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_CIRCUIT_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_points "
                       " WHERE id = %s ", (new_values['data']['point_id'],))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.POINT_NOT_FOUND')

        query = (" SELECT id " 
                 " FROM tbl_distribution_circuits_points "
                 " WHERE distribution_circuit_id = %s AND point_id = %s")
        cursor.execute(query, (id_, new_values['data']['point_id'],))
        if cursor.fetchone() is not None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_400, title='API.ERROR',
                                   description='API.DISTRIBUTION_CIRCUIT_POINT_RELATION_EXISTED')

        add_row = (" INSERT INTO tbl_distribution_circuits_points (distribution_circuit_id, point_id) "
                   " VALUES (%s, %s) ")
        cursor.execute(add_row, (id_, new_values['data']['point_id'],))
        new_id = cursor.lastrowid
        cnx.commit()
        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_201
        resp.location = '/distributioncircuits/' + str(id_) + '/points/' + str(new_values['data']['point_id'])


class DistributionCircuitPointItem:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp, id_, pid):
            resp.status = falcon.HTTP_200

    @staticmethod
    def on_delete(req, resp, id_, pid):
        if not id_.isdigit() or int(id_) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_DISTRIBUTION_CIRCUIT_ID')

        if not pid.isdigit() or int(pid) <= 0:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_POINT_ID')

        cnx = mysql.connector.connect(**config.myems_system_db)
        cursor = cnx.cursor()

        cursor.execute(" SELECT name "
                       " FROM tbl_distribution_circuits "
                       " WHERE id = %s ", (id_,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_CIRCUIT_NOT_FOUND')

        cursor.execute(" SELECT name "
                       " FROM tbl_points "
                       " WHERE id = %s ", (pid,))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.POINT_NOT_FOUND')

        cursor.execute(" SELECT id "
                       " FROM tbl_distribution_circuits_points "
                       " WHERE distribution_circuit_id = %s AND point_id = %s ", (id_, pid))
        if cursor.fetchone() is None:
            cursor.close()
            cnx.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND',
                                   description='API.DISTRIBUTION_CIRCUIT_POINT_RELATION_NOT_FOUND')

        cursor.execute(" DELETE FROM tbl_distribution_circuits_points "
                       " WHERE distribution_circuit_id = %s AND point_id = %s ", (id_, pid))
        cnx.commit()

        cursor.close()
        cnx.disconnect()

        resp.status = falcon.HTTP_204

