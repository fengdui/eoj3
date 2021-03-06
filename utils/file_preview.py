import zipfile
import os
import re
from django.shortcuts import reverse


def sort_data_from_zipfile(file_path):
    import operator
    from functools import cmp_to_key

    def compare(a, b):
        x, y = a[0], b[0]
        try:
            cx = list(map(lambda x: int(x) if x.isdigit() else x, re.split(r'(\d+)', x)))
            cy = list(map(lambda x: int(x) if x.isdigit() else x, re.split(r'(\d+)', y)))
            if operator.eq(cx, cy):
                raise ArithmeticError
            return -1 if operator.lt(cx, cy) else 1
        except Exception:
            if x == y:
                return 0
            return -1 if x < y else 1

    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError
        saved_file = zipfile.ZipFile(file_path)
        raw_namelist = list(filter(lambda x: os.path.split(x)[0] == '', saved_file.namelist()))
        # print(raw_namelist)
        result = []
        file_set = set(raw_namelist)
        patterns = {'.in$': ['.out', '.ans'], '.IN$': ['.OUT', '.ANS'],
                    'input': ['output', 'answer'], 'INPUT': ['OUTPUT', 'ANSWER']}

        for file in raw_namelist:
            for pattern_in, pattern_out in patterns.items():
                if re.search(pattern_in, file) is not None:
                    for pattern in pattern_out:
                        try_str = re.sub(pattern_in, pattern, file)
                        if try_str in file_set:
                            file_set.remove(try_str)
                            file_set.remove(file)
                            result.append((file, try_str))
                            break

        return sorted(result, key=cmp_to_key(compare))
    except Exception:
        return []


def get_file_list(file_path, prefix):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError
        result = []
        for file in os.listdir(file_path):
            result.append(dict(
                filename=file,
                size="%dKB" % (os.path.getsize(os.path.join(file_path, file)) // 1024),
                path=os.path.join('/upload/', prefix, file)
            ))
        return result
    except Exception as e:
        print(repr(e))
        return []
