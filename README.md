# Python Chat Application with File Sharing

A multi-client chat application supporting multiple messaging modes and file sharing over TCP/UDP.

## Features

### Messaging Modes

#### 1. **Broadcast** (Default)
- Send messages to all connected clients except yourself
- Just type a message and press Enter
- Example: `hello everyone` → all others see "YourName: hello everyone"

#### 2. **Unicast** (Private Messaging)
- Send private messages to a specific user
- Command: `/msg <nickname> <message>`
- Example: `/msg Frank hey there`
- Only the target user receives the message as `[Private] Sender: message`

#### 3. **Multicast** (Group Messaging)
- Create/join named groups and send messages to group members only
- Commands:
  - `/join <group>` - Join or create a group
  - `/group <group> <message>` - Send to group members
  - `/leave <group>` - Leave a group
- Example:
  ```
  /join football
  /group football did you watch the match?
  ```

### File Sharing

#### Commands
- `/files` - List all available files in SharedFiles directory with sizes
- `/download <filename> <tcp|udp>` - Download a file using TCP or UDP
  - TCP: Reliable, ordered delivery
  - UDP: Faster, connectionless transfer
- `/help` - Show all available commands
- `/quit` - Exit the chat

#### File Transfer Details
- Files are stored in `SharedFiles` directory on server
- Downloaded files saved to folder named after your username
- File sizes displayed in bytes
- Supports all file types (text, images, audio, video)

## Setup

### Environment Variables
Set `SERVER_SHARED_FILES` to specify the shared files directory:
```powershell
$env:SERVER_SHARED_FILES = "C:\Path\To\SharedFiles"
```
If not set, defaults to `./SharedFiles`

### Running the Application

1. **Start the Server:**
```powershell
python server.py [port]
```
Example: `python server.py 12000`

The server will:
- Listen on the specified TCP port for chat (default: 55555)
- Listen on UDP port (TCP port + 1) for file transfers
- Create SharedFiles directory if it doesn't exist
- Display connection information when clients connect (IP address and port)

2. **Start Clients:**
```powershell
python client.py [username] [hostname] [port]
```
Example: `python client.py John 127.0.0.1 12000`

Or simply run without arguments and enter details interactively:
```powershell
python client.py
```
- Enter your username when prompted
- Receive a welcome message from the server
- A folder with your username will be created for downloads
- All messages display with timestamps in [HH:MM:SS] format

## Usage Examples

All messages are displayed with timestamps in `[HH:MM:SS]` format.

### Connection Messages
```
  [14:23:15] George joined the chat!

  [14:23:42] Frank joined the chat!
```

### Basic Chat
```
  [14:24:01] George: hello everyone
  [14:24:05] Frank: hi George!
```

### Private Messaging
```
/msg Frank want to grab coffee?
  [14:24:30] [To Frank] want to grab coffee?

# Frank sees:
  [14:24:30] [Private] George: want to grab coffee?
```

### Group Chat
```
# George and Frank join a group
/join coursework
  [14:25:10] Joined group 'coursework'

# Send to group
/group coursework anyone done the lab?
# Only coursework members see:
  [14:25:15] [coursework] George: anyone done the lab?
```

### File Sharing
```
# List files
/files
  [14:26:00] Accessed SharedFiles folder - 3 files available
=== Available Files ===
report.pdf                     - 245,632 bytes
presentation.pptx              - 1,048,576 bytes
data.csv                       - 12,345 bytes
======================
Use: /download <filename> <tcp|udp>

# Download via TCP
/download report.pdf tcp
  [14:26:15] [Downloaded] report.pdf via TCP - 245,632 bytes
  [14:26:15] [Saved to] George/report.pdf

# Download via UDP
/download data.csv udp
  [14:26:30] [Downloaded] data.csv via UDP - 12,345 bytes
  [14:26:30] [Saved to] George/data.csv
```

## Architecture

### Server (`server.py`)
- **Threading**: One thread per connected client
- **TCP Socket**: Main communication channel (port 55555)
- **UDP Socket**: File transfer channel (port 55556)
- **Data Structures**:
  - `clients[]` - List of client sockets
  - `nicknames[]` - Corresponding usernames
  - `groups{}` - Dict of group_name → set of client sockets

### Client (`client.py`)
- **Threads**:
  - Receive thread: Listens for server messages
  - Write thread: Handles user input
- **Downloads**: Saved to `<username>/` directory
- **Protocols**: Supports both TCP and UDP file transfers

## Technical Details

### Message Format
All messages include timestamps in `[HH:MM:SS]` format:
- Chat: `[HH:MM:SS] <nickname>: <message>`
- Private: `[HH:MM:SS] [Private] <sender>: <message>`
- Group: `[HH:MM:SS] [<group>] <sender>: <message>`
- Join/Leave: `[HH:MM:SS] <username> joined/left the chat!` (with extra spacing)

### File Transfer Protocol

#### TCP
1. Server sends `FILE_START:<filename>:<size>`
2. Server sends file data in 4KB chunks
3. Server sends `FILE_END`
4. Client saves to `<username>/<filename>`

#### UDP
1. Client sends `REQUEST:<filename>` to UDP port
2. Server sends `START:<size>`
3. Server sends chunks as `DATA:<seq>:<data>`
4. Server sends `END`
5. Client reassembles and saves

### Error Handling
- Automatic group cleanup when empty
- Client disconnect removes from all groups
- File not found errors reported to client
- Socket reuse enabled (SO_REUSEADDR)

## Requirements
- Python 3.x
- Standard library only (socket, threading, os)
- Windows or Unix-like OS

## Notes
- All file transfers go through sockets (no hardcoded lists)
- File sizes computed dynamically from filesystem
- Groups created automatically on first `/join`
- Server must be running before clients connect
- Ensure ports 55555 (TCP) and 55556 (UDP) are available
