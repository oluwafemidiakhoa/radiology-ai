"""
Evidence-based Clinical Guidelines for Medical Imaging

This module provides concise summaries of key clinical guidelines from ACR, ESC, and NCCN.
These guidelines support evidence-based decision making in AI diagnostic systems.
Always refer to the latest published guidelines for clinical practice.
"""

from typing import Dict, Any

# Define the guidelines using nested dictionaries.
evidence_based_guidelines: Dict[str, Any] = {
    "ACR": {
        "LungRADS": {
            "Category 1": "No significant findings - routine follow-up",
            "Category 2": "Benign appearance - 12 month follow-up",
            "Category 3": "Probably benign - short-interval follow-up (e.g., 6 months)",
            "Category 4A": "Suspicious findings - consider biopsy",
            "Category 4B": "Highly suspicious findings - biopsy recommended",
            "Category 4X": "Highly suspicious findings with additional features - biopsy mandatory"
        },
        "BI-RADS": {
            "Category 0": "Incomplete - need additional imaging evaluation",
            "Category 1": "Negative - routine screening",
            "Category 2": "Benign findings - routine screening",
            "Category 3": "Probably benign - short-interval follow-up (e.g., 6 months)",
            "Category 4A": "Low suspicion for malignancy - consider biopsy",
            "Category 4B": "Intermediate suspicion for malignancy - biopsy recommended",
            "Category 4C": "Moderate concern for malignancy - biopsy recommended",
            "Category 5": "Highly suggestive of malignancy - prompt action required",
            "Category 6": "Known biopsy-proven malignancy - appropriate management"
        }
    },
    "ESC": {
        "PE": {
            "Diagnosis": [
                "Wells Score",
                "D-Dimer testing",
                "CT Pulmonary Angiography (CTPA)",
                "Ventilation/Perfusion (V/Q) scan"
            ],
            "Treatment": [
                "Anticoagulation (LMWH, unfractionated heparin, DOACs)",
                "Thrombolysis (in severe cases)",
                "Embolectomy (rarely used)",
                "IVC filter (for contraindications)"
            ],
            "Prognosis": [
                "Pulmonary Embolism Severity Index (PESI)",
                "sPESI (simplified PESI)"
            ]
        },
        "ACS": {
            "Diagnosis": [
                "ECG",
                "Cardiac biomarkers (troponin)",
                "Coronary angiography"
            ],
            "Treatment": [
                "Aspirin",
                "Clopidogrel or ticagrelor",
                "Heparin",
                "PCI",
                "CABG",
                "Beta-blockers",
                "ACE inhibitors",
                "Statins"
            ]
        }
    },
    "NCCN": {
        "Breast Cancer": {
            "Screening": [
                "Mammography",
                "Clinical breast exam",
                "Self-breast exam",
                "MRI (for high-risk individuals)"
            ],
            "Treatment": [
                "Surgery (lumpectomy, mastectomy)",
                "Radiation therapy",
                "Chemotherapy",
                "Hormone therapy",
                "Targeted therapy",
                "Immunotherapy"
            ]
        }
    }
}


def get_guideline(organization: str, guideline_type: str) -> Any:
    """
    Retrieve the guideline data for a given organization and guideline type.

    Args:
        organization (str): The guideline organization (e.g., "ACR", "ESC", "NCCN").
        guideline_type (str): The specific guideline type (e.g., "LungRADS", "PE", "Breast Cancer").

    Returns:
        Any: The guideline data (either a dictionary or list) for the specified organization and type.

    Raises:
        KeyError: If the organization or guideline type is not found.
    """
    try:
        return evidence_based_guidelines[organization][guideline_type]
    except KeyError as e:
        raise KeyError(f"Guideline not found for organization '{organization}' and type '{guideline_type}'.") from e


def list_guidelines(organization: str) -> Dict[str, Any]:
    """
    List all guideline types for a given organization.

    Args:
        organization (str): The guideline organization (e.g., "ACR", "ESC", "NCCN").

    Returns:
        Dict[str, Any]: A dictionary mapping each guideline type to its data.

    Raises:
        KeyError: If the organization is not found.
    """
    try:
        return evidence_based_guidelines[organization]
    except KeyError as e:
        raise KeyError(f"No guidelines found for organization '{organization}'.") from e
