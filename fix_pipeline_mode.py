#!/usr/bin/env python3
"""Fix pipeline mode if it's None."""

from ingestion.database.models_db import PipelineModel, PipelineMode
from ingestion.database.session import get_db

PIPELINE_ID = "3b06bbae-2bbc-4526-ad6f-4e5d12c14f04"

db = next(get_db())
p = db.query(PipelineModel).filter_by(id=PIPELINE_ID).first()

if p:
    print(f"Current pipeline mode: {p.mode}")
    print(f"Mode value: {p.mode.value if p.mode else 'None'}")
    
    if p.mode != PipelineMode.FULL_LOAD_AND_CDC:
        print("Updating mode to FULL_LOAD_AND_CDC...")
        p.mode = PipelineMode.FULL_LOAD_AND_CDC
        db.commit()
        print("✓ Mode updated to FULL_LOAD_AND_CDC")
    else:
        print("✓ Mode is already FULL_LOAD_AND_CDC")
else:
    print(f"✗ Pipeline {PIPELINE_ID} not found")

db.close()

