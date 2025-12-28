"""
Test script to demonstrate all messaging modes and file sharing.
Run this after starting server.py to test functionality.
"""

print("""
=== CHAT APPLICATION TEST SCENARIOS ===

Prerequisites:
1. Start server.py first
2. Create some test files in SharedFiles directory
3. Open multiple client.py instances

TEST 1: BROADCAST MESSAGING
----------------------------
Client 1 (George):
  > hello everyone

Expected:
- Frank sees: "  [14:24:01] George: hello everyone"
- Rita sees: "  [14:24:01] Rita: hello everyone"
- George does NOT see his own message echoed (broadcast excludes sender)

TEST 2: UNICAST (PRIVATE) MESSAGING
------------------------------------
Client 1 (George):
  > /msg Frank hey, can you help me?

Expected:
- George sees: "  [14:24:30] [To Frank] hey, can you help me?"
- Frank sees: "  [14:24:30] [Private] George: hey, can you help me?"
- Rita sees: nothing (unicast is one-to-one)

TEST 3: GROUP MESSAGING (MULTICAST)
------------------------------------
Client 1 (George):
  > /join football
  Expected: "  [14:25:10] Joined group 'football'"

Client 2 (Frank):
  > /join football
  Expected: "  [14:25:15] Joined group 'football'"

Client 3 (Rita):
  > /join coursework
  Expected: "  [14:25:20] Joined group 'coursework'"

Client 1 (George):
  > /group football anyone watching the match?

Expected:
- Frank sees: "  [14:25:25] [football] George: anyone watching the match?"
- Rita sees: nothing (not in football group - multicast to group only)
- George does NOT see his own group message

TEST 4: FILE LISTING
--------------------
Any Client:
  > /files

Expected output:
  [14:26:00] Accessed SharedFiles folder - 3 files available
=== Available Files ===
document.pdf                   - 52,431 bytes
image.jpg                      - 245,632 bytes
video.mp4                      - 5,242,880 bytes
======================
Use: /download <filename> <tcp|udp>

Note: File count and sizes sent via socket (not hardcoded)

TEST 5: FILE DOWNLOAD (TCP)
----------------------------
Client 1 (George):
  > /download document.pdf tcp

Expected:
- "  [14:26:15] [Downloaded] document.pdf via TCP - 52,431 bytes"
- "  [14:26:15] [Saved to] George/document.pdf"
- File exists in George/ directory
- File transferred via network socket (reliable, ordered delivery)

TEST 6: FILE DOWNLOAD (UDP)
----------------------------
Client 1 (George):
  > /download image.jpg udp

Expected:
- "  [14:26:30] [Downloaded] image.jpg via UDP - 245,632 bytes"
- "  [14:26:30] [Saved to] George/image.jpg"
- File exists in George/ directory
- Verify file size matches original
- File transferred via UDP (faster, connectionless)

TEST 7: MODE SWITCHING
----------------------
Client 1 (George):
  > hello everyone          # broadcast
  Expected: "  [14:27:00] George: hello everyone" (all except George)

  > /msg Frank private      # unicast
  Expected: "  [14:27:05] [To Frank] private"

  > /join team             # join group
  Expected: "  [14:27:10] Joined group 'team'"

  > /group team hi team    # multicast
  Expected: "  [14:27:15] [team] George: hi team" (team members only)

  > hello all again        # back to broadcast
  Expected: "  [14:27:20] George: hello all again" (all except George)

Expected:
- All modes work sequentially without reconnection
- Client can dynamically switch between broadcast, unicast, and multicast
- Messages routed correctly based on mode

TEST 8: HELP COMMAND
--------------------
Any Client:
  > /help

Expected output:
=== Commands ===
/msg <nickname> <message>    - Send private message
/join <group>                - Join a group
/leave <group>               - Leave a group
/group <group> <message>     - Send message to group
/files                       - List available files
/download <file> <tcp|udp>   - Download file
/help                        - Show this help
/quit                        - Exit chat
================

TEST 9: GROUP LEAVE
-------------------
Client 1 (George):
  > /join football
  > /leave football

Expected:
- "Left group 'football'"
- Other football members see: "George left group 'football'"

TEST 10: CLIENT DISCONNECT
---------------------------
Client 1 (George):
  > /quit

Expected:
- George sees: "You have left the chat."
- All other clients see: "

  [14:28:00] George left the chat!

"
- George removed from all groups
- Server prints disconnect info with IP and port
- Server continues running (doesn't crash)

VERIFICATION CHECKLIST:
-----------------------
**Part 1.1 - Server/Client (8 marks):**
[ ] Server prints connection info (IP + port)
[ ] Client displays welcome message (sent via socket)
[ ] Multiple clients connect successfully
[ ] Input prompt available for messages
[ ] "[username] has joined" on all clients
[ ] /quit command leaves gracefully
[ ] Unexpected disconnect handled
[ ] Server doesn't crash on disconnect

**Part 1.2 - Messaging (15 marks):**
[ ] Multiple messages can be sent
[ ] Broadcast excludes sender
[ ] Unicast reaches only target (/msg)
[ ] Named groups can be joined/left
[ ] Groups auto-create on first /join
[ ] Multicast to group members only
[ ] Mode switching works without reconnect

**Part 1.3 - File Downloads (20 marks):**
[ ] SharedFiles folder exists
[ ] /files command accesses folder
[ ] SERVER_SHARED_FILES env variable works
[ ] Success message shows file count (via socket)
[ ] File list displays correctly
[ ] All file types can be downloaded
[ ] Files saved to username folder
[ ] Files transferred via socket (not hardcoded)
[ ] TCP/UDP protocol selection works
[ ] File sizes displayed in bytes (via socket)

**Additional:**
[ ] Timestamps on all messages [HH:MM:SS]
[ ] Port reuse (SO_REUSEADDR) works on restart
[ ] Downloaded files are not corrupted
[ ] Command-line args work: python client.py [username] [host] [port]

ERROR CASES TO TEST:
--------------------
1. /msg InvalidUser hello
   → "User 'InvalidUser' not found"

2. /download nonexistent.txt tcp
   → "[Error] File not found"

3. /group notmember hello
   → "You are not in group 'notmember'"

4. /download file.txt xyz
   → "Protocol must be 'tcp' or 'udp'"

PERFORMANCE TESTS:
------------------
1. Large file (>10MB) via TCP
2. Large file (>10MB) via UDP
3. Multiple simultaneous downloads
4. Broadcast to 10+ clients
5. Multiple groups with overlapping members

""")

# Sample file creator
import os

def create_test_files():
    """Create sample files for testing."""
    shared_dir = os.environ.get("SERVER_SHARED_FILES", "./SharedFiles")

    if not os.path.exists(shared_dir):
        os.makedirs(shared_dir)

    # Create text file
    with open(os.path.join(shared_dir, "test.txt"), "w") as f:
        f.write("This is a test file for the chat application.\n" * 100)

    # Create binary file
    with open(os.path.join(shared_dir, "test.bin"), "wb") as f:
        f.write(b'\x00\x01\x02\x03' * 1000)

    # Create larger file
    with open(os.path.join(shared_dir, "large.dat"), "wb") as f:
        f.write(b'A' * (1024 * 100))  # 100KB

    print(f"\nCreated test files in {shared_dir}:")
    for filename in os.listdir(shared_dir):
        filepath = os.path.join(shared_dir, filename)
        size = os.path.getsize(filepath)
        print(f"  {filename}: {size:,} bytes")

if __name__ == "__main__":
    create_test_files()
