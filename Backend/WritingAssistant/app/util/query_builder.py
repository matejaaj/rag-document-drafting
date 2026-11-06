from sqlalchemy.sql.expression import and_


def dict_to_sqlalchemy_filter_options(model_class, filter_values: dict):
    conditions = []
    for key, value in filter_values.items():
        column = getattr(model_class, key, None)
        if column is None:
            continue
        if type(value) in [int, float]:
            conditions.append(column == value)
        elif type(value) in [str]:
            conditions.append(column.like("%" + value + "%"))
        elif type(value) in [bool]:
            conditions.append(column.is_(value))
    return and_(True, *conditions)
