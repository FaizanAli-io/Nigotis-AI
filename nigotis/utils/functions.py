def extract_name(client):
    info = client.get("personalInfo", {})

    parts = [
        info["firstName"].strip(),
        info.get("title", "").strip(),
        info.get("lastName", "").strip(),
        info.get("middleName", "").strip(),
    ]

    return " ".join(part for part in parts if part)
