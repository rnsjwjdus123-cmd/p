import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\user\Desktop\santokki\quiz\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# Find the submit handler and Firebase save code
print("=== SUBMIT HANDLER ===")
for i, line in enumerate(lines):
    s = line.strip()
    if any(kw in s for kw in ['btnSubmit', 'firebaseInitialized', 'db.collection', 'FIREBASE CHECK', 'quiz_results', 'resultData', 'try {', 'catch(err)']):
        print(f"L{i+1}: {s[:150]}")

# Find Firebase init
print("\n=== FIREBASE INIT ===")
for i, line in enumerate(lines):
    s = line.strip()
    if any(kw in s for kw in ['let firebaseInitialized', 'firebase.initializeApp', 'firebase.firestore', 'const db =', 'fallback mode', 'Firebase not initialized']):
        print(f"L{i+1}: {s[:150]}")

# Find subscriber_id handling
print("\n=== SUBSCRIBER ID ===")
for i, line in enumerate(lines):
    s = line.strip()
    if 'subscriberId' in s or 'subscriber_id' in s:
        print(f"L{i+1}: {s[:150]}")
        
# Check Q3 selectedSpace
print("\n=== SELECTED SPACE ===")
for i, line in enumerate(lines):
    s = line.strip()
    if 'selectedSpace' in s:
        print(f"L{i+1}: {s[:150]}")
