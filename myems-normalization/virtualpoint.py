import time
from datetime import datetime, timedelta
import mysql.connector
from sympy import sympify, Piecewise, symbols
from decimal import Decimal
from multiprocessing import Pool
import random
import json
import config
import re


########################################################################################################################
# PROCEDURES:
# Step 1: Query all virtual points
# Step 2: Create multiprocessing pool to call worker in parallel
########################################################################################################################

def calculate(logger):

    while True:
        # the outermost while loop to reconnect server if there is a connection error
        cnx_system_db = None
        cursor_system_db = None
        try:
            cnx_system_db = mysql.connector.connect(**config.myems_system_db)
            cursor_system_db = cnx_system_db.cursor()
        except Exception as e:
            logger.error("Error in step 0 of virtual point calculate " + str(e))
            if cursor_system_db:
                cursor_system_db.close()
            if cnx_system_db:
                cnx_system_db.close()
            # sleep and continue the outer loop to reconnect the database
            time.sleep(60)
            continue

        print("Connected to MyEMS System Database")

        virtual_point_list = list()
        try:
            cursor_system_db.execute(" SELECT id, name, data_source_id, high_limit, low_limit, address "
                                     " FROM tbl_points "
                                     " WHERE is_virtual = 1 AND object_type = 'ANALOG_VALUE' ")
            rows_virtual_points = cursor_system_db.fetchall()

            if rows_virtual_points is None or len(rows_virtual_points) == 0:
                # sleep several minutes and continue the outer loop to reconnect the database
                time.sleep(60)
                continue

            for row in rows_virtual_points:
                meta_result = {"id": row[0],
                               "name": row[1],
                               "data_source_id": row[2],
                               "high_limit": row[3],
                               "low_limit": row[4],
                               "address": row[5]}
                virtual_point_list.append(meta_result)

        except Exception as e:
            logger.error("Error in step 1 of virtual point calculate " + str(e))
            # sleep and continue the outer loop to reconnect the database
            time.sleep(60)
            continue
        finally:
            if cursor_system_db:
                cursor_system_db.close()
            if cnx_system_db:
                cnx_system_db.close()

        # shuffle the virtual point list for randomly calculating
        random.shuffle(virtual_point_list)

        print("Got all virtual points in MyEMS System Database")
        ################################################################################################################
        # Step 2: Create multiprocessing pool to call worker in parallel
        ################################################################################################################
        p = Pool(processes=config.pool_size)
        error_list = p.map(worker, virtual_point_list)
        p.close()
        p.join()

        for error in error_list:
            if error is not None and len(error) > 0:
                logger.error(error)

        print("go to sleep ")
        time.sleep(60)
        print("wake from sleep, and continue to work")


########################################################################################################################
# Step 1: get start datetime and end datetime
# Step 2: parse the expression and get all points in substitutions
# Step 3: query points value from historical database
# Step 4: evaluate the equation with points values
########################################################################################################################

