#!/usr/bin/env python3
"""
Network Test Utility for Street Fighter LAN
This utility helps test and debug network connections
"""

import socket
import sys
import time
import threading
from network_manager import NetworkManager

def test_local_ip():
    """Test getting local IP address"""
    print("=== Local IP Test ===")
    nm = NetworkManager()
    local_ip = nm.get_local_ip()
    print(f"Local IP: {local_ip}")
    return local_ip

def test_port_availability(port=12345):
    """Test if the game port is available"""
    print(f"=== Port {port} Availability Test ===")
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('', port))
        test_socket.close()
        print(f"Port {port} is available")
        return True
    except Exception as e:
        print(f"Port {port} is not available: {e}")
        return False

def test_host_scan():
    """Test scanning for available hosts"""
    print("=== Host Scan Test ===")
    nm = NetworkManager(is_host=False)
    print("Scanning for hosts...")
    start_time = time.time()
    hosts = nm.get_available_hosts()
    end_time = time.time()
    
    print(f"Scan completed in {end_time - start_time:.2f} seconds")
    print(f"Found {len(hosts)} hosts:")
    for host in hosts:
        print(f"  - {host}")
    
    return hosts

def test_host_server(duration=30):
    """Test hosting a server for a specified duration"""
    print(f"=== Host Server Test (for {duration} seconds) ===")
    nm = NetworkManager(is_host=True)
    
    def host_worker():
        if nm.start_host():
            print("Host started successfully. Waiting for connections...")
            time.sleep(duration)
        else:
            print("Failed to start host")
        nm.close()
    
    host_thread = threading.Thread(target=host_worker)
    host_thread.daemon = True
    host_thread.start()
    
    print(f"Host will run for {duration} seconds...")
    host_thread.join()
    print("Host test completed")

def test_client_connection(host_ip, timeout=5):
    """Test connecting to a specific host"""
    print(f"=== Client Connection Test to {host_ip} ===")
    nm = NetworkManager(is_host=False)
    
    print(f"Attempting to connect to {host_ip}...")
    start_time = time.time()
    
    if nm.connect_to_host(host_ip):
        end_time = time.time()
        print(f"Connected successfully in {end_time - start_time:.2f} seconds")
        
        # Test sending data
        test_data = {"test": "hello", "timestamp": time.time()}
        nm.send_data(test_data)
        print("Test data sent")
        
        # Wait a bit for response
        time.sleep(2)
        received = nm.get_received_data()
        if received:
            print(f"Received data: {received}")
        else:
            print("No data received")
        
        nm.close()
        return True
    else:
        print("Connection failed")
        nm.close()
        return False

def interactive_test():
    """Interactive test menu"""
    while True:
        print("\n=== Street Fighter Network Test Utility ===")
        print("1. Test Local IP")
        print("2. Test Port Availability")
        print("3. Scan for Hosts")
        print("4. Start Test Host (30 seconds)")
        print("5. Test Client Connection")
        print("6. Full Network Test")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            test_local_ip()
        elif choice == '2':
            port = input("Enter port (default 12345): ").strip()
            port = int(port) if port else 12345
            test_port_availability(port)
        elif choice == '3':
            test_host_scan()
        elif choice == '4':
            test_host_server()
        elif choice == '5':
            host_ip = input("Enter host IP to connect to: ").strip()
            if host_ip:
                test_client_connection(host_ip)
        elif choice == '6':
            print("Running full network test...")
            local_ip = test_local_ip()
            test_port_availability()
            hosts = test_host_scan()
            
            if hosts:
                print(f"\nTesting connection to first found host: {hosts[0]}")
                test_client_connection(hosts[0])
        else:
            print("Invalid choice")

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'ip':
            test_local_ip()
        elif command == 'port':
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 12345
            test_port_availability(port)
        elif command == 'scan':
            test_host_scan()
        elif command == 'host':
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            test_host_server(duration)
        elif command == 'connect':
            if len(sys.argv) > 2:
                test_client_connection(sys.argv[2])
            else:
                print("Usage: python network_test.py connect <host_ip>")
        else:
            print("Available commands: ip, port, scan, host, connect")
    else:
        interactive_test()

if __name__ == "__main__":
    main()
