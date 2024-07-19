from pymodbus.client import ModbusTcpClient
import struct

# Coefficients polynomiaux pour le thermocouple de type K
COEFFICIENTS = [
    0.0,
    2.5173462e-2,
    -1.1662878e-6,
    -1.0833638e-9,
    -8.9773540e-13,
    -3.7342377e-16,
    -8.6632643e-20,
    -1.0450598e-23,
    -5.1920577e-28
]

def voltage_to_temperature_K(voltage_mV):
    temperature_C = 0.0
    power = 1
    for coefficient in COEFFICIENTS:
        temperature_C += coefficient * power
        power *= voltage_mV
    return temperature_C

def read_and_convert_thermocouple(ip, port, transaction_id, unit_id, start_address, quantity):
    # Créer un client Modbus TCP
    client = ModbusTcpClient(ip, port)
    
    try:
        # Se connecter à l'appareil
        client.connect()
        
        # Construire le message Modbus TCP personnalisé
        function_code = 0x04
        request_pdu = struct.pack('>BHH', function_code, start_address, quantity)
        mbap_header = struct.pack('>HHH', transaction_id, 0, len(request_pdu) + 1)
        message = mbap_header + struct.pack('B', unit_id) + request_pdu
        
        # Envoyer le message
        client.socket.send(message)
        
        # Recevoir la réponse (maximum 1024 octets)
        response = client.socket.recv(1024)
        
        # Afficher la réponse brute
        print(f"Réponse brute de l'appareil: {response.hex().upper()}")
        
        # Analyse de la réponse
        if response[7] == function_code:
            byte_count = response[8]
            data = response[9:9 + byte_count]
            
            # Traiter chaque valeur dans les données
            temperatures = []
            for a, i in enumerate(range(0, byte_count, 2)):
                raw_value = struct.unpack('>H', data[i:i + 2])[0]
                current_mA = raw_value / 10  # Conversion en mA
                if raw_value == 64537:
                	raw_value = None
                	current_mA = None
                print(f"Valeur brute {a}: {raw_value}, Degrée : {current_mA} °C")
            return temperatures
    
    except Exception as e:
        print(f"Erreur de communication : {e}")
    
    finally:
        # Fermer la connexion
        client.close()

# Adresse IP et port de l'appareil
device_ip = '192.168.1.6'
device_port = 502
transaction_id = 0x001D
unit_id = 0x01
start_address = 0x0190  # Adresse trouvée
quantity = 0x0002  # Lire 6 registres

# Lire les valeurs et les convertir en °C
temperatures_C = read_and_convert_thermocouple(device_ip, device_port, transaction_id, unit_id, start_address, quantity)
print(f"Températures en °C : {temperatures_C}")
