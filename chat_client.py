import threading
import sys
import socket
import json

from chatui import init_windows, read_command, print_message, end_windows

def usage():
    print("usage: chat_client.py prefix host port", file=sys.stderr)

def main(argv):
    try:
        nickname = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1

    s = socket.socket()
    s.connect((host, port))

    s.send(json.dumps({"nickname": nickname, "type": "hello"}).encode())
    init_windows()
    
    global server_thread,user_thread
    server_thread = [threading.Thread(target=server_runner, args=(s,), daemon=True)]
    user_thread = [threading.Thread(target=user_runner, args=(s, nickname))]

    join_and_start_threads()
    end_windows()

def join_and_start_threads():
    for server,user in zip(server_thread,user_thread):
        server.start(),user.start()
    user.join()

def server_runner(connection):
    while True:
        print_message(find_packet(load_json(connection)))

def find_packet(message):
    if message["type"] == "chat":
      return "{}: {}".format(message["nickname"], message["message"])
    elif message["type"] == "leave":
      return "*** {} has left the chat".format(message["nickname"])
    elif message["type"] == "join":
      return "*** {} has joined the chat".format(message["nickname"])

def client_prompt(name):
  return read_command("{}> ".format(name))

def user_runner(connection, name):
    while True:
        input = client_prompt(name)
        if len(input) == 0:
            continue
        elif input == "/q":
            connection.close()
            break
        else:
            send_connection(connection,input)

def send_connection(connection,input):
  connection.send(json.dumps({"message": input, "type": "chat"}).encode())

def load_json(connection):
  return json.loads(connection.recv(4096).decode())

if __name__ == "__main__":
    sys.exit(main(sys.argv))