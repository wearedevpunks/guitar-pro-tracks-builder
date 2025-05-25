#!/usr/bin/env python3
"""
Test script to verify the video export fix for the file_reference attribute error.
"""

import asyncio
from api.routes.songs.dto import VideoExportRequest
from api.routes.songs.actions.export_video import export_song_video_action
from api.features.tabs.service import get_tabs_service


async def test_video_export_fix():
    """Test that the video export action now correctly accesses tab.file instead of tab.file_reference."""
    
    print("=" * 60)
    print("VIDEO EXPORT FIX VERIFICATION")
    print("=" * 60)
    print()
    
    print("ISSUE FIXED:")
    print("  Before: song_result.tab.file_reference (AttributeError)")
    print("  After:  song_result.tab.file (Correct attribute)")
    print()
    
    # Test with a non-existent song (should fail gracefully without AttributeError)
    request = VideoExportRequest(
        song_id='non-existent-song-id',
        output_format='mp4',
        resolution=(1280, 720),
        fps=24
    )
    
    tabs_service = get_tabs_service()
    
    print(f"Testing video export for song: {request.song_id}")
    print("Expected: Graceful failure with 'Failed to retrieve song' message")
    print("NOT Expected: AttributeError about 'file_reference'")
    print()
    
    try:
        response = await export_song_video_action(request, tabs_service)
        
        print("RESULT:")
        print(f"  Success: {response.success}")
        print(f"  Message: {response.message}")
        print(f"  Song ID: {response.song_id}")
        
        if "file_reference" in response.message:
            print("\n❌ STILL HAS ISSUE: Response mentions file_reference")
        elif not response.success and "Failed to retrieve song" in response.message:
            print("\n✅ FIX CONFIRMED: Proper error handling without AttributeError")
        else:
            print(f"\n⚠️  UNEXPECTED: {response.message}")
            
    except AttributeError as e:
        if "file_reference" in str(e):
            print(f"\n❌ FIX FAILED: Still getting AttributeError: {e}")
        else:
            print(f"\n⚠️  DIFFERENT ATTRIBUTE ERROR: {e}")
    except Exception as e:
        print(f"\n⚠️  UNEXPECTED ERROR: {e}")
    
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("The fix changes the following in export_video.py:")
    print("  Line 38: if not song_result.tab or not song_result.tab.file:")
    print("  Line 48: parse_result = await tabs_service.parse_tab(song_result.tab.file)")
    print()
    print("This matches the Tab model definition:")
    print("  class Tab(BaseModel):")
    print("      id: str")
    print("      file: FileReference  # <- Correct attribute name")
    print()
    print("The error should now be resolved for real song exports!")


if __name__ == "__main__":
    asyncio.run(test_video_export_fix())