def worker(virtual_point):
    cnx_historical_db = None
    cursor_historical_db = None

    try:
        cnx_historical_db = mysql.connector.connect(**config.myems_historical_db)
        cursor_historical_db = cnx_historical_db.cursor()
    except Exception as e:
        if cursor_historical_db:
            cursor_historical_db.close()
        if cnx_historical_db:
            cnx_historical_db.close()
        return "Error in step 1.1 of virtual point worker " + str(e) + " for '" + virtual_point['name'] + "'"

    print("Start to process virtual point: " + "'" + virtual_point['name']+"'")

    ####################################################################################################################
    # step 1: get start datetime and end datetime
    ####################################################################################################################

    try:
        query = (" SELECT MAX(utc_date_time) "
                 " FROM tbl_analog_value "
                 " WHERE point_id = %s ")
        cursor_historical_db.execute(query, (virtual_point['id'],))
        row = cursor_historical_db.fetchone()
    except Exception as e:
        if cursor_historical_db:
            cursor_historical_db.close()
        if cnx_historical_db:
            cnx_historical_db.close()
        return "Error in step 1.2 of virtual point worker " + str(e) + " for '" + virtual_point['name'] + "'"

    start_datetime_utc = datetime.strptime(config.start_datetime_utc, '%Y-%m-%d %H:%M:%S')
    start_datetime_utc = start_datetime_utc.replace(minute=0, second=0, microsecond=0, tzinfo=None)

    if row is not None and len(row) > 0 and isinstance(row[0], datetime):
        # replace second and microsecond with 0
        # note: do not replace minute in case of calculating in half hourly
        start_datetime_utc = row[0].replace(second=0, microsecond=0, tzinfo=None)
        # start from the next time slot
        start_datetime_utc += timedelta(minutes=config.minutes_to_count)

    end_datetime_utc = datetime.utcnow().replace()
    end_datetime_utc = end_datetime_utc.replace(second=0, microsecond=0, tzinfo=None)

    if end_datetime_utc <= start_datetime_utc:
        if cursor_historical_db:
            cursor_historical_db.close()
        if cnx_historical_db:
            cnx_historical_db.close()
        return "it's too early to calculate" + " for '" + virtual_point['name'] + "'"

    print("start_datetime_utc: " + start_datetime_utc.isoformat()[0:19]
          + "end_datetime_utc: " + end_datetime_utc.isoformat()[0:19])

    ############################################################################################################
    # Step 2: parse the expression and get all points in substitutions
    ############################################################################################################
    point_list = list()
    try:
        ########################################################################################################
        # parse the expression and get all points in substitutions
        ########################################################################################################
        address = json.loads(virtual_point['address'])
        # algebraic expression example: '{"expression": "x1-x2", "substitutions": {"x1":1,"x2":2}}'
        # piecewise function example: '{"expression":"(1,x<200 ), (2,x>=500), (0,True)", "substitutions":{"x":101}}'
        if 'expression' not in address.keys() \
                or 'substitutions' not in address.keys() \
                or len(address['expression']) == 0 \
                or len(address['substitutions']) == 0:
            return "Error in step 2.1 of virtual point worker for '" + virtual_point['name'] + "'"
        expression = address['expression']
        substitutions = address['substitutions']
        for variable_name, point_id in substitutions.items():
            point_list.append({"variable_name": variable_name, "point_id": point_id})
    except Exception as e:
        if cursor_historical_db:
            cursor_historical_db.close()
        if cnx_historical_db:
            cnx_historical_db.close()
        return "Error in step 2.2 of virtual point worker " + str(e) + " for '" + virtual_point['name'] + "'"

    ############################################################################################################
    # Step 3: query points value from historical database
    ############################################################################################################

    print("getting point values ")
    point_values_dict = dict()
    if point_list is not None and len(point_list) > 0:
        try:
            for point in point_list:
                point_id = str(point['point_id'])
                query = (" SELECT utc_date_time, actual_value "
                         " FROM tbl_analog_value "
                         " WHERE point_id = %s AND utc_date_time >= %s AND utc_date_time < %s "
                         " ORDER BY utc_date_time ")
                cursor_historical_db.execute(query, (point_id, start_datetime_utc, end_datetime_utc, ))
                rows = cursor_historical_db.fetchall()
                if rows is None or len(rows) == 0:
                    point_values_dict[point_id] = None
                else:
                    point_values_dict[point_id] = dict()
                    for row in rows:
                        point_values_dict[point_id][row[0]] = row[1]
        except Exception as e:
            if cursor_historical_db:
                cursor_historical_db.close()
            if cnx_historical_db:
                cnx_historical_db.close()
            return "Error in step 3.1 virtual point worker " + str(e) + " for '" + virtual_point['name'] + "'"

    ############################################################################################################
    # Step 4: evaluate the equation with points values
    ############################################################################################################

    print("getting date time set for all points")
    utc_date_time_set = set()
    if point_values_dict is not None and len(point_values_dict) > 0:
        for point_id, point_values in point_values_dict.items():
            if point_values is not None and len(point_values) > 0:
                utc_date_time_set = utc_date_time_set.union(point_values.keys())

    print("evaluating the equation with SymPy")
    normalized_values = list()

    ############################################################################################################
    # Converting Strings to SymPy Expressions
    # The sympify function(that’s sympify, not to be confused with simplify) can be used to
    # convert strings into SymPy expressions.
    ############################################################################################################
    try:
        if re.search(',', expression):
            for item in substitutions.keys():
                locals()[item] = symbols(item)
            expr = eval(expression)
            print("the expression will be evaluated as piecewise function: " + str(expr))
        else:
            expr = sympify(expression)
            print("the expression will be evaluated as algebraic expression: " + str(expr))

        for utc_date_time in utc_date_time_set:
            meta_data = dict()
            meta_data['utc_date_time'] = utc_date_time

            ####################################################################################################
            # create a dictionary of Symbol: point pairs
            ####################################################################################################

            subs = dict()

            ####################################################################################################
            # Evaluating the expression at current_datetime_utc
            ####################################################################################################

            if point_list is not None and len(point_list) > 0:
                for point in point_list:
                    point_id = str(point['point_id'])
                    actual_value = point_values_dict[point_id].get(utc_date_time, None)
                    if actual_value is None:
                        break
                    subs[point['variable_name']] = actual_value

            if len(subs) != len(point_list):
                continue

            ####################################################################################################
            # To numerically evaluate an expression with a Symbol at a point,
            # we might use subs followed by evalf,
            # but it is more efficient and numerically stable to pass the substitution to evalf
            # using the subs flag, which takes a dictionary of Symbol: point pairs.
            ####################################################################################################
            if re.search(',', expression):
                formula = Piecewise(*expr)
                meta_data['actual_value'] = Decimal(str(formula.subs(subs)))
                normalized_values.append(meta_data)
            else:
                meta_data['actual_value'] = Decimal(str(expr.evalf(subs=subs)))
                normalized_values.append(meta_data)
    except Exception as e:
        if cursor_historical_db:
            cursor_historical_db.close()
        if cnx_historical_db:
            cnx_historical_db.close()
        return "Error in step 4.1 virtual point worker " + str(e) + " for '" + virtual_point['name'] + "'"

    print("saving virtual points values to historical database")

    if len(normalized_values) > 0:
        try:
            add_values = (" INSERT INTO tbl_analog_value "
                          " (point_id, utc_date_time, actual_value) "
                          " VALUES  ")

            for meta_data in normalized_values:
                add_values += " (" + str(virtual_point['id']) + ","
                add_values += "'" + meta_data['utc_date_time'].isoformat()[0:19] + "',"
                add_values += str(meta_data['actual_value']) + "), "
            print("add_values:" + add_values)
            # trim ", " at the end of string and then execute
            cursor_historical_db.execute(add_values[:-2])
            cnx_historical_db.commit()
        except Exception as e:
            if cursor_historical_db:
                cursor_historical_db.close()
            if cnx_historical_db:
                cnx_historical_db.close()
            return "Error in step 4.2 virtual point worker " + str(e) + " for '" + virtual_point['name'] + "'"

    if cursor_historical_db:
        cursor_historical_db.close()
    if cnx_historical_db:
        cnx_historical_db.close()

    return None
