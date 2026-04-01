from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class AadhaarFields(BaseModel):
    aadhaar_number: Optional[str] = Field(
        default=None,
        description="12 digit Aadhaar number"
    )

    dob: Optional[str] = Field(
        default=None,
        description="Date of birth extracted from Aadhaar"
    )


class PanFields(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Name on PAN card"
    )

    father_name: Optional[str] = Field(
        default=None,
        description="Father name on PAN card"
    )

    dob: Optional[str] = Field(
        default=None,
        description="Date of birth on PAN card"
    )

    pan_number: Optional[str] = Field(
        default=None,
        description="PAN number (e.g. ABCDE1234F)"
    )


class PassportFields(BaseModel):
    passport_number: Optional[str] = Field(
        default=None,
        description="Passport number"
    )

    name: Optional[str] = Field(
        default=None,
        description="Passport holder name"
    )

    dob: Optional[str] = Field(
        default=None,
        description="Date of birth"
    )

    nationality: Optional[str] = Field(
        default=None,
        description="Nationality"
    )


class DLFields(BaseModel):
    dl_number: Optional[str] = Field(
        default=None,
        description="Driving License number"
    )

    name: Optional[str] = Field(
        default=None,
        description="License holder name"
    )

    dob: Optional[str] = Field(
        default=None,
        description="Date of birth"
    )

    expiry_date: Optional[str] = Field(
        default=None,
        description="License expiry date"
    )


class VoterIDFields(BaseModel):
    voter_id: Optional[str] = Field(
        default=None,
        description="Voter ID number"
    )

    name: Optional[str] = Field(
        default=None,
        description="Voter name"
    )

    father_name: Optional[str] = Field(
        default=None,
        description="Father name"
    )

    dob: Optional[str] = Field(
        default=None,
        description="Date of birth"
    )


class ExtractionResult(BaseModel):
    status: str = Field(
        description="Processing status (success / failed / error)"
    )

    blur_score: Optional[float] = Field(
        default=None,
        description="Blur detection score"
    )

    rotation_angle: Optional[int] = Field(
        default=None,
        description="Image rotation angle applied"
    )

    document_cropped: Optional[bool] = Field(
        default=None,
        description="Whether document edge detection cropped the image"
    )

    qr_data: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Decoded QR data if QR code detected"
    )

    raw_text: Optional[str] = Field(
        default=None,
        description="Raw OCR extracted text"
    )

    aadhaar_fields: Optional[AadhaarFields] = None
    pan_fields: Optional[PanFields] = None
    passport_fields: Optional[PassportFields] = None
    dl_fields: Optional[DLFields] = None
    voterid_fields: Optional[VoterIDFields] = None

    document_type: Optional[str] = Field(
        default=None,
        description="Detected document type"
    )

    reason: Optional[str] = Field(
        default=None,
        description="Failure reason if status is failed"
    )

    class Config:
        extra = "ignore"