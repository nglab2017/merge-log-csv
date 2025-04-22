import serial
import pynmea2
import time
import csv
import sys

def log_gps_data(port="/dev/ttyACM0", baud=9600, log_filename="gps_log2.txt"):
    try:
        serialPort = serial.Serial(port, baudrate=baud, timeout=0.5)
        print(f"Logging GPS data to {log_filename}. Press Ctrl+C to stop.")
        while True:
            try:
                data = serialPort.readline().decode().strip()
                if data.startswith("$GPGGA"):
                    msg = pynmea2.parse(data)
                    timestamp = msg.timestamp
                    latitude = msg.latitude
                    longitude = msg.longitude
                    altitude = msg.altitude
                    num_sats = msg.num_sats

                    log_string = f"{timestamp}, Lat: {latitude:.6f}, Lon: {longitude:.6f}, Alt: {altitude}, Sats: {num_sats}"
                    print(log_string)

                    # Log to a file
                    with open(log_filename, "a") as log_file:
                        log_file.write(log_string + "\n")

            except pynmea2.ParseError as e:
                print(f"Parse error: {e}")
            except UnicodeDecodeError as e:
                print(f"Decode error: {e}")
            time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except KeyboardInterrupt:
        print("\nLogging stopped by user.")
    finally:
        if 'serialPort' in locals() and serialPort.is_open:
            serialPort.close()

def convert_log_to_csv(log_file_path, csv_file_path):
    """
    Converts a GPS log file to a CSV file.

    Args:
        log_file_path (str): Path to the input GPS log file.
        csv_file_path (str): Path to the output CSV file.
    """
    try:
        with open(log_file_path, 'r') as infile, open(csv_file_path, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            # Write header
            writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Altitude', 'Satellites'])
            for line in infile:
                try:
                    # Example line: "12:34:56, Lat: 12.345678, Lon: 98.765432, Alt: 123.4, Sats: 7"
                    parts = line.strip().split(',')
                    timestamp = parts[0]
                    lat = parts[1].split(':')[1].strip()
                    lon = parts[2].split(':')[1].strip()
                    alt = parts[3].split(':')[1].strip()
                    sats = parts[4].split(':')[1].strip()
                    writer.writerow([timestamp, lat, lon, alt, sats])
                except Exception as e:
                    print(f"Skipping malformed line: {line.strip()} ({e})")
        print(f"Successfully converted '{log_file_path}' to '{csv_file_path}'")
    except FileNotFoundError:
        print(f"Error: Log file '{log_file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Select an option:")
    print("1. Log GPS data")
    print("2. Convert log file to CSV")
    choice = input("Enter 1 or 2: ").strip()
    if choice == "1":
        port = input("Enter serial port (default /dev/ttyACM0): ").strip() or "/dev/ttyACM0"
        baud = input("Enter baud rate (default 9600): ").strip()
        baud = int(baud) if baud else 9600
        log_filename = input("Enter log file name (default gps_log2.txt): ").strip() or "gps_log2.txt"
        log_gps_data(port, baud, log_filename)
    elif choice == "2":
        log_file = input("Enter log file name (default gps_log2.txt): ").strip() or "gps_log2.txt"
        csv_file = input("Enter output CSV file name (default gps_data2.csv): ").strip() or "gps_data2.csv"
        convert_log_to_csv(log_file, csv_file)
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main()
