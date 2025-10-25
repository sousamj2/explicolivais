from datetime import datetime

def dictify_real_dict_row(row):
    def convert_value(val):
        if isinstance(val, datetime):
            return val.isoformat()
        if isinstance(val, list):
            return [convert_value(i) for i in val]
        if isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        return val

    return {k: convert_value(v) for k, v in row.items()}

def convert_datetimes(obj):
    if isinstance(obj, dict):
        return {k: convert_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes(elem) for elem in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


# if __name__ == "__main__":
#     # Example usage
#     insert_user("John Doe", "john.doe2@example.com", "123 Main St", "12345", "556-1234", "123.57.89.0")



