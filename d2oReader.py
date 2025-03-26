import struct

def read_int(file):
    data = file.read(4)
    if len(data) < 4:
        return None
    return struct.unpack('>i', data)[0]

def read_uint(file):
    data = file.read(4)
    if len(data) < 4:
        return None
    return struct.unpack('>I', data)[0]

def read_utf(file):
    length = read_int(file)
    return file.read(length).decode('utf-8', 'ignore')

def parse_d2o_file(file_path):
    with open(file_path, 'rb') as file:
        # Vérifier le header
        header = file.read(3)
        if header != b'D2O':
            raise ValueError("Invalid file format")

        index_table_start = read_int(file)
        file.seek(index_table_start)

        index_table_size = read_int(file)
        index_table = {}
        for _ in range(index_table_size // 8):
            key = read_int(file)
            position = read_int(file)
            index_table[key] = position

        class_count = read_int(file)
        print("Class count : ", class_count)
        classes = {}
        for _ in range(class_count):
            class_id = read_int(file)
            class_name = read_utf(file)
            package_name = read_utf(file)
            fields_count = read_int(file)

            fields = []
            for _ in range(fields_count):
                field_name = read_utf(file)
                field_type = read_int(file)
                fields.append((field_name, field_type))

            classes[class_id] = {
                'class_name': class_name,
                'package_name': package_name,
                'fields': fields
            }
        
        return classes

data = parse_d2o_file('D:/Ankama/Dofus/data/common/MapPositions.d2o')
print(data)