# Windows Multiprocessing Fix

## Problem

When running the FastAPI backend with uvicorn's auto-reload feature on Windows, you may encounter an error:

```
File "C:\Users\...\platform.py", line 327, in _wmi_query
neo4j library fails during platform detection in multiprocessing context
```

This occurs because:
1. Uvicorn's auto-reload uses multiprocessing on Windows
2. When files change, uvicorn spawns a new process to reload the app
3. During the reload, neo4j library tries to detect Windows platform using WMI
4. WMI queries fail in the multiprocessing spawn context

## Solution

We've implemented multiple fixes to resolve this issue:

### 1. Platform Fix Module (`platform_fix.py`)

This module pre-caches platform information before multiprocessing occurs, avoiding WMI queries in child processes.

### 2. Updated `main.py`

Now imports the platform fix first, before any other imports that might trigger platform detection.

### 3. Development Scripts

- **`run.py`**: Python script for running with auto-reload
- **`start.bat`**: Windows batch file for easy startup

## How to Use

### Option 1: Use the Batch File (Easiest)

```bash
cd backend
start.bat
```

### Option 2: Use the Python Script

```bash
cd backend
python run.py
```

### Option 3: Use Uvicorn Directly

```bash
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --reload-dir .
```

### Option 4: No Auto-Reload (Production)

```bash
cd backend
python main.py
```

## Testing the Fix

After starting the server with one of the methods above:

1. Make a small change to any `.py` file in the backend directory
2. Save the file
3. The server should reload without errors

You should see:
```
WARNING: WatchFiles detected changes in 'filename.py'. Reloading...
INFO: Application startup complete.
```

Instead of the previous multiprocessing error.

## Additional Notes

- The platform fix only applies when modules are imported (not when running directly)
- If you still encounter issues, try using production mode without auto-reload
- The fix is Windows-specific and won't affect Linux/Mac systems

## Files Modified

- `main.py` - Added platform_fix import
- `platform_fix.py` - NEW: Platform detection fix
- `run.py` - NEW: Development server startup script
- `start.bat` - NEW: Windows batch file for easy startup
- `README.md` - Updated with Windows-specific instructions

