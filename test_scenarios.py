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
- Frank sees: "George: hello everyone"
- Rita sees: "George: hello everyone"
- George does NOT see his own message echoed

TEST 2: UNICAST (PRIVATE) MESSAGING
------------------------------------
Client 1 (George):
  > /msg Frank hey, can you help me?

Expected:
- George sees: "[To Frank] hey, can you help me?"
- Frank sees: "[Private] George: hey, can you help me?"
- Rita sees: nothing

TEST 3: GROUP MESSAGING (MULTICAST)
------------------------------------
Client 1 (George):
  > /join football

Client 2 (Frank):
  > /join football

Client 3 (Rita):
  > /join coursework

Client 1 (George):
  > /group football anyone watching the match?

Expected:
- Frank sees: "[football] George: anyone watching the match?"
- Rita sees: nothing (not in football group)
- George does NOT see his own group message

TEST 4: FILE LISTING
--------------------
Any Client:
  > /files

Expected output:
=== Available Files ===
document.pdf                   - 52,431 bytes
image.jpg                      - 245,632 bytes
video.mp4                      - 5,242,880 bytes
======================
Use: /download <filename> <tcp|udp>

TEST 5: FILE DOWNLOAD (TCP)
----------------------------
Client 1 (George):
  > /download document.pdf tcp

Expected:
- Progress shown
- "[Downloaded] document.pdf via TCP - 52,431 bytes"
- "[Saved to] George/document.pdf"
- File exists in George/ directory

TEST 6: FILE DOWNLOAD (UDP)
----------------------------
Client 1 (George):
  > /download image.jpg udp

Expected:
- "[Downloaded] image.jpg via UDP - 245,632 bytes"
- "[Saved to] George/image.jpg"
- File exists in George/ directory
- Verify file size matches original

TEST 7: MODE SWITCHING
----------------------
Client 1 (George):
  > hello everyone          # broadcast
  > /msg Frank private      # unicast
  > /join team             # join group
  > /group team hi team    # multicast
  > hello all again        # back to broadcast

Expected:
- All modes work sequentially
- No reconnection needed
- Messages routed correctly

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
- All other clients see: "George left the chat!"
- George removed from all groups
- Server prints disconnect info

VERIFICATION CHECKLIST:
-----------------------
[ ] Broadcast excludes sender
[ ] Unicast reaches only target
[ ] Groups work independently
[ ] Files list shows correct sizes
[ ] TCP download completes successfully
[ ] UDP download completes successfully
[ ] Downloaded files are not corrupted
[ ] File sizes match original
[ ] Mode switching works without reconnect
[ ] Server handles multiple simultaneous clients
[ ] Disconnect cleanup works properly
[ ] Port reuse (SO_REUSEADDR) works on restart

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
