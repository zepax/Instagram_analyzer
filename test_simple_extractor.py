#!/usr/bin/env python3
"""Simple test to verify the extractor imports and basic functionality."""

import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all imports work correctly."""
    print("🔍 Testing imports...")
    
    try:
        from instagram_analyzer.extractors.conversation_extractor import ConversationExtractor
        print("✅ ConversationExtractor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ConversationExtractor: {e}")
        return False
    
    try:
        from instagram_analyzer.extractors.conversation_extractor import quick_extract_top_conversations
        print("✅ quick_extract_top_conversations imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import quick_extract_top_conversations: {e}")
        return False
    
    try:
        from instagram_analyzer.extractors.conversation_extractor import ConversationIterator
        print("✅ ConversationIterator imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ConversationIterator: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality without full dependencies."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test that we can create an extractor instance
        from instagram_analyzer.extractors.conversation_extractor import ConversationExtractor
        
        data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
        extractor = ConversationExtractor(data_root, max_workers=2)
        
        print("✅ ConversationExtractor instance created successfully")
        
        # Test filter setting
        extractor.set_filters(min_messages=5, exclude_empty=True)
        print("✅ Filters set successfully")
        
        # Test file discovery (without processing)
        inbox_dir = data_root / 'your_instagram_activity' / 'messages' / 'inbox'
        if inbox_dir.exists():
            conversation_files = extractor._discover_conversation_files(inbox_dir)
            print(f"✅ Found {len(conversation_files)} conversation files")
        else:
            print(f"⚠️ Inbox directory not found: {inbox_dir}")
        
        # Test statistics (empty state)
        stats = extractor.get_extraction_statistics()
        print(f"✅ Got extraction statistics: {len(stats)} metrics")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_privacy_utils():
    """Test privacy utilities."""
    print("\n🔒 Testing privacy utilities...")
    
    try:
        from instagram_analyzer.utils.privacy_utils import anonymize_conversation_data
        print("✅ anonymize_conversation_data imported successfully")
        
        # Create a mock conversation object for testing
        class MockConversation:
            def __init__(self):
                self.title = "Chat with John Doe"
                self.participants = [MockParticipant("John Doe", False), MockParticipant("Flora Escobar", True)]
                self.messages = [MockMessage("John Doe", "Hello there!")]
                self.raw_data = {"test": "data"}
                self.anonymization_applied = False
        
        class MockParticipant:
            def __init__(self, name, is_self):
                self.name = name
                self.is_self = is_self
                self.username = name.lower().replace(" ", "")
        
        class MockMessage:
            def __init__(self, sender, content):
                self.sender_name = sender
                self.content = content
        
        # Test anonymization
        mock_conv = MockConversation()
        anonymized = anonymize_conversation_data(mock_conv)
        
        print(f"✅ Anonymization test completed")
        print(f"   Original title: {mock_conv.title}")
        print(f"   Anonymized title: {anonymized.title}")
        
        return True
        
    except Exception as e:
        print(f"❌ Privacy utils test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Enhanced Conversation Extractor - Simple Tests")
    print("=" * 60)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test basic functionality
    if not test_basic_functionality():
        success = False
    
    # Test privacy utils
    if not test_privacy_utils():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL TESTS PASSED - Enhanced Extractor is ready to use!")
        print("\n💡 Next steps:")
        print("   1. Install dependencies: poetry install")
        print("   2. Run full test: poetry run python test_enhanced_extractor.py")
        print("   3. Use the extractor in your code")
    else:
        print("❌ SOME TESTS FAILED - Check the errors above")
    
    print("=" * 60)

if __name__ == "__main__":
    main()