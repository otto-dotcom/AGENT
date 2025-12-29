#!/usr/bin/env python3
"""
HELIOS Setup Test Script
Test that all dependencies and configurations are working
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported"""
    print("Testing imports...")

    try:
        import selenium
        print("✓ selenium installed")
    except ImportError as e:
        print(f"✗ selenium not installed: {e}")
        return False

    try:
        import bs4
        print("✓ beautifulsoup4 installed")
    except ImportError as e:
        print(f"✗ beautifulsoup4 not installed: {e}")
        return False

    try:
        import pyairtable
        print("✓ pyairtable installed")
    except ImportError as e:
        print(f"✗ pyairtable not installed: {e}")
        return False

    try:
        import supabase
        print("✓ supabase installed")
    except ImportError as e:
        print(f"⚠ supabase not installed (optional): {e}")
        # Supabase is optional, don't fail the test
        pass

    try:
        import colorlog
        print("✓ colorlog installed")
    except ImportError as e:
        print(f"✗ colorlog not installed: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv installed")
    except ImportError as e:
        print(f"✗ python-dotenv not installed: {e}")
        return False

    return True


def test_selenium_driver():
    """Test that Selenium can initialize a Chrome driver"""
    print("\nTesting Selenium WebDriver...")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service

        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # Try with webdriver-manager first
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except:
            # Fallback to system driver
            driver = webdriver.Chrome(options=chrome_options)

        driver.get('https://www.google.com')

        if 'Google' in driver.title:
            print("✓ Selenium WebDriver working")
            driver.quit()
            return True
        else:
            print("✗ Selenium WebDriver loaded page but unexpected content")
            driver.quit()
            return False

    except Exception as e:
        print(f"✗ Selenium WebDriver failed: {e}")
        return False


def test_project_structure():
    """Test that project directories exist"""
    print("\nTesting project structure...")

    base_dir = Path(__file__).parent

    required_dirs = [
        'scrapers',
        'integrations',
        'config',
        'exports',
        'logs',
    ]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✓ {dir_name}/ exists")
        else:
            print(f"✗ {dir_name}/ missing")
            all_exist = False

    return all_exist


def test_env_file():
    """Test that .env.example exists"""
    print("\nTesting environment configuration...")

    base_dir = Path(__file__).parent
    env_example = base_dir / '.env.example'

    if env_example.exists():
        print("✓ .env.example exists")

        env_file = base_dir / '.env'
        if env_file.exists():
            print("✓ .env file exists")
        else:
            print("⚠ .env file not found (copy from .env.example)")

        return True
    else:
        print("✗ .env.example missing")
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("🌞 HELIOS Setup Test")
    print("="*60)

    tests = [
        ("Package Imports", test_imports),
        ("Project Structure", test_project_structure),
        ("Environment Config", test_env_file),
        ("Selenium WebDriver", test_selenium_driver),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {test_name}")

    print("="*60)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! HELIOS is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please fix issues above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
