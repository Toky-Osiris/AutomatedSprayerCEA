
import socket
import json

def send_signal(signal, host='192.168.254.51', port=1234, duration=18000):
    """
    Sends a signal to an IoT device via TCP socket.
    :param signal: List of predictions (e.g. ['Spray', 'Do not spray', ...])
    :param host: IP address of the IoT device
    :param port: Port number for the socket connection
    :param duration: Duration to activate solenoids (default 18000 ms)
    """
    signal_json = {
        "solenoids": signal,
        "duration": duration
    }
    message = json.dumps(signal_json) + '\n'

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode())
            data = s.recv(1024)
            print("Received:", data.decode())
        print("Signal sent!")
    except Exception as e:
        print("Socket error:", e)