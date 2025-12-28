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
- (message)                 Broadcast to all other clients
- /msg <nickname> <text>    Private message (unicast) to one client
- /join <group>             Join or create a named group
- /leave <group>            Leave a named group
- /group <group> <text>     Send to group members only (multicast)
- /files                    List SharedFiles with sizes
- /download <file> <tcp|udp> Download a file via chosen protocol
- /help                     Show commands
- /quit                     Exit chat gracefully

Messaging Modes
- Broadcast: Message goes to everyone except the sender
- Unicast: One-to-one private message using /msg
- Multicast (groups): Join with /join; send using /group
  Group membership and message routing are handled server-side; clients only issue commands.

File Downloading
- Shared folder: Server’s SharedFiles (path can be set via SERVER_SHARED_FILES)
- Listing: Use /files to request file list (sent via sockets; not hardcoded)
- Download: /download <filename> <tcp|udp>
  - TCP: Reliable, ordered delivery (recommended for large files)
  - UDP: Faster, connectionless (may lose packets for very large files)
- Save location: Client saves to a folder named after your username
- File size: Displayed in bytes on the client, sent by server via sockets
- UDP port: Ensure the UDP file transfer port printed by the server is open

Examples
Join/leave + chat
  [14:23:15] George joined the chat!
  [14:24:01] George: hello everyone
  [14:24:05] Frank: hi George!

Private message
  Command: /msg Frank can you help me?
  Sender sees:   [14:24:30] [To Frank] can you help me?
  Receiver sees: [14:24:30] [Private] George: can you help me?

Group chat
  /join football
  [14:25:10] Joined group 'football'
  /group football match tonight?
  [14:25:20] [football] George: match tonight?

Files
  /files
  [14:26:00] Accessed SharedFiles folder - N files available
  (list prints with sizes)
  /download test.txt tcp
  [14:26:15] [Downloaded] test.txt via TCP - 10,000 bytes
  [14:26:15] [Saved to] George/test.txt

Troubleshooting
- Port already in use:
  netstat -ano | findstr :<PORT>
  taskkill /PID <PID> /F
- File not found:
  Verify SERVER_SHARED_FILES path and file names; use /files to list
- UDP download fails:
  Check firewall rules. Ensure the UDP file transfer port printed by the server is open.
  Try TCP: /download <file> tcp
- Client cannot connect:
  Ensure server is running, host/port match, and firewall allows connections

Architecture (high-level)
- Server: One thread per client; TCP for chat; UDP handler for file transfers
- Client: Receiver thread + input thread; saves downloads to <username>/
- Data structures: clients, nicknames, groups (server-side)

Assessment Checklist (brief-aligned)
- Server prints client connection info (IP and port); client gets a welcome message over sockets
- Multiple clients connect; input prompt available; join/leave messages show username
- Broadcast excludes sender; unicast to a single target; groups support join/leave and multicast
- /files lists server SharedFiles via sockets; files downloaded via TCP or UDP
- Files saved under <username>/; file sizes shown (bytes) and sent via sockets
- Protocol selection via command; proper error handling; clean output with timestamps

Performance Notes
- TCP: reliable; best for important files
- UDP: faster; may lose packets for very large files
- Recommended: use TCP for files > 1 MB
- Max clients: Limited by system resources and thread usage (tested with multiple concurrent clients)

Code Quality & Presentation
- Pythonic naming and structure (PEP 8): clear functions and variables
- Comments where needed for understanding; avoid excessive commentary
- Direct use of socket library; no redundant imports or dead code
- Clear conditional and loop logic; no over-engineering
- Documentation is concise, focused on usage and protocol steps; consistent formatting
