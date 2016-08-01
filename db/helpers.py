def select(fields, from_table):
    return 'select %s from public."%s" ' % (','.join(fields), from_table)


def insert(fields, to_table):
    return 'insert into public."%s"(%s) ' % (to_table, ','.join(fields))


def form_fields(fields):
    return fields if fields else '*'
