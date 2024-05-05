# CSV Export related
# ----------------------------------------------

from ast import literal_eval
from func.attribute_func import get_attribute_default_value, get_attribute_values, set_attribute_values
from func.enum_func import get_attribute_data_types, get_attribute_domains
from modules import LEGACY_etc, LEGACY_static_data


import csv


def write_csv_attributes_file(filepath:str, obj, attributes: list, add_domain_and_data_type_to_title_row = True):
    """Writes specified attrtibutes to .csv file specified in filepath

    Args:
        filepath (str): path to the file
        obj (_type_): object to take attributes from
        attributes (list): list of attribute references to take data from

    Exceptions:
        PermissionError
    """

    # add csv extension
    if not filepath.lower().endswith('.csv'):
        filepath += ".csv"

    LEGACY_etc.log(write_csv_attributes_file, f"Exporting to CSV file located at \"{filepath}\"", LEGACY_etc.ELogLevel.VERBOSE)

    with open(filepath, 'w', newline='') as csvfile:

        rownames = []
        datalengths = []
        values = []

        for attribute in attributes:
            if add_domain_and_data_type_to_title_row:
                rownames.append(str(attribute.name + "(" + attribute.data_type + ")(" + attribute.domain+")"))
            else:
                rownames.append(attribute.name)
            datalengths.append(len(attribute.data))
            values.append(get_attribute_values(attribute, obj))

        max_data_len = max(datalengths)

        writer = csv.DictWriter(csvfile, fieldnames=rownames)
        writer.writeheader()

        for i in range(0, max_data_len):

            row = {}
            for j, attribute in enumerate(attributes):
                rownames[j].replace(',', "")
                if i < datalengths[j]:
                    row[rownames[j]] = values[j][i]
                else:
                    row[rownames[j]] = ""

            writer.writerow(row)

    LEGACY_etc.log(write_csv_attributes_file, f"Wrote {max_data_len+1} lines.", LEGACY_etc.ELogLevel.VERBOSE)


