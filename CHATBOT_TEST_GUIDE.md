# AI Chatbot Browser UI Test Guide

## Prerequisites
- Frontend running at: http://localhost:3000
- Backend running at: http://localhost:8000
- Groq API key configured

## Step-by-Step Browser Testing

### 1. Register & Login
```
URL: http://localhost:3000
1. Click "Register" or navigate to /register
2. Enter:
   - Email: test.user@example.com
   - Password: TestPass123
3. Click Register
4. You'll be redirected to login
5. Login with the same credentials
6. You'll be redirected to /dashboard
```

### 2. Open AI Chatbot
```
1. On dashboard, look for BOTTOM-LEFT corner
2. You should see a FLOATING SPARKLES BUTTON (✨)
3. Click the button to open chat drawer
4. Chat sidebar slides in from the right
```

### 3. Test English Query
```
Chat Input: "Show my tasks"

Expected:
- AI Response appears: Message about tasks
- No blank bubbles
- "✓ Message is displayed" in chat
```

### 4. Test Roman Urdu Query
```
Chat Input: "Mere kitne tasks baaki hain?"

Expected:
- AI responds in Roman Urdu/Hinglish
- Example: "Aap ke 0 tasks baaki hain..."
- Natural conversational tone
```

### 5. Test Task Creation
```
Chat Input: "Add task: Exercise for 30 minutes"

Expected:
1. Chat shows AI response (e.g., "Theek hai, task add kar diya!")
2. Toast notification: "Task Added" appears (top-right, 2 sec)
3. NO blank chat bubbles
4. Console shows: "Tasks updated via AI: {action: 'add_task'}"
5. Task appears in main task list immediately
6. Refresh page - task still exists (persisted)
```

### 6. Test Task Listing
```
Chat Input: "Show my tasks" or "Mere tasks dikha do"

Expected:
- AI responds with task count
- No toast for read-only operation
- Messages are clear and in proper language
```

### 7. Test Entity Mapping (Advanced)
```
Chat Input: "Task add karo: Meeting with Ali sham 5 baje"

Expected:
- Title extracted: "Meeting with Ali"
- Description extracted: "sham 5 baje"
- Task created with both fields populated
```

### 8. Test Blank Message Fix
```
Chat Input: Any message that might cause AI to stall

Expected:
- If AI takes too long or times out
- Fallback message appears: "Ji, main samajh nahi paya. Dobara bolye ga?"
- No blank bubbles ever appear
```

### 9. Check Browser Console
```
Press F12 to open DevTools
Go to Console tab

Expected logs:
- "AI Response: {message: '...', action_taken: 'add_task', ...}"
- "Tasks updated via AI: {action: 'add_task'}"
- No error messages (unless network issues)
```

### 10. Check Network Activity
```
Press F12 > Network tab
Send a chat message

Expected requests:
1. POST /api/ai/chat (Response: 200, has 'message' field)
2. GET /api/tasks (Auto-triggered if add_task)
3. Response shows: {message: "...", action_taken: "add_task", ...}

✓ Never show empty 'message' field
✓ Always has content
```

## Test Scenarios Summary

| Test | Input | Expected Result | Status |
|------|-------|-----------------|--------|
| 1 | "Show my tasks" | English response, no blank | ✓ |
| 2 | "Mere tasks dikha do" | Roman Urdu response | ✓ |
| 3 | "Add task: Work out 1hr" | Task added, toast shown | ✓ |
| 4 | "Meeting add karo 5pm" | Toast "Task Added", no blank | ✓ |
| 5 | Stalled query | Fallback message shown | ✓ |
| 6 | Console check | Logs visible, no errors | ✓ |
| 7 | Network check | All requests 200 OK | ✓ |
| 8 | Task sync | New task in list immediately | ✓ |
| 9 | Refresh | Tasks persist | ✓ |
| 10 | Multiple queries | All have messages | ✓ |

## Troubleshooting

### Chatbot button not visible?
- Check browser console (F12) for JS errors
- Verify frontend is running: http://localhost:3000
- Hard refresh: Ctrl+Shift+R

### Messages appear blank?
- Check console for "Empty message from AI, using fallback"
- Check Network tab to see full response
- Backend should always return message field

### Tasks not appearing?
- Check if toast "Task Added" appears
- Manual refresh should show new task
- Check browser console for "Tasks updated via AI" event

### API errors?
- Check backend is running: http://localhost:8000/api/health
- Verify Groq API key is set
- Check backend logs for errors

## Quick Checklist ✓
- [ ] Frontend loads at http://localhost:3000
- [ ] Can login/register
- [ ] Chat button visible in bottom-left
- [ ] Chat drawer opens with animation
- [ ] Can send English messages
- [ ] Can send Roman Urdu messages
- [ ] No blank chat bubbles ever
- [ ] Tasks created via AI appear in list
- [ ] Toast notifications work
- [ ] Console shows proper logs
- [ ] Network requests all 200 OK
- [ ] Tasks persist after refresh

