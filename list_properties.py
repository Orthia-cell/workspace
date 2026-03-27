import requests
import json

CONFIG_PATH = "/root/.openclaw/workspace/arduino-iot-pipeline/config/arduino_iot_config.json"

def get_access_token(client_id, client_secret):
    url = "https://api2.arduino.cc/iot/v1/clients/token"
    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": "https://api2.arduino.cc/iot"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def list_things(token):
    url = "https://api2.arduino.cc/iot/v2/things"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def list_properties(token, thing_id):
    url = f"https://api2.arduino.cc/iot/v2/things/{thing_id}/properties"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)
    
    token = get_access_token(config['client_id'], config['client_secret'])
    
    # List all things
    print("=== Available Things ===")
    things = list_things(token)
    for thing in things:
        print(f"Name: {thing.get('name')}")
        print(f"ID: {thing.get('id')}")
        print("---")
    
    # List properties for Load Tester_2
    thing_id = "37cd8c67-7ebf-401f-a88e-321c9a285c4a"
    print(f"\n=== Properties for Thing {thing_id} ===")
    properties = list_properties(token, thing_id)
    
    for prop in properties:
        print(f"Name: {prop.get('name')}")
        print(f"ID: {prop.get('id')}")
        print(f"Variable: {prop.get('variable_name')}")
        print(f"Type: {prop.get('type')}")
        print(f"Last Value: {prop.get('last_value')}")
        print("---")

if __name__ == "__main__":
    main()
