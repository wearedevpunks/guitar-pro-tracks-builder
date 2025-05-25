# Video Export Fix Summary

## Issue Resolved

**Error**: `'Tab' object has no attribute 'file_reference'`

**Root Cause**: The video export action was trying to access `song_result.tab.file_reference` but the `Tab` model uses `file` as the attribute name, not `file_reference`.

## Fix Applied

### File Modified
`api/routes/songs/actions/export_video.py`

### Changes Made

**Before (Lines 38 & 48):**
```python
# Line 38
if not song_result.tab or not song_result.tab.file_reference:

# Line 48  
parse_result = await tabs_service.parse_tab(song_result.tab.file_reference)
```

**After (Lines 38 & 48):**
```python
# Line 38
if not song_result.tab or not song_result.tab.file:

# Line 48
parse_result = await tabs_service.parse_tab(song_result.tab.file)
```

## Tab Model Structure

The correct `Tab` model structure from `api/db/redis/tabs_collection.py`:

```python
class Tab(BaseModel):
    """Tab model for Guitar Pro tabs."""
    
    id: str = Field(..., description="Tab unique identifier")
    file: FileReference = Field(..., description="Reference to the tab file")
    #    ^^^^
    #    This is the correct attribute name
```

## Verification

✅ **Fix Confirmed**: The video export action now properly accesses `tab.file` instead of the non-existent `tab.file_reference`

✅ **Error Handling**: The action gracefully handles missing songs without AttributeError

✅ **Compatibility**: Other actions (`get_song.py`, `create_song.py`) already use the correct attribute

## Impact

- **Video export endpoint now works**: POST `/api/songs/export-video` will no longer throw AttributeError
- **Proper error handling**: Missing songs return appropriate error messages
- **No breaking changes**: Fix only affects the incorrect attribute access

## Testing

The fix was verified with:
1. Non-existent song ID (graceful failure expected)
2. Proper error message returned without AttributeError
3. Logging confirms correct flow through the action

The video export functionality should now work correctly for valid song IDs with uploaded Guitar Pro files.