# test/test_pipeline.py

import os
from app.pipeline.document_pipeline import process_document

# Path to test images
TEST_FOLDER = "test"
images = [f for f in os.listdir(TEST_FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

for img_file in images:
    img_path = os.path.join(TEST_FOLDER, img_file)
    print(f"\nProcessing file: {img_path}")
    
    result = process_document(img_path)
    
    print("=== Extraction Result ===")
    print(f"Status: {result.status}")
    print(f"Document Type: {result.document_type}")
    print(f"Blur Score: {result.blur_score}")
    print(f"Rotation Angle: {result.rotation_angle}")
    print(f"Aadhaar Fields: {result.aadhaar_fields}")
    print(f"PAN Fields: {result.pan_fields}")
    print(f"Passport Fields: {result.passport_fields}")
    print(f"DL Fields: {result.dl_fields}")
    print(f"VoterID Fields: {result.voterid_fields}")
    print(f"QR Data: {result.qr_data}")
    print(f"Raw Text Snippet: {result.raw_text[:200]}...\n")