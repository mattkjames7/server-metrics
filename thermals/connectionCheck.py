import socket

def connectionCheck(hostname, port=22, timeout=3):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set a timeout
        sock.settimeout(timeout)
        # Attempt to connect to the host
        result = sock.connect_ex((hostname, port))
        sock.close()
        # A result of 0 means the connection was successful
        return result == 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return False