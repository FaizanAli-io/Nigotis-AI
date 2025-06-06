import requests


def extract_name(client):
    info = client.get("personalInfo", {})

    parts = [
        info["firstName"].strip(),
        info.get("title", "").strip(),
        info.get("lastName", "").strip(),
        info.get("middleName", "").strip(),
    ]

    return " ".join(part for part in parts if part)


def call_login_api(email, password, account_type):
    return requests.post(
        "https://nigotis-be.vercel.app/api/v1/user/login",
        json={
            "email": email,
            "password": password,
            "loginAs": account_type,
        },
    ).json()
