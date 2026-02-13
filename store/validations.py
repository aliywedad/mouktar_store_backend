def validate_stores_debt_payload(data, partial=False):
    """
    partial=False  -> POST (required validations)
    partial=True   -> PATCH (validate only provided fields, but still safe types)

    Returns: (clean_data, errors)
    """
    errors = {}
    clean = {}

    # ---------- helpers ----------
    def is_missing(val):
        return val is None or val == ""

    def to_float(field):
        v = data.get(field)
        if is_missing(v):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            errors[field] = f"{field} يجب أن يكون رقم"
            return None

    def to_int(field):
        v = data.get(field)
        if is_missing(v):
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            errors[field] = f"{field} يجب أن يكون عدداً صحيحاً"
            return None

    # ---------- name ----------
    if "name" in data or not partial:
        name = (data.get("name") or "").strip()
        if not name:
            errors["name"] = "اسم العميل مطلوب."
        else:
            clean["name"] = name

    # ---------- tel ----------
    if "tel" in data or not partial:
        tel = data.get("tel")
        if is_missing(tel):
            errors["tel"] = "رقم الهاتف مطلوب."
        else:
            try:
                tel_int = int(tel)
                if len(str(tel_int)) < 8:
                    errors["tel"] = "رقم الهاتف يجب أن يكون 8 أرقام على الأقل."
                else:
                    clean["tel"] = tel_int
            except (ValueError, TypeError):
                errors["tel"] = "رقم الهاتف يجب أن يكون عدداً صحيحاً"

    # ---------- OnUs (must exist + boolean) ----------
    if "OnUs" in data or not partial:
        if "OnUs" not in data:
            errors["OnUs"] = "يجب تحديد نوع الدين"
        else:
            onus = data.get("OnUs")
            if type(onus) is not bool:
                errors["OnUs"] = "يجب تحديد نوع الدين (true/false)"
            else:
                clean["OnUs"] = onus

    # ---------- data (must be array and at least 1 item) ----------
    # if "data" in data or not partial:
    #     if "data" not in data:
    #         errors["data"] = "يجب إضافة منتج واحد على الأقل."
    #     else:
    #         items = data.get("data")
    #         if not isinstance(items, list):
    #             errors["data"] = "data يجب أن تكون قائمة (Array)"
    #         elif len(items) == 0:
    #             errors["data"] = "يجب إضافة منتج واحد على الأقل."
    #         else:
    #             clean["data"] = items

    # ---------- total ----------
    if "total" in data or not partial:
        total = to_float("total")
        if total is None and (not partial):
            errors["total"] = "total مطلوب"
        elif total is not None:
            clean["total"] = total

    # ---------- payed_price (default 0) ----------
    if "payed_price" in data or not partial:
        if "payed_price" not in data and not partial:
            clean["payed_price"] = 0.0
        else:
            pp = data.get("payed_price", 0)
            try:
                clean["payed_price"] = float(pp if pp is not None else 0)
            except (ValueError, TypeError):
                errors["payed_price"] = "payed_price يجب أن يكون رقم"

    # ---------- timestamp ----------
    if "timestamp" in data:
        ts = to_float("timestamp")
        if ts is not None:
            clean["timestamp"] = ts

    # ---------- date ----------
    if "date" in data:
        dt = data.get("date")
        if dt is not None and not isinstance(dt, str):
            errors["date"] = "date يجب أن يكون نص"
        else:
            clean["date"] = dt

    # ---------- image_url ----------
    if "image_url" in data:
        url = data.get("image_url")
        if url is not None and not isinstance(url, str):
            errors["image_url"] = "image_url يجب أن يكون نص"
        else:
            clean["image_url"] = url

    # ---------- Final rule: payed_price <= total ----------
    # Only check if both are available (POST always, PATCH only if relevant)
    total_val = clean.get("total")
    pp_val = clean.get("payed_price")

    # If PATCH didn't include total but included payed_price, you may want to compare with DB value later
    # For POST, we can always check directly.
    if (total_val is not None) and (pp_val is not None):
        if pp_val > total_val:
            errors["payed_price"] = "تم دفع أكثر من المبلغ الكلي!"

    return clean, errors
