import socket
import json
from dice import validate_probabilities, roll_biased_dice
HOST = "127.0.0.1"
PORT = 8081


def parse_request_body(request_str):
    if "\r\n\r\n" in request_str:
        return request_str.split("\r\n\r\n", 1)[1].strip()
    return ""


def handle_roll_dice(request_str):
    body_str = parse_request_body(request_str)

    if not body_str:
        return 400, {"status": "error", "message": "'probabilities' field is required."}

    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError as e:
        return 400, {"status": "error", "message": f"Invalid JSON: {e}"}

    probabilities    = payload.get("probabilities")
    number_of_random = payload.get("number_of_random", 1)

    if probabilities is None:
        return 400, {"status": "error", "message": "'probabilities' field is required."}

    valid, error_msg = validate_probabilities(probabilities)
    if not valid:
        return 400, {"status": "error", "message": error_msg}

    if not isinstance(number_of_random, int) or number_of_random < 1:
        return 400, {"status": "error", "message": "'number_of_random' must be a positive integer."}

    dices = roll_biased_dice(probabilities, number_of_random)
    return 200, {"status": "success", "probabilities": probabilities, "dices": dices}


def run_server(host=HOST, port=PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server is listening on http://{host}:{port}/roll_dice ...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address} established.")

        request = b""
        client_socket.settimeout(5.0)
        try:
            while True:
                chunk = client_socket.recv(4096)
                if not chunk:
                    break
                request += chunk
                if b"\r\n\r\n" in request:
                    header_raw = request.split(b"\r\n\r\n")[0].decode("utf-8", errors="replace")
                    body_so_far = request.split(b"\r\n\r\n", 1)[1]
                    content_length = 0
                    for line in header_raw.split("\r\n")[1:]:
                        if line.lower().startswith("content-length:"):
                            content_length = int(line.split(":", 1)[1].strip())
                    if len(body_so_far) >= content_length:
                        break
        except socket.timeout:
            pass

        request_str = request.decode("utf-8", errors="replace")
        print(f"Request received ({len(request_str)} bytes):")
        print("*" * 50)
        print(request_str[:300])
        print("*" * 50)

        first_line = request_str.split("\r\n")[0]
        method = first_line.split(" ")[0] if " " in first_line else ""

        if "/roll_dice" in first_line and method in ("GET", "POST"):
            status_code, response_data = handle_roll_dice(request_str)
            response_json = json.dumps(response_data)
            status_text = {200: "200 OK", 400: "400 Bad Request"}.get(status_code, f"{status_code}")
            response = (f"HTTP/1.1 {status_text}\r\n"
                        f"Content-Type: application/json\r\n"
                        f"Content-Length: {len(response_json)}\r\n"
                        f"Connection: close\r\n\r\n"
                        f"{response_json}")
        elif method in ("GET", "POST"):
            body = json.dumps({"status": "error", "message": "Endpoint not found. Use /roll_dice"})
            response = f"HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{body}"
        else:
            response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

        client_socket.sendall(response.encode("utf-8"))
        client_socket.close()
        print("Waiting for the next TCP request...")


if __name__ == "__main__":
    run_server()
