import serial
import serial.tools.list_ports
import time
import sys

def get_port():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("No COM ports found. Is the Mega plugged in?")
        sys.exit(1)
        
    print("Available Ports:")
    for i, port in enumerate(ports):
        print(f"[{i}] {port.device}")
        
    choice = input("Select port number: ")
    try:
        return ports[int(choice)].device
    except (ValueError, IndexError):
        print("Invalid selection.")
        sys.exit(1)

def run_benchmark(port_name):
    print(f"\n--- Starting Benchmark on {port_name} at 115200 baud ---")
    try:
        # Open serial port
        ser = serial.Serial(port_name, 115200, timeout=1)
        print("Waiting 2 seconds for Arduino to initialize...")
        time.sleep(2) 
        
        # 1. Force the Arduino into MAX SPEED mode (0ms delay)
        ser.write(b"0\n")
        time.sleep(0.1)
        ser.reset_input_buffer() # Clear old data
        
        # --- READ SPEED TEST ---
        print("\n[1/2] Testing Read Speed (Mega -> PC)...")
        print("Listening for 5 seconds...")
        start_time = time.time()
        bytes_read = 0
        lines_read = 0
        
        while time.time() - start_time < 5.0:
            if ser.in_waiting:
                chunk = ser.read(ser.in_waiting)
                bytes_read += len(chunk)
                lines_read += chunk.count(b'\n')
                
        read_time = time.time() - start_time
        bps = bytes_read / read_time
        lps = lines_read / read_time
        
        print(f"✔ Read Speed: {bps:,.2f} Bytes/sec")
        print(f"✔ Throughput: {lps:,.0f} Data Packets/sec")

        # --- WRITE SPEED TEST ---
        print("\n[2/2] Testing Write Speed (PC -> Mega)...")
        print("Blasting 10,000 speed commands...")
        
        ser.reset_output_buffer()
        start_time = time.time()
        
        writes = 10000
        payload = b"0\n" # The command to set delay to 0
        bytes_written = len(payload) * writes
        
        for _ in range(writes):
            ser.write(payload)
            
        ser.flush() # Force Python to wait until the OS actually sends the data
        write_time = time.time() - start_time
        
        wps = writes / write_time
        wbps = bytes_written / write_time
        
        print(f"✔ Write Speed: {wbps:,.2f} Bytes/sec")
        print(f"✔ Throughput:  {wps:,.0f} Commands/sec")
        
        ser.close()
        print("\n--- Benchmark Complete ---")
        
    except Exception as e:
        print(f"\n[!] Error connecting to serial port: {e}")

if __name__ == '__main__':
    target_port = get_port()
    run_benchmark(target_port)