#!/usr/bin/env python3

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ecommerce_agent import EcommerceAnalysisAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_basic_initialization():
    print("=== Testing Basic Initialization ===")
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    
    try:
        agent = EcommerceAnalysisAgent(google_api_key=google_api_key)
        print("✅ Agent initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize agent: {e}")
        return False


def test_schema_retrieval():
    print("\n=== Testing Schema Retrieval ===")
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    try:
        agent = EcommerceAnalysisAgent(google_api_key=google_api_key)
        
        # Test single table schema
        schema = agent.get_schema_info("orders")
        if "orders" in schema and isinstance(schema["orders"], list):
            print(f"✅ Retrieved schema for orders table ({len(schema['orders'])} columns)")
        else:
            print("❌ Failed to retrieve orders schema")
            return False
        
        # Test all schemas
        all_schemas = agent.get_schema_info()
        if len(all_schemas) >= 4:  # Should have at least 4 tables
            print(f"✅ Retrieved schemas for {len(all_schemas)} tables")
        else:
            print(f"❌ Expected 4 tables, got {len(all_schemas)}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Schema retrieval test failed: {e}")
        return False


def test_simple_query():
    print("\n=== Testing Simple Query Analysis ===")
    
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ GOOGLE_API_KEY not found")
        return False
    
    try:
        agent = EcommerceAnalysisAgent(google_api_key=google_api_key)
        
        # Test with a simple query
        test_query = "Show me the top 5 products by total sales"
        
        print(f"Analyzing query: '{test_query}'")
        result = agent.analyze(test_query)
        
        # Check result structure
        if not result:
            print("❌ No result returned")
            return False
        
        if result.get("success"):
            print("✅ Query analysis completed successfully")
            print(f"   - Analysis type: {result.get('analysis_type')}")
            print(f"   - SQL generated: {'Yes' if result.get('generated_sql') else 'No'}")
            print(f"   - Results returned: {'Yes' if result.get('query_results') else 'No'}")
            print(f"   - Insights generated: {len(result.get('insights', []))}")
            
            if result.get("generated_sql"):
                print(f"   - SQL preview: {result['generated_sql'][:100]}...")
                
            return True
        else:
            print(f"❌ Query analysis failed: {result.get('error')}")
            print(f"   - Error count: {result.get('error_count', 0)}")
            return False
            
    except Exception as e:
        print(f"❌ Simple query test failed: {e}")
        logger.exception("Exception details:")
        return False


def test_cli_import():
    print("\n=== Testing CLI Module Import ===")
    
    try:
        from cli import EcommerceCLI
        cli = EcommerceCLI()
        print("✅ CLI module imported successfully")
        return True
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False


def run_all_tests():
    print("BigQuery E-commerce Agent Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Initialization", test_basic_initialization),
        ("Schema Retrieval", test_schema_retrieval), 
        ("Simple Query Analysis", test_simple_query),
        ("CLI Import", test_cli_import)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The system is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)