def csv_to_attributes(filepath:str, obj, excluded_attribute_names: list, remove_domain_from_name: bool = True, remove_datatype_from_name: bool = True,
                      force_domain: str = '', force_data_type: str = ''):
    """Converts CSV file to active mesh attributes

    Args:
        filepath (str): The path to the CSV file
        obj (ref): Reference to the object to store the attributes in
        excluded_attribute_names (list): List of attriubte names that should be ignored while importing+
        remove_domain_from_name (bool, optional): Whether to remove the strings like (POINT) from attribute name if title row contains it. Defaults to True.
        remove_datatype_from_name (bool, optional): Whether to remove the strings like (FLOAT) from attribute name if title row constains it. Defaults to True.
        force_domain (str, optional): Name of the domain to override all imported attributes to be stored in. Use same naming convetion as blender, eg. POINT. Defaults to ''.
        force_data_type (str, optional): Name of the data type to override all imported attributes to be. Use same naming convetion as blender, eg. FLOAT_VECTOR. Defaults to ''.

    Returns:
        Status (bool): True on success
        Errors list (list): List of str elements that contain error descriptions
        New attribute count (int): the count of attributes imported or created.
    """

    LEGACY_etc.log(csv_to_attributes, f"Creating and writing attributes from CSV file located at \"{filepath}\"", LEGACY_etc.ELogLevel.VERBOSE)

    errors = []

    with open(filepath, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        attribute_sets = []
        valid_columns = []
        data_columns = []

        line = 0
        for row in reader:
            line += 1
            if line == 1:
                # read attributes
                for col_id, column in enumerate(row):
                    if not column.endswith(')') and (force_domain != '' or force_data_type != ''):
                        errors.append(f"Column {col_id} title invalid: {column}")
                        continue

                    # find domain
                    attrib_domain = None
                    domains = get_attribute_domains()

                    if force_domain == '' or remove_domain_from_name:
                        # check for longest first
                        domains.sort(key=len, reverse=True)

                        for dom in domains:
                            foundat = column.rfind("(" + dom.upper() + ")")
                            if foundat != -1:
                                attrib_domain = dom
                                if remove_domain_from_name:
                                    column = column[:foundat] + column[foundat+len(dom)+2:]
                                break

                    if force_domain != '':
                        attrib_domain = force_domain


                    if attrib_domain is None or attrib_domain not in domains:
                        errors.append(f"Can't determine domain or domain unsupported in this blender version for column {col_id}: {column}")
                        continue

                    # find data type
                    attrib_dt = None
                    data_types = LEGACY_static_data.attribute_data_types #get_attribute_data_types()

                    if force_data_type == '' or remove_datatype_from_name:

                        for dt in data_types:
                            foundat = column.rfind("(" + dt.upper() + ")")
                            if foundat != -1:
                                attrib_dt = dt
                                if remove_datatype_from_name:
                                    column = column[:foundat] + column[foundat+len(dt)+2:]
                                break

                    if force_data_type != '':
                        attrib_dt = force_data_type

                    if attrib_dt is None or attrib_dt not in data_types:
                        errors.append(f"Can't determine data type in column {col_id}: {column}")
                        continue

                    if attrib_dt not in get_attribute_data_types():
                        errors.append(f"Data type \"{attrib_dt}\" unsupported in this blender version in column {col_id}: {column}")
                        continue


                    # remove
                    column = column.replace('(', "")
                    column = column.replace(')', "")

                    if column in obj.data.attributes:
                        attribute = obj.data.attributes[column]
                        if attribute.data_type != attrib_dt:
                            errors.append(f"This attribute exists, but the data type is different: column {col_id}: {column}")
                            continue
                        elif attribute.domain != attrib_domain:
                            errors.append(f"This attribute exists, but the domain is different: column {col_id}: {column}")
                            continue
                    else:
                        if column == "":
                            errors.append(f"Cannot create an attribute with empty name, column {col_id}")
                            continue

                        attribute = obj.data.attributes.new(name=column, type=attrib_dt, domain=attrib_domain)

                    if attribute in excluded_attribute_names:
                        LEGACY_etc.log(csv_to_attributes, f"Attribute on exclude list: {col_id} {column}", LEGACY_etc.ELogLevel.VERBOSE)
                        continue

                    # Because this script can create many attributes quickly, blender might not update the data about
                    # domains and data types fast enough to be accessible via .data_type and .domain
                    # so this has to be passed through manually

                    aset = {
                        "attribute": attribute,
                        "name": column,
                        "data_type": attrib_dt,
                        "domain": attrib_domain
                    }
                    attribute_sets.append(aset)
                    valid_columns.append(col_id)
                    data_columns.append([])

                    LEGACY_etc.log(csv_to_attributes, f'Identified column {col_id} as {column}, domain {attrib_domain}, data type {attrib_dt}', LEGACY_etc.ELogLevel.VERBOSE)

                obj.data.update()

            else:
                if not len(valid_columns):
                    errors.append('No valid fields detected')
                    return False, errors, 0

                for i, col_id in enumerate(valid_columns):
                    attribute_set = attribute_sets[i]

                    LEGACY_etc.log(csv_to_attributes, f"[COL {col_id}][ROW: {line-1}] Reading data for attribute {attribute_set['name']}, domain {attribute_set['domain']}, data type {attribute_set['data_type']}", LEGACY_etc.ELogLevel.VERBOSE)

                    cast_type = LEGACY_static_data.attribute_data_types[attribute_set['data_type']].cast_type

                    data = row[col_id]
                    if data == "" and cast_type is not string:
                        continue

                    try:
                        if cast_type is not tuple:
                            data_columns[i].append(cast_type(data))
                        else:
                            if type(literal_eval(data)) != cast_type:
                                raise ValueError
                            data_columns[i].append(literal_eval(data))
                    except ValueError:
                        errors.append(f"Cannot convert {data} from column {col_id}, row {line-1} to {cast_type}, using default value for this data type.")
                        data_columns[i].append(get_attribute_default_value(attribute))



        for i, attribute_set in enumerate(attribute_sets):
            attribute = attribute_set['attribute']
            input_data_len = len(data_columns[i])
            storage_len = len(attribute.data)
            if input_data_len < storage_len:
                data_columns[i] += [get_attribute_default_value(attribute)] * (storage_len-input_data_len)
            elif input_data_len > storage_len:
                data_columns[i] = data_columns[i][:storage_len]

            set_attribute_values(attribute, data_columns[i], bugbypass_data_type=attribute_set['data_type'], bugbypass_domain=attribute_set['domain'])




    return True, errors, len(attribute_sets)