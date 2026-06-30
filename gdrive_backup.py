"""
Google Sheets backup for scoreboard data.
- backup_to_sheet(data): saves entire data as JSON string to Sheet cell A1
- restore_from_sheet(): reads JSON from Sheet cell A1, returns data dict or None
"""
import json

SHEET_ID = "1BE3xEtrT6uGaIcAzRGff4AUpJjc025Dq8tDsOhVbA2U"

SERVICE_ACCOUNT_INFO = {
    "type": "service_account",
    "project_id": "gen-lang-client-0946609439",
    "private_key_id": "7cf335ddd858585c742bf4ad609a2afbe1ad99e2", "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQChUUY9lDert3tc\nRGFyKjp4FecRIHwDftnKY9XzBCkXdpdYo0o17NEZQpVZ/3BCaeq3FlQE/G42nnBz\nB7zMQiJwdOjcbWuHjS2LFeRiu+QMF5kqv2hyOOJlXhBnMJgYhlJM2IHFRt9xCGTo\n62KxyvTha1yh720aiXqgYdUJY18c60He7uxU3I+Rw4v3rhmoYwg3eIxxeBEGTtWM\niD/UhST4WKRcfb7hIa/4VnmbF+UqkLOTDj3MJFpJt+hQU67pxIzljboeI0LcTvVd\nZkUK3BO0/H+29NXNwsE7itiuJarQmnOXWnAF61iFOhebTM3oVz9WXtsA8HHDDc6v\nZq/ZHGlnAgMBAAECggEAED5Fy1eMT38XLdA4260C3CqgbKoPsq5oMafh2Cl4FcO8\nM5GlnE5vM5LvxPMik51ko/Dcnu/oDRnhCsQhr5ONMjOjauadqDV/+3xF1edDbDBI\nHPTPCIlPypMxJaLP/dAwo0o9ruaXAyOsPYPOGUbtZ3FPD4MzQjPLpDCVqe9WmWux\n9iCCp71RzYdxJnXyvXif1EMMWh0BpLkfmPRTWqGUMV5xVhKhg+/6qQscWOTsXuAA\nx9XighdRQu65toygPBHC671t8nW439Lf4B3ZujJn2sNjiPsvTlcisIiNRaeAlvli\nKMEI/En07DB5rD4oTau2+zemOlN/LNeD8KBo2aBViQKBgQDM4XfbygFtXAJaXh5F\nulrRococw5X6bzsXWt6Mx66IBhOJsd0ohY+sxSvY4IOfJPQex8IQEx3DPXdBEgvW\nhZu7HC7uh1adYBMS3yf9QI+vQUZqdhdJVQT2xoI1OKM6HZCJ5p5dVT53Juo3VFFA\nuaqWRacr/08Rhgzd+jGGXoCYfQKBgQDJkUBB6ss+9kdQ8vBWw89yQP/XLLmO5mtd\nmDKhIQ1ve2uFfAmKWS9MSVOeISOvC2Cek5BdXMfsp+6yIjg4Qy9WU06rUSN+IJLz\nGOLFoqViHild0nghdUWHbzSPgtMVPnbrCvYeWr/XoCEseqmZD1QRp+k+qR0bywA2\nLpRrxq0SswKBgDEVj1abxc3CblniFJSV+e4hOb+8Z/EQtvJ4dbr6l+jEs+eYMijk\nHrDAqCmUWFRHUSkSqH6bZdUBo9F2Fln1toKUVPYWfHzFqKwrxHPbBNFy7QDSe++4\nq7DHjCheAlUJAjjXhHdN1eJL828AB1tfX+wSkeNrjjDfkbOYnkbX2y0tAoGALmui\nJcwh9KUZNX5NdV3xB3oKsY5eSZetQEfN2SfYhUUiNQKk29TAPMxiUneFVUnEfaC0\nTZwReuIN6b5RvjtSyomzA2dTSjfMP+oKR8O2XMtfcXkIK4Rrd85Xh3l0jV7uWiET\nH1h89/arzSeOqW5LSSmnYMPnrT/qE5BUpCGEOFsCgYA0E8WZecaNd3LGKJQ9RhMh\nprb1ocjPb9gbIhxanhJy2A3Gdca3QorZ6dS2VJIQ6HfziCFujlG4CubO8JbFYDiO\nql7w1+SRjelfs9IbmVnjCTRFQrilrz1zldof+BF+vAFNwHmDZPDTjgaDL2wO5H/R\n5MjCk5f2dPJI2MnTElmMKw==\n-----END PRIVATE KEY-----\n",
    "client_email": "scoreboard-backup@gen-lang-client-0946609439.iam.gserviceaccount.com",
    "client_id": "115036046801314143386",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/scoreboard-backup%40gen-lang-client-0946609439.iam.gserviceaccount.com",
}


def _get_credentials():
    from google.oauth2.service_account import Credentials
    return Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=["https://www.googleapis.com/auth/spreadsheets"])


def backup_to_sheet(data: dict):
    """Write entire scoreboard data as JSON string to Sheet cell A1."""
    try:
        from googleapiclient.discovery import build
        creds = _get_credentials()
        service = build("sheets", "v4", credentials=creds)
        json_str = json.dumps(data, ensure_ascii=False)
        service.spreadsheets().values().update(
            spreadsheetId=SHEET_ID,
            range="Sheet1!A1",
            valueInputOption="RAW",
            body={"values": [[json_str]]},
        ).execute()
        return True
    except Exception as e:
        print(f"[backup] Failed: {e}")
        return False


def restore_from_sheet():
    """Read JSON string from Sheet cell A1, parse and return data dict. Returns None on failure."""
    try:
        from googleapiclient.discovery import build
        creds = _get_credentials()
        service = build("sheets", "v4", credentials=creds)
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range="Sheet1!A1",
        ).execute()
        values = result.get("values", [])
        if values and values[0]:
            return json.loads(values[0][0])
    except Exception as e:
        print(f"[backup] Restore failed: {e}")
    return None
