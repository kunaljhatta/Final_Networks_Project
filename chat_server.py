import json
import sys
import socket
import select

def usage():
    print("usage: chat_server.py port", file=sys.stderr)

def run_server(port):
    server_socket = socket.socket()
    server_socket.bind(('', port))
    server_socket.listen()
    
    name_dict = {}
    socket_set = {server_socket}

    while True:
        read, _, _ = select.select(socket_set, {}, {})
        
        for s in read:
            if s is server_socket: 
                new_socket, _ = server_socket.accept()
                socket_set.add(new_socket)
            else:
                message = s.recv(4096) 
                if not message:
                    s.close()
                    socket_set.remove(s)
                    handle_leave_packet(s,name_dict)
                else:
                    handle_packet(s, message.decode(), name_dict)

def displays_message_type(message, user_map):
    for user_socket in user_map:
            user_socket.send(message.encode())

def handle_join_packet(packet, key, user_map):
    user_map[key] = packet["nickname"]
    join_packet = {
    "type": "join",
    "nickname": packet["nickname"]
    }
    join = json.dumps(join_packet)
    print(join)
    displays_message_type(join, user_map)
    print( "*** {} has joined the chat".format(packet['nickname']))

def handle_chat_packet(packet,key,user_map):
    chat_packet = {
    "type": "chat",
    "message": packet["message"],
    "nickname": user_map[key]
    }
    chat = json.dumps(chat_packet)
    print(chat)
    displays_message_type(chat, user_map)
    print("{}: {}".format(user_map[key], packet['message']))

def handle_leave_packet(s,user_map):
    user = user_map.pop(s)
    leave_packet ={
    "type": "leave", 
    "nickname": user
    }
    leave = json.dumps(leave_packet)
    print(leave)
    displays_message_type(leave, user_map)
    print("*** {} has left the chat".format(user))

def handle_packet(key, message, user_map):
    packet = json.loads(message)
    if packet["type"] == "hello":
      handle_join_packet(packet,key,user_map)
    elif packet["type"] == "chat":
      handle_chat_packet(packet,key,user_map)

def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))