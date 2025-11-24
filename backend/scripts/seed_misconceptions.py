"""Seed misconceptions database from JSON files."""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database.connection import SessionLocal
from app.database.models import Misconception


def load_misconceptions_from_json():
    """Load misconceptions from JSON files and insert into database."""
    db = SessionLocal()
    
    try:
        misconceptions_dir = Path(__file__).parent.parent.parent / "data" / "misconceptions"
        
        if not misconceptions_dir.exists():
            print(f"Misconceptions directory not found: {misconceptions_dir}")
            return
        
        count = 0
        for json_file in misconceptions_dir.glob("*.json"):
            try:
                with open(json_file, "r") as f:
                    data = json.load(f)
                    topic = data.get("topic", json_file.stem)
                    subject = data.get("subject")
                    year_level_range = data.get("year_level_range")
                    
                    for mc_data in data.get("misconceptions", []):
                        # Check if already exists
                        existing = db.query(Misconception).filter_by(
                            topic=topic,
                            misconception=mc_data.get("misconception", "")
                        ).first()
                        
                        if not existing:
                            misconception = Misconception(
                                topic=topic,
                                misconception=mc_data.get("misconception", ""),
                                correction=mc_data.get("correction", ""),
                                subject=subject,
                                year_level_range=year_level_range,
                                metadata=mc_data,
                            )
                            db.add(misconception)
                            count += 1
                
                print(f"Processed {json_file.name}")
            except Exception as e:
                print(f"Error processing {json_file}: {str(e)}")
        
        db.commit()
        print(f"Inserted {count} new misconceptions into database")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding misconceptions: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    load_misconceptions_from_json()


