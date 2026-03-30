
@api_view(["POST"])
@permission_classes([HasTokenPermission])
def addMultipleStoreChangesAPI(request):
    try:
        data = request.data
        name     = data.get("name", "")
        tel_raw  = data.get("tel", 0)
        type_    = data.get("type")
        date_ts  = data.get("date", int(datetime.now().timestamp() * 1000))
        items    = data.get("items", [])

        # ── Basic validation ──────────────────────────────────────────
        if type_ not in ["IN", "OUT"]:
            return Response({"error": "type must be IN or OUT"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not items:
            return Response({"error": "items list is required and cannot be empty"},
                            status=status.HTTP_400_BAD_REQUEST)

        # Parse tel
        try:
            tel = int(tel_raw) if tel_raw else 0
        except (ValueError, TypeError):
            tel = 0

        # Validate tel for OUT movements
        if type_ == "OUT":
            is_valid_tel, tel_result = validate_tel(tel)
            if not is_valid_tel:
                return Response({"error": tel_result},
                                status=status.HTTP_400_BAD_REQUEST)

        # ── Per-item validation & Store check ────────────────────────
        errors = []
        resolved_items = []  # will hold (Store_doc, change_qty, item)

        for idx, item in enumerate(items):
            Store_id  = item.get("id")
            change_qty_raw = item.get("quantity")   # the qty the user wants to move

            if not Store_id:
                errors.append({"index": idx, "error": "StoreId (id) is required"})
                continue

            try:
                change_qty = round(float(change_qty_raw), 2)
            except (TypeError, ValueError):
                errors.append({"index": idx, "error": "quantity must be a number"})
                continue

            if change_qty <= 0:
                errors.append({"index": idx, "error": "quantity must be > 0"})
                continue

            Store_doc = Store.find_one({"_id": ObjectId(Store_id)})
            if not Store_doc:
                errors.append({"index": idx, "error": f"Store item {Store_id} not found"})
                continue

            if type_ == "OUT":
                current_qty = float(Store_doc.get("Quantity", 0))
                if current_qty < change_qty:
                    errors.append({
                        "index": idx,
                        "name":  item.get("name"),
                        "error": "Insufficient Store",
                        "available": current_qty,
                        "requested": change_qty,
                    })
                    continue

            resolved_items.append((Store_doc, change_qty, item))

        if errors:
            return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

        # ── Apply changes ─────────────────────────────────────────────
        inserted_ids   = []
        updated_Stores = []
        now_ts = int(datetime.now().timestamp() * 1000)

        for Store_doc, change_qty, item in resolved_items:
            Store_id = str(Store_doc["_id"])

            change_doc = {
                "StoreId":   Store_id,
                "name":      name,
                "tel":       tel,
                "type":      type_,
                "Quantity":  change_qty,
                "product":   item.get("name"),
                "package":   item.get("package"),
                "timestamp": now_ts,
                "date":      date_ts,
            }

            ins = StoreChanges.insert_one(change_doc)
            inserted_ids.append(str(ins.inserted_id))

            increment = -change_qty if type_ == "OUT" else change_qty
            Store.update_one(
                {"_id": ObjectId(Store_id)},
                {"$inc": {"Quantity": increment},
                 "$set": {"timestamp": now_ts}},
            )

            updated = Store.find_one({"_id": ObjectId(Store_id)})
            updated_Stores.append(mongo_to_json(updated))

        return Response(
            {
                "message":       "Multiple Store changes created successfully",
                "count":         len(inserted_ids),
                "changeIds":     inserted_ids,
                "updatedStores": updated_Stores,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        print(e)
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


