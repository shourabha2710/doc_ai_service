from pydantic import BaseModel
from typing import Optional, Dict, Any

class AadhaarFields(BaseModel):
    aadhaar_number: Optional[str] = None
    dob: Optional[str] = None

class PanFields(BaseModel):
    name: Optional[str] = None
    father_name: Optional[str] = None
    dob: Optional[str] = None
    pan_number: Optional[str] = None

class PassportFields(BaseModel):
    passport_number: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    nationality: Optional[str] = None

class DLFields(BaseModel):
    dl_number: Optional[str] = None
    name: Optional[str] = None
    dob: Optional[str] = None
    expiry_date: Optional[str] = None

class VoterIDFields(BaseModel):
    voter_id: Optional[str] = None
    name: Optional[str] = None
    father_name: Optional[str] = None
    dob: Optional[str] = None

class ExtractionResult(BaseModel):
    status: str
    blur_score: Optional[float] = None
    rotation_angle: Optional[int] = None
    document_cropped: Optional[bool] = None
    qr_data: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    aadhaar_fields: Optional[AadhaarFields] = None
    pan_fields: Optional[PanFields] = None
    passport_fields: Optional[PassportFields] = None
    dl_fields: Optional[DLFields] = None
    voterid_fields: Optional[VoterIDFields] = None
    document_type: Optional[str] = None
    reason: Optional[str] = None  # for failure cases