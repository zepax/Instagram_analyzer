#!/usr/bin/env python3
"""Test script for the enhanced conversation extractor."""

from pathlib import Path
from datetime import datetime, timedelta
from instagram_analyzer.extractors.conversation_extractor import ConversationExtractor, quick_extract_top_conversations

def test_enhanced_extractor():
    """Test the enhanced conversation extractor functionality."""
    
    print("🚀 Testing Enhanced Conversation Extractor")
    print("=" * 60)
    
    # Setup
    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    
    # Initialize extractor
    print("\n📁 Initializing enhanced extractor...")
    extractor = ConversationExtractor(data_root, max_workers=4)
    
    # Test 1: Basic extraction with filters
    print("\n🔍 Test 1: Basic extraction with filters")
    extractor.set_filters(
        min_messages=5,
        exclude_empty=True
    )
    
    conversations = extractor.extract_all_conversations(parallel=True)
    print(f"✅ Extracted {len(conversations)} conversations with filters")
    
    # Show statistics
    stats = extractor.get_extraction_statistics()
    print(f"📊 Extraction stats:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   • {key}: {value:.2f}")
        else:
            print(f"   • {key}: {value}")
    
    # Test 2: Extract subset
    print("\n🎯 Test 2: Extract conversation subset")
    subset = extractor.extract_conversation_subset(limit=5, sample_random=False)
    print(f"✅ Extracted subset: {len(subset)} conversations")
    
    for i, conv in enumerate(subset, 1):
        print(f"   {i}. {conv.title[:40]}... ({len(conv.messages)} msgs)")
    
    # Test 3: Extract by criteria
    print("\n🔎 Test 3: Extract by criteria")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # Last year
    
    criteria_conversations = extractor.extract_conversations_by_criteria(
        date_range=(start_date, end_date),
        min_message_count=10
    )
    print(f"✅ Found {len(criteria_conversations)} conversations from last year with 10+ messages")
    
    # Test 4: Full extraction and analysis
    print("\n🧠 Test 4: Full extraction and analysis")
    export_path = Path("enhanced_analysis")
    
    conversations, analysis = extractor.extract_and_analyze(
        export_path=export_path,
        include_advanced_analytics=True,
        anonymize=False
    )
    
    print(f"✅ Complete analysis finished:")
    print(f"   • Conversations: {len(conversations)}")
    print(f"   • Total messages: {analysis.total_messages}")
    print(f"   • Unique contacts: {analysis.unique_contacts}")
    print(f"   • Date range: {analysis.date_range}")
    
    # Test 5: Quick utility function
    print("\n⚡ Test 5: Quick extraction utility")
    top_conversations = quick_extract_top_conversations(data_root, limit=3)
    print(f"✅ Top 3 most active conversations:")
    
    for i, conv in enumerate(top_conversations, 1):
        print(f"   {i}. {conv.title[:30]}... - {len(conv.messages)} messages")
    
    # Test 6: Performance comparison
    print("\n⏱️ Test 6: Performance comparison")
    
    # Sequential processing
    import time
    start_time = time.time()
    seq_conversations = extractor.extract_all_conversations(parallel=False)
    seq_time = time.time() - start_time
    
    # Parallel processing
    start_time = time.time()
    par_conversations = extractor.extract_all_conversations(parallel=True)
    par_time = time.time() - start_time
    
    print(f"📈 Performance results:")
    print(f"   • Sequential: {seq_time:.2f}s ({len(seq_conversations)} conversations)")
    print(f"   • Parallel: {par_time:.2f}s ({len(par_conversations)} conversations)")
    if seq_time > 0:
        speedup = seq_time / par_time
        print(f"   • Speedup: {speedup:.1f}x")
    
    return extractor, conversations, analysis

def test_conversation_iterator():
    """Test the conversation iterator for memory-efficient processing."""
    
    print("\n" + "=" * 60)
    print("🔄 Testing Conversation Iterator")
    print("=" * 60)
    
    from instagram_analyzer.extractors.conversation_extractor import ConversationIterator
    
    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    extractor = ConversationExtractor(data_root)
    
    # Create iterator
    iterator = ConversationIterator(extractor, batch_size=10)
    
    total_conversations = 0
    total_messages = 0
    batch_count = 0
    
    print("🔄 Processing conversations in batches...")
    
    for batch in iterator:
        batch_count += 1
        batch_conversations = len(batch)
        batch_messages = sum(len(conv.messages) for conv in batch)
        
        total_conversations += batch_conversations
        total_messages += batch_messages
        
        print(f"   Batch {batch_count}: {batch_conversations} conversations, {batch_messages} messages")
        
        # Stop after a few batches for demo
        if batch_count >= 3:
            break
    
    print(f"\n✅ Iterator test completed:")
    print(f"   • Processed {batch_count} batches")
    print(f"   • Total conversations: {total_conversations}")
    print(f"   • Total messages: {total_messages}")

def test_keyword_extraction():
    """Test keyword-based conversation extraction."""
    
    print("\n" + "=" * 60)
    print("🔍 Testing Keyword Extraction")
    print("=" * 60)
    
    from instagram_analyzer.extractors.conversation_extractor import extract_conversations_with_keywords
    
    data_root = Path("examples/instagram-florenescobar-2025-07-13-pcFuHXmB")
    
    # Test with common keywords
    keywords = ["gracias", "hola", "foto", "jaja"]
    
    print(f"🔍 Searching for conversations with keywords: {keywords}")
    
    matching_conversations = extract_conversations_with_keywords(data_root, keywords)
    
    print(f"✅ Found {len(matching_conversations)} conversations with keywords")
    
    # Show details for first few matches
    for i, conv in enumerate(matching_conversations[:5], 1):
        print(f"   {i}. {conv.title[:40]}... ({len(conv.messages)} messages)")
        
        # Show which keywords were found
        found_keywords = []
        for keyword in keywords:
            if any(msg.content and keyword.lower() in msg.content.lower() 
                   for msg in conv.messages if msg.content):
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"      Keywords found: {', '.join(found_keywords)}")

if __name__ == "__main__":
    try:
        # Run all tests
        extractor, conversations, analysis = test_enhanced_extractor()
        test_conversation_iterator()
        test_keyword_extraction()
        
        print("\n" + "=" * 60)
        print("✅ ALL ENHANCED EXTRACTOR TESTS COMPLETED")
        print("=" * 60)
        
        print("\n📊 Final Summary:")
        final_stats = extractor.get_extraction_statistics()
        print(f"   • Success rate: {final_stats.get('success_rate', 0):.1f}%")
        print(f"   • Processing speed: {final_stats.get('processing_rate_conversations_per_second', 0):.1f} conv/sec")
        print(f"   • Average messages per conversation: {final_stats.get('avg_messages_per_conversation', 0):.1f}")
        
        print("\n📁 Generated files:")
        print("   • enhanced_analysis/conversation_extraction_results.json")
        print("   • enhanced_analysis/conversations/ (sample conversations)")
        
        print("\n💡 New capabilities available:")
        print("   • Parallel processing for faster extraction")
        print("   • Advanced filtering and criteria-based extraction")
        print("   • Memory-efficient batch processing")
        print("   • Keyword-based conversation search")
        print("   • Performance monitoring and statistics")
        print("   • Enhanced anonymization options")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()