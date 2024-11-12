import os
import json
import requests
import re
from get_token import  base_url, get_auth
from dotenv import load_dotenv

def check_login(login):
    turkish_chars = "çÇğĞüÜöÖşŞıİ"
    
    if any(char in turkish_chars for char in login):
        return False
    
    if not re.match(r'^[a-zA-Z0-9._]+$', login):
        return False
    
    if login.startswith(('_', '.')) or login.endswith(('_', '.')):
        return False
    
    return True

def create_customers():
    try:
        auth = get_auth()
        data = []
        load_dotenv()
        infra_id = os.getenv('INFRA_ID')

        with open("customer.json", "r") as file:
            data = json.load(file)

        for customer in data:
            name = customer["name"].strip()
            login = customer["login"].strip()
            password = customer["password"].strip()
            parent_id = customer["parent_id"].strip()
            email = customer["email"].strip()
            
            login_valid = check_login(login)
            
            if login_valid == False:
                print(name, f"- '{login}' kullanıcı adı geçerli formatta değil!")
                continue
            
            login_check_res = requests.get(
                f"{base_url}/users/check_login?username={login}",
                headers=auth
            )

            if login_check_res.status_code == 409:
                print(name, f"- '{login}' kullanıcı adı daha önceden kullanılmış!")
                continue

            customer_res = requests.post(
                f'{base_url}/tenants',
                data=json.dumps({
                    "kind": "customer",
                    "language": "tr",
                    "name": name,
                    "parent_id": parent_id,
                    "contact": {
                        "email": email
                    }
                }),
                headers=auth
            )
            
            if customer_res.status_code == 409:
                print(name, "- Müşteri adı daha önceden kullanılmış!")
                continue
            
            if customer_res.ok == False:
                print(name, "- Müşteri oluşturulurken hata oluştu!")
                continue
            
            new_customer = customer_res.json()
            
            requests.post(
                f"{base_url}/applications/6e6d758d-8e74-3ae3-ac84-50eb0dff12eb/bindings/tenants/{new_customer["id"]}",
                headers=auth
            )
            
            requests.post(
                f"{base_url}/applications/7459244f-68f3-3bf4-9f53-5f63ecc1d91f/bindings/tenants/{new_customer["id"]}",
                headers=auth
            )
            
            user_res = requests.post(
                f"{base_url}/users",
                data=json.dumps({
                    "tenant_id": new_customer["id"],
                    "login": login,
                    "contact": {
                        "email": email,
                        "types": [
                            "billing",
                            "management",
                            "technical"
                        ]
                    } 
                }),
                headers=auth
            )
            
            if user_res.ok == False:
                print(name, "- Kullanıcı oluşturulurken hata oluştu!")
                continue
                
            new_user = user_res.json()
            
            password_res = requests.post(
                f"{base_url}/users/{new_user["id"]}/password",
                data=json.dumps({
                    "password": password    
                }),
                headers=auth
            )
            
            if password_res.ok == False:
                print(name, "- Şifre oluşturulurken hata oluştu!")
            
            role_res = requests.put(
                f"{base_url}/users/{new_user["id"]}/access_policies",
                data=json.dumps({
                    "items": [
                        {
                            "id": "00000000-0000-0000-0000-000000000000",
                            "issuer_id": "00000000-0000-0000-0000-000000000000",
                            "role_id": "company_admin",
                            "tenant_id": new_customer["id"],
                            "trustee_id": new_user["id"],
                            "trustee_type": "user",
                            "version": 0
                        }
                    ]
                }),
                headers=auth
            )
            
            if role_res.ok == False:
                print(name, "- Rol eklenirken hata oluştu!")
            
            offering_items_res = requests.put(
                f"{base_url}/tenants/{new_customer["id"]}/offering_items",
                data=json.dumps({
                    "offering_items": [
                            {
                                "name": "local_storage",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": None,
                                "usage_name": "local_storage",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "bytes"
                            },
                            {
                                "name": "pg_base_storage",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "storage",
                                "status": 1,
                                "locked": False,
                                "type": "infra",
                                "infra_id": infra_id,
                                "measurement_unit": "bytes"
                            },
                            {
                                "name": "pg_base_workstations",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "workstations",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_servers",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "servers",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_vms",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "vms",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_mobiles",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "mobiles",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_m365_seats",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "mailboxes",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_websites",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "websites",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_gworkspace_seats",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "gsuite_seats",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_web_hosting_servers",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "web_hosting_servers",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_m365_mailboxes",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "o365_mailboxes",
                                "status": 1,
                                "locked": False,
                                "type": "feature",
                                "infra_id": None,
                                "measurement_unit": "n/a"
                            },
                            {
                                "name": "pg_base_m365_onedrive",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "o365_onedrive",
                                "status": 1,
                                "locked": False,
                                "type": "feature",
                                "infra_id": None,
                                "measurement_unit": "n/a"
                            },
                            {
                                "name": "pg_base_m365_sharepoint_sites",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "o365_sharepoint_sites",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_google_mail",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "google_mail",
                                "status": 1,
                                "locked": False,
                                "type": "feature",
                                "infra_id": None,
                                "measurement_unit": "n/a"
                            },
                            {
                                "name": "pg_base_google_drive",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "google_drive",
                                "status": 1,
                                "locked": False,
                                "type": "feature",
                                "infra_id": None,
                                "measurement_unit": "n/a"
                            },
                            {
                                "name": "pg_base_google_team_drive",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "google_team_drive",
                                "status": 1,
                                "locked": False,
                                "type": "feature",
                                "infra_id": None,
                                "measurement_unit": "n/a"
                            },
                            {
                                "name": "pg_base_m365_teams",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "o365_teams",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_hosted_exchange",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "hosted_exchange",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            },
                            {
                                "name": "pg_base_nas",
                                "application_id": "6e6d758d-8e74-3ae3-ac84-50eb0dff12eb",
                                "edition": "pck_per_gigabyte",
                                "usage_name": "nas",
                                "status": 1,
                                "locked": False,
                                "type": "count",
                                "infra_id": None,
                                "measurement_unit": "quantity"
                            }
                        ]
                }),
                headers=auth
            )

            if offering_items_res.ok == True:
                print(name)
            else:
                print(name, "- Standart koruma eklenirken hata oluştu!")

        print("------------------------")
        print("Tüm işlemler tamamlandı!")

    except Exception as error: 
        print(error)

def run_app():
    try:
        create_customers()
    except (Exception) as error:
        print(error)    

if __name__ == "__main__":
    run_app()