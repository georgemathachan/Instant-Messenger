Instant Messenger — Usage Guide (Windows, Python 3.13)
====================================================

Overview
- Multi-client chat with Broadcast, Unicast (private), and Multicast (groups)
- File sharing from server’s SharedFiles via TCP or UDP
- Clean terminal output with timestamps and clear commands

Requirements
- OS: Windows
- Python: 3.13
- Libraries: Python standard library only (socket, threading, os, time)
- Networking: TCP for chat; UDP optional for file download
- Ports: Server prints TCP and UDP ports at startup
- Environment: Optional `SERVER_SHARED_FILES` to set shared folder path

Quick Start
1) Set SharedFiles location (optional)
   PowerShell:
   $env:SERVER_SHARED_FILES = "C:\MySharedFiles"

2) Create test files
   python test_scenarios.py

3) Start the server
   python server.py 12000
   The server prints:
   - TCP port (chat): 12000
   - UDP port (file transfer): 12001
   - SharedFiles directory path

4) Start clients
   With args:
   python client.py George 127.0.0.1 12000

   Or interactive:
   python client.py
   (Enter username, hostname, and port when prompted)

Note: All messages display with [HH:MM:SS] timestamps (added client-side for readability; not transmitted over the network)

Commands
- (message): broadcast to all except sender
- /msg <nickname> <message>: private message
- /join <group>: join/create group
- /leave <group>: leave group
- /group <group> <message>: send to group members
- /files: list SharedFiles with sizes
- /download <filename> <tcp|udp>: download via chosen protocol
- /help: show commands
- /quit: exit chat

Notes
- Downloads saved to `<username>/`; sizes shown in bytes
- UDP: ensure the file transfer port printed by the server is open
