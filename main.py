import json
import requests
import re
from get_token import  base_url, get_auth

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

            if role_res.ok == True:
                print(name)
            else:
                print(name, "- Rol eklenirken hata oluştu!")

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