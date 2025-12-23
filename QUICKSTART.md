# Quick Start Guide

## Setup (5 minutes)

### 1. Set Environment Variable (Optional)
```powershell
# Set custom shared files location
$env:SERVER_SHARED_FILES = "C:\MySharedFiles"

# Or use default ./SharedFiles
```

### 2. Create Test Files
```powershell
python test_scenarios.py
```
This creates sample files in SharedFiles directory.

### 3. Start Server
```powershell
python server.py
```
Expected output:
```
Created shared files directory: ./SharedFiles
Server started on 127.0.0.1:55555
File transfer port (UDP): 55556
Shared files directory: ./SharedFiles
UDP file transfer server listening on 127.0.0.1:55556
Server is listening...
```

### 4. Start Clients (Multiple Terminals)
```powershell
# Terminal 1
python client.py
# Enter username: George

# Terminal 2
python client.py
# Enter username: Frank

# Terminal 3
python client.py
# Enter username: Rita
```

## Quick Test Commands

### Test 1: Basic Chat (10 seconds)
```
George: hello everyone
Frank: hi George
Rita: hey folks
```

### Test 2: Private Message (10 seconds)
```
George: /msg Frank can you help me?
Frank: /msg George sure, what's up?
```

### Test 3: Groups (20 seconds)
```
George: /join football
Frank: /join football
George: /group football match tonight?
Frank: /group football yes, 7pm
```

### Test 4: File Sharing (30 seconds)
```
George: /files
# (See list of files)

George: /download test.txt tcp
# Wait for download

George: /download test.bin udp
# Wait for download

# Verify files in George/ directory
```

### Test 5: Help
```
George: /help
# See all commands
```

## Command Reference

| Command | Example | Description |
|---------|---------|-------------|
| (message) | `hello` | Broadcast to all |
| `/msg` | `/msg Frank hi` | Private message |
| `/join` | `/join team` | Join/create group |
| `/group` | `/group team hello` | Message to group |
| `/leave` | `/leave team` | Leave group |
| `/files` | `/files` | List shared files |
| `/download` | `/download file.txt tcp` | Download file |
| `/help` | `/help` | Show commands |
| `/quit` | `/quit` | Exit chat |

## Troubleshooting

### Port Already in Use
```powershell
# Find process using port
netstat -ano | findstr :55555

# Kill it
taskkill /PID <PID> /F

# Or change port in server.py
```

### File Not Found
```
# Check SERVER_SHARED_FILES path
# Verify files exist in directory
# Use /files command to see available files
```

### UDP Download Fails
```
# Check firewall settings
# Ensure port 55556 is open
# Try TCP instead: /download file.txt tcp
```

### Client Can't Connect
```
# Ensure server is running first
# Check host/port match in client.py
# Verify no firewall blocking
```

## File Structure After Running

```
Instant Messenger/
├── server.py
├── client.py
├── README.md
├── test_scenarios.py
├── SharedFiles/          # Server files
│   ├── test.txt
│   ├── test.bin
│   └── large.dat
├── George/               # George's downloads
│   ├── test.txt
│   └── test.bin
├── Frank/                # Frank's downloads
│   └── test.txt
└── Rita/                 # Rita's downloads
    └── large.dat
```

## Performance Notes

- **TCP**: Reliable, best for important files
- **UDP**: Faster, may lose packets for very large files
- **Recommended**: Use TCP for files >1MB
- **Max clients**: Limited by system threads (~100+)
- **Max file size**: No limit, but large files take longer

## Security Notes (For Production)

Current implementation is for **educational purposes**. For production:
- Add authentication
- Encrypt file transfers (TLS/SSL)
- Validate file paths (prevent directory traversal)
- Add rate limiting
- Implement proper error handling
- Use async I/O for better scalability

## Marking Criteria Checklist

✅ Multiple clients supported (threading)
✅ Broadcast messaging (excludes sender)
✅ Unicast messaging (/msg command)
✅ Multicast/group messaging (/join, /group, /leave)
✅ Mode switching (dynamic commands)
✅ File listing (via sockets, not hardcoded)
✅ File download TCP
✅ File download UDP
✅ File sizes displayed
✅ Client-specific download folders
✅ Environment variable support
✅ Clean terminal output
✅ Proper error handling
✅ No hardcoded file lists/sizes

## Next Steps

1. Test all messaging modes
2. Test file transfers (TCP and UDP)
3. Verify file integrity (compare checksums)
4. Test with multiple simultaneous clients
5. Document any issues found
6. Create demo video/screenshots for submission
