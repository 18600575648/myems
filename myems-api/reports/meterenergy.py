import falcon
import simplejson as json
import mysql.connector
import config
from datetime import datetime, timedelta, timezone
from core import utilities
from decimal import Decimal
import excelexporters.meterenergy


class Reporting:
    @staticmethod
    def __init__():
        pass

    @staticmethod
    def on_options(req, resp):
        resp.status = falcon.HTTP_200

    ####################################################################################################################
    # PROCEDURES
    # Step 1: valid parameters
    # Step 2: query the meter and energy category
    # Step 3: query associated points
    # Step 4: query base period energy consumption
    # Step 5: query reporting period energy consumption
    # Step 6: query tariff data
    # Step 7: query associated points data
    # Step 8: construct the report
    ####################################################################################################################
    @staticmethod
    def on_get(req, resp):
        print(req.params)
        meter_id = req.params.get('meterid')
        period_type = req.params.get('periodtype')
        base_period_start_datetime = req.params.get('baseperiodstartdatetime')
        base_period_end_datetime = req.params.get('baseperiodenddatetime')
        reporting_period_start_datetime_local = req.params.get('reportingperiodstartdatetime')
        reporting_period_end_datetime_local = req.params.get('reportingperiodenddatetime')

        ################################################################################################################
        # Step 1: valid parameters
        ################################################################################################################
        if meter_id is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_METER_ID')
        else:
            meter_id = str.strip(meter_id)
            if not meter_id.isdigit() or int(meter_id) <= 0:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_METER_ID')

        if period_type is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_PERIOD_TYPE')
        else:
            period_type = str.strip(period_type)
            if period_type not in ['hourly', 'daily', 'monthly', 'yearly']:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST', description='API.INVALID_PERIOD_TYPE')

        timezone_offset = int(config.utc_offset[1:3]) * 60 + int(config.utc_offset[4:6])
        if config.utc_offset[0] == '-':
            timezone_offset = -timezone_offset

        base_start_datetime_utc = None
        if base_period_start_datetime is not None and len(str.strip(base_period_start_datetime)) > 0:
            base_period_start_datetime = str.strip(base_period_start_datetime)
            try:
                base_start_datetime_utc = datetime.strptime(base_period_start_datetime, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_BASE_PERIOD_START_DATETIME")
            base_start_datetime_utc = base_start_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        base_end_datetime_utc = None
        if base_period_end_datetime is not None and len(str.strip(base_period_end_datetime)) > 0:
            base_period_end_datetime = str.strip(base_period_end_datetime)
            try:
                base_end_datetime_utc = datetime.strptime(base_period_end_datetime, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_BASE_PERIOD_END_DATETIME")
            base_end_datetime_utc = base_end_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        if base_start_datetime_utc is not None and base_end_datetime_utc is not None and \
                base_start_datetime_utc >= base_end_datetime_utc:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_BASE_PERIOD_END_DATETIME')

        if reporting_period_start_datetime_local is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description="API.INVALID_REPORTING_PERIOD_START_DATETIME")
        else:
            reporting_period_start_datetime_local = str.strip(reporting_period_start_datetime_local)
            try:
                reporting_start_datetime_utc = datetime.strptime(reporting_period_start_datetime_local,
                                                                 '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_REPORTING_PERIOD_START_DATETIME")
            reporting_start_datetime_utc = reporting_start_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        if reporting_period_end_datetime_local is None:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description="API.INVALID_REPORTING_PERIOD_END_DATETIME")
        else:
            reporting_period_end_datetime_local = str.strip(reporting_period_end_datetime_local)
            try:
                reporting_end_datetime_utc = datetime.strptime(reporting_period_end_datetime_local,
                                                               '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                       description="API.INVALID_REPORTING_PERIOD_END_DATETIME")
            reporting_end_datetime_utc = reporting_end_datetime_utc.replace(tzinfo=timezone.utc) - \
                timedelta(minutes=timezone_offset)

        if reporting_start_datetime_utc >= reporting_end_datetime_utc:
            raise falcon.HTTPError(falcon.HTTP_400, title='API.BAD_REQUEST',
                                   description='API.INVALID_REPORTING_PERIOD_END_DATETIME')

        ################################################################################################################
        # Step 2: query the meter and energy category
        ################################################################################################################
        cnx_system = mysql.connector.connect(**config.myems_system_db)
        cursor_system = cnx_system.cursor()

        cnx_energy = mysql.connector.connect(**config.myems_energy_db)
        cursor_energy = cnx_energy.cursor()

        cnx_historical = mysql.connector.connect(**config.myems_historical_db)
        cursor_historical = cnx_historical.cursor()

        cursor_system.execute(" SELECT m.id, m.name, m.cost_center_id, m.energy_category_id, "
                              "        ec.name, ec.unit_of_measure, ec.kgce, ec.kgco2e "
                              " FROM tbl_meters m, tbl_energy_categories ec "
                              " WHERE m.id = %s AND m.energy_category_id = ec.id ", (meter_id,))
        row_meter = cursor_system.fetchone()
        if row_meter is None:
            if cursor_system:
                cursor_system.close()
            if cnx_system:
                cnx_system.disconnect()

            if cursor_energy:
                cursor_energy.close()
            if cnx_energy:
                cnx_energy.disconnect()

            if cursor_historical:
                cursor_historical.close()
            if cnx_historical:
                cnx_historical.disconnect()
            raise falcon.HTTPError(falcon.HTTP_404, title='API.NOT_FOUND', description='API.METER_NOT_FOUND')

        meter = dict()
        meter['id'] = row_meter[0]
        meter['name'] = row_meter[1]
        meter['cost_center_id'] = row_meter[2]
        meter['energy_category_id'] = row_meter[3]
        meter['energy_category_name'] = row_meter[4]
        meter['unit_of_measure'] = row_meter[5]
        meter['kgce'] = row_meter[6]
        meter['kgco2e'] = row_meter[7]

        ################################################################################################################
        # Step 3: query associated points
        ################################################################################################################
        point_list = list()
        cursor_system.execute(" SELECT p.id, p.name, p.units, p.object_type  "
                              " FROM tbl_meters m, tbl_meters_points mp, tbl_points p "
                              " WHERE m.id = %s AND m.id = mp.meter_id AND mp.point_id = p.id "
                              " ORDER BY p.id ", (meter['id'],))
        rows_points = cursor_system.fetchall()
        if rows_points is not None and len(rows_points) > 0:
            for row in rows_points:
                point_list.append({"id": row[0], "name": row[1], "units": row[2], "object_type": row[3]})

        ################################################################################################################
        # Step 4: query base period energy consumption
        ################################################################################################################
        cnx_energy = mysql.connector.connect(**config.myems_energy_db)
        cursor_energy = cnx_energy.cursor()
        query = (" SELECT start_datetime_utc, actual_value "
                 " FROM tbl_meter_hourly "
                 " WHERE meter_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor_energy.execute(query, (meter['id'], base_start_datetime_utc, base_end_datetime_utc))
        rows_meter_hourly = cursor_energy.fetchall()

        rows_meter_periodically = utilities.aggregate_hourly_data_by_period(rows_meter_hourly,
                                                                            base_start_datetime_utc,
                                                                            base_end_datetime_utc,
                                                                            period_type)
        base = dict()
        base['timestamps'] = list()
        base['values'] = list()
        base['total_in_category'] = Decimal(0.0)
        base['total_in_kgce'] = Decimal(0.0)
        base['total_in_kgco2e'] = Decimal(0.0)

        for row_meter_periodically in rows_meter_periodically:
            current_datetime_local = row_meter_periodically[0].replace(tzinfo=timezone.utc) + \
                                     timedelta(minutes=timezone_offset)
            if period_type == 'hourly':
                current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
            elif period_type == 'daily':
                current_datetime = current_datetime_local.strftime('%Y-%m-%d')
            elif period_type == 'monthly':
                current_datetime = current_datetime_local.strftime('%Y-%m')
            elif period_type == 'yearly':
                current_datetime = current_datetime_local.strftime('%Y')

            actual_value = Decimal(0.0) if row_meter_periodically[1] is None else row_meter_periodically[1]
            base['timestamps'].append(current_datetime)
            base['values'].append(actual_value)
            base['total_in_category'] += actual_value
            base['total_in_kgce'] += actual_value * meter['kgce']
            base['total_in_kgco2e'] += actual_value * meter['kgco2e']

        ################################################################################################################
        # Step 5: query reporting period energy consumption
        ################################################################################################################
        query = (" SELECT start_datetime_utc, actual_value "
                 " FROM tbl_meter_hourly "
                 " WHERE meter_id = %s "
                 " AND start_datetime_utc >= %s "
                 " AND start_datetime_utc < %s "
                 " ORDER BY start_datetime_utc ")
        cursor_energy.execute(query, (meter['id'], reporting_start_datetime_utc, reporting_end_datetime_utc))
        rows_meter_hourly = cursor_energy.fetchall()

        rows_meter_periodically = utilities.aggregate_hourly_data_by_period(rows_meter_hourly,
                                                                            reporting_start_datetime_utc,
                                                                            reporting_end_datetime_utc,
                                                                            period_type)
        reporting = dict()
        reporting['timestamps'] = list()
        reporting['values'] = list()
        reporting['total_in_category'] = Decimal(0.0)
        reporting['total_in_kgce'] = Decimal(0.0)
        reporting['total_in_kgco2e'] = Decimal(0.0)

        for row_meter_periodically in rows_meter_periodically:
            current_datetime_local = row_meter_periodically[0].replace(tzinfo=timezone.utc) + \
                timedelta(minutes=timezone_offset)
            if period_type == 'hourly':
                current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
            elif period_type == 'daily':
                current_datetime = current_datetime_local.strftime('%Y-%m-%d')
            elif period_type == 'monthly':
                current_datetime = current_datetime_local.strftime('%Y-%m')
            elif period_type == 'yearly':
                current_datetime = current_datetime_local.strftime('%Y')

            actual_value = Decimal(0.0) if row_meter_periodically[1] is None else row_meter_periodically[1]

            reporting['timestamps'].append(current_datetime)
            reporting['values'].append(actual_value)
            reporting['total_in_category'] += actual_value
            reporting['total_in_kgce'] += actual_value * meter['kgce']
            reporting['total_in_kgco2e'] += actual_value * meter['kgco2e']

        ################################################################################################################
        # Step 6: query tariff data
        ################################################################################################################
        parameters_data = dict()
        parameters_data['names'] = list()
        parameters_data['timestamps'] = list()
        parameters_data['values'] = list()

        tariff_dict = utilities.get_energy_category_tariffs(meter['cost_center_id'],
                                                            meter['energy_category_id'],
                                                            reporting_start_datetime_utc,
                                                            reporting_end_datetime_utc)
        print(tariff_dict)
        tariff_timestamp_list = list()
        tariff_value_list = list()
        for k, v in tariff_dict.items():
            # convert k from utc to local
            k = k + timedelta(minutes=timezone_offset)
            tariff_timestamp_list.append(k.isoformat()[0:19])
            tariff_value_list.append(v)

        parameters_data['names'].append('TARIFF-' + meter['energy_category_name'])
        parameters_data['timestamps'].append(tariff_timestamp_list)
        parameters_data['values'].append(tariff_value_list)

        ################################################################################################################
        # Step 7: query associated points data
        ################################################################################################################
        for point in point_list:
            point_values = []
            point_timestamps = []
            if point['object_type'] == 'ANALOG_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_analog_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s "
                         " ORDER BY utc_date_time ")
                cursor_historical.execute(query, (point['id'],
                                                  reporting_start_datetime_utc,
                                                  reporting_end_datetime_utc))
                rows = cursor_historical.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        current_datetime_local = row[0].replace(tzinfo=timezone.utc) + \
                                                 timedelta(minutes=timezone_offset)
                        current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
                        point_timestamps.append(current_datetime)
                        point_values.append(row[1])

            elif point['object_type'] == 'ENERGY_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_energy_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s "
                         " ORDER BY utc_date_time ")
                cursor_historical.execute(query, (point['id'],
                                                  reporting_start_datetime_utc,
                                                  reporting_end_datetime_utc))
                rows = cursor_historical.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        current_datetime_local = row[0].replace(tzinfo=timezone.utc) + \
                                                 timedelta(minutes=timezone_offset)
                        current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
                        point_timestamps.append(current_datetime)
                        point_values.append(row[1])
            elif point['object_type'] == 'DIGITAL_VALUE':
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_digital_value "
                         " WHERE point_id = %s "
                         "       AND utc_date_time BETWEEN %s AND %s ")
                cursor_historical.execute(query, (point['id'],
                                                  reporting_start_datetime_utc,
                                                  reporting_end_datetime_utc))
                rows = cursor_historical.fetchall()

                if rows is not None and len(rows) > 0:
                    for row in rows:
                        current_datetime_local = row[0].replace(tzinfo=timezone.utc) + \
                                                 timedelta(minutes=timezone_offset)
                        current_datetime = current_datetime_local.strftime('%Y-%m-%dT%H:%M:%S')
                        point_timestamps.append(current_datetime)
                        point_values.append(row[1])

            parameters_data['names'].append(point['name'] + ' (' + point['units'] + ')')
            parameters_data['timestamps'].append(point_timestamps)
            parameters_data['values'].append(point_values)

        ################################################################################################################
        # Step 8: construct the report
        ################################################################################################################
        if cursor_system:
            cursor_system.close()
        if cnx_system:
            cnx_system.disconnect()

        if cursor_energy:
            cursor_energy.close()
        if cnx_energy:
            cnx_energy.disconnect()

        if cursor_historical:
            cursor_historical.close()
        if cnx_historical:
            cnx_historical.disconnect()
        result = {
            "meter": {
                "cost_center_id": meter['cost_center_id'],
                "energy_category_id": meter['energy_category_id'],
                "energy_category_name": meter['energy_category_name'],
                "unit_of_measure": meter['unit_of_measure'],
                "kgce": meter['kgce'],
                "kgco2e": meter['kgco2e'],
            },
            "base_period": {
                "total_in_category": base['total_in_category'],
                "total_in_kgce": base['total_in_kgce'],
                "total_in_kgco2e": base['total_in_kgco2e'],
                "timestamps": base['timestamps'],
                "values": base['values']
            },
            "reporting_period": {
                "increment_rate":
                    (reporting['total_in_category'] - base['total_in_category'])/base['total_in_category']
                    if base['total_in_category'] > 0 else None,
                "total_in_category": reporting['total_in_category'],
                "total_in_kgce": reporting['total_in_kgce'],
                "total_in_kgco2e": reporting['total_in_kgco2e'],
                "timestamps": reporting['timestamps'],
                "values": reporting['values'],
            },
            "parameters": {
                "names": parameters_data['names'],
                "timestamps": parameters_data['timestamps'],
                "values": parameters_data['values']
            },
        }
        # export result to Excel file and then encode the file to base64 string
        result['excel_bytes_base64'] = \
            excelexporters.meterenergy.export(result,
                                              meter['name'],
                                              reporting_period_start_datetime_local,
                                              reporting_period_end_datetime_local,
                                              period_type)

        resp.body = json.dumps(result)
