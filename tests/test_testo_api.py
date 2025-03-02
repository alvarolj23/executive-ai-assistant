import requests
import os
import json
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HeatingDevice:
    """Represents essential information about a heating device."""
    type: str
    brand: str
    model: str
    year: str
    power: str
    serial_number: str
    fuel_type: str


@dataclass
class Client:
    """Represents essential client information."""
    id: int
    name: str
    address: str
    city: str
    postal_code: str
    phone: str
    email: str
    devices: List[HeatingDevice]


def process_testo_response(data: Dict[str, Any]) -> List[Client]:
    """
    Process the Testo API response and extract essential client information.
    
    Args:
        data: Raw API response data
        
    Returns:
        List[Client]: List of processed client information
    """
    clients = []
    
    for client_data in data.get("data", []):
        # Extract basic client info
        client = Client(
            id=client_data.get("id"),
            name=client_data.get("name", ""),
            address=client_data.get("address", ""),
            city=client_data.get("city", ""),
            postal_code=client_data.get("postal_code", ""),
            phone=client_data.get("phone", ""),
            email=client_data.get("email", ""),
            devices=[]
        )
        
        # Process heating appliances
        for appliance in client_data.get("heating_appliance", []):
            device_info = None
            
            # Check which region's data to use
            if appliance.get("flanders"):
                device_info = appliance["flanders"]
            elif appliance.get("brassels"):
                device_info = appliance["brassels"]
            elif appliance.get("wallonie"):
                device_info = appliance["wallonie"]
                
            if device_info:
                # Map fuel type to readable string
                fuel_type = "Unknown"
                if device_info.get("fuel") == "0":
                    fuel_type = "Gas"
                elif device_info.get("fuel") == "1":
                    fuel_type = "Oil"
                elif device_info.get("fuel") == "2":
                    fuel_type = "Solid"
                
                device = HeatingDevice(
                    type=appliance.get("name", ""),
                    brand=device_info.get("device_make", ""),
                    model=device_info.get("device_type", ""),
                    year=device_info.get("device_year", ""),
                    power=f"{device_info.get('device_nominal_power', '0')} kW",
                    serial_number=device_info.get("device_manufacturing_no", ""),
                    fuel_type=fuel_type
                )
                client.devices.append(device)
        
        clients.append(client)
    
    return clients


def print_client_summary(client: Client) -> None:
    """
    Print a formatted summary of client information.
    
    Args:
        client: Client object to summarize
    """
    print("\n" + "="*50)
    print(f"Client: {client.name}")
    print(f"Contact: {client.phone} | {client.email}")
    print(f"Address: {client.address}, {client.postal_code} {client.city}")
    print("\nDevices:")
    for device in client.devices:
        print("-" * 40)
        print(f"Type: {device.type}")
        print(f"Brand/Model: {device.brand} {device.model}")
        print(f"Year: {device.year}")
        print(f"Power: {device.power}")
        print(f"Fuel: {device.fuel_type}")
        print(f"Serial: {device.serial_number}")


def test_api_connection() -> None:
    """
    Test the connection to the Testo API production endpoint.
    
    This function attempts to pull client data from the Testo API using the configured
    API key from environment variables, processes the response, and displays a clean summary.
    
    Returns:
        None
    """
    url = "https://api.testocloud.be/expose/pull-client"
    headers: Dict[str, str] = {
        "X-expose-secret-key": os.getenv("TESTO_API_KEY", ""),
        "Content-Type": "application/json"
    }
    params: Dict[str, str] = {
        "from_date": "2023-01-01",
        "to_date": "2023-01-15",
        "language": "nl"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        print(f"API Status Code: {response.status_code}")
        
        # Process and display clean data
        data = response.json()
        clients = process_testo_response(data)
        
        print(f"\nFound {len(clients)} clients")
        for client in clients:
            print_client_summary(client)
            
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except json.JSONDecodeError:
        print(f"Raw Response: {response.text}")


if __name__ == "__main__":
    test_api_connection()
