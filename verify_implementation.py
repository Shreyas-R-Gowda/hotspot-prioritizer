
import sys
import os

# Add paths to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'ai_service'))

def test_models():
    print("Testing Models...")
    try:
        from backend.app.models import Report
        r = Report(title="Test", road_importance=5)
        print(f"✅ Report model has road_importance: {r.road_importance}")
    except Exception as e:
        print(f"❌ Model Error: {e}")

def test_ai_logic():
    print("\nTesting AI Logic...")
    try:
        import ai_service.logic as logic
        # Manhole (637) -> Pothole
        cat = logic.get_predicted_category(637)
        print(f"✅ Class 637 (Manhole) category: {cat}")
        assert cat == "Pothole"
        
        # Trashmap (412) -> Garbage
        cat = logic.get_predicted_category(412)
        print(f"✅ Class 412 (Trash Can) category: {cat}")
        assert cat == "Garbage"
        
    except ImportError:
        print("❌ Could not import ai_service.logic")
    except AssertionError as e:
        print(f"❌ AI Logic Assertion Error: {e}")
    except Exception as e:
        print(f"❌ AI Logic Error: {e}")

def test_nlp():
    print("\nTesting NLP Duplicate Detection...")
    try:
        # Mock DB session
        class MockReport:
            def __init__(self, id, desc):
                self.report_id = id
                self.description = desc
                self.title = "Test"
        
        class MockQuery:
            def filter(self, *args): return self
            def order_by(self, *args): return self
            def limit(self, *args): return self
            def all(self):
                return [
                    MockReport(1, "There is a big pothole on Main St"),
                    MockReport(2, "Garbage pile near the park"),
                    MockReport(3, "Deep pothole in the middle of Main Street")
                ]

        class MockSession:
            def query(self, model): return MockQuery()

        from backend.app.ml.duplicates import check_duplicate
        
        db = MockSession()
        # Test with similar description
        duplicates = check_duplicate(db, "Big pothole on Main Street")
        
        print(f"✅ Duplicates found: {len(duplicates)}")
        if len(duplicates) > 0:
            print(f"   Top match: {duplicates[0]['title']} (Sim: {duplicates[0]['similarity']})")
            # Should match report 1 or 3 high
        
    except ImportError:
         print("❌ Could not import backend.app.ml.duplicates (scikit-learn missing?)")
    except Exception as e:
        print(f"❌ NLP Error: {e}")

if __name__ == "__main__":
    test_models()
    test_ai_logic()
    test_nlp()
