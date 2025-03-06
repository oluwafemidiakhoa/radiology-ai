"""
Evidence-based Clinical Guidelines for Medical Imaging, Cardiology, and Oncology (Updated)

This module provides concise summaries of key clinical guidelines from:
- ACR (radiology/imaging)
- ESC (cardiology)
- NCCN (oncology)

Guidelines for imaging have been reorganized by modality to support targeted application in an AI-driven diagnostic environment.
Always consult the latest official guidelines for comprehensive clinical practice.
"""

from typing import Dict, Any

# Define modality-specific imaging guidelines and other clinical guidelines.
evidence_based_guidelines: Dict[str, Any] = {
    # Modality-specific imaging guidelines:
    "ChestXRay": {
        "ACR_ChestXRay": {
            "NormalChest": "Follow standard screening intervals unless clinical suspicion arises.",
            "AbnormalChest": "If suspicious lesions are present, further evaluation with CT is recommended."
        }
    },
    "Mammogram": {
        "BI-RADS": {
            "Category 0": "Incomplete - additional imaging evaluation is required.",
            "Category 1": "Negative - routine screening is recommended.",
            "Category 2": "Benign findings - continue routine screening.",
            "Category 3": "Probably benign - short-interval follow-up (e.g., 6 months).",
            "Category 4A": "Low suspicion for malignancy - consider biopsy.",
            "Category 4B": "Intermediate suspicion for malignancy - biopsy recommended.",
            "Category 4C": "Moderate concern for malignancy - biopsy recommended.",
            "Category 5": "Highly suggestive of malignancy - prompt action required.",
            "Category 6": "Known biopsy-proven malignancy - manage appropriately."
        }
    },
    # General radiology protocols applicable across modalities
    "General_Radiology": {
        "CT_Protocols": [
            "Appropriate use of contrast vs. non-contrast CT",
            "Dose optimization per ALARA principle",
            "Patient screening for renal function if contrast is used"
        ],
        "MRI_Protocols": [
            "Screening for contraindications (e.g., pacemaker, certain implants)",
            "Use of gadolinium-based contrast agents with renal function assessment",
            "Tailoring pulse sequences to the suspected pathology"
        ]
    },
    # Cardiology guidelines remain under a dedicated key:
    "Cardiology": {
        "ESC": {
            "ACS": {
                "Diagnosis": [
                    "ECG",
                    "Cardiac biomarkers (troponin)",
                    "Coronary angiography"
                ],
                "Treatment": [
                    "Aspirin",
                    "P2Y12 inhibitors (Clopidogrel, Ticagrelor)",
                    "Heparin (LMWH or unfractionated)",
                    "Percutaneous coronary intervention (PCI)",
                    "CABG (if indicated)",
                    "Beta-blockers, ACE inhibitors, and Statins"
                ],
                "Risk Stratification": [
                    "GRACE score",
                    "TIMI risk score"
                ]
            },
            "PE": {
                "Diagnosis": [
                    "Wells Score",
                    "D-Dimer testing",
                    "CT Pulmonary Angiography (CTPA)",
                    "Ventilation/Perfusion (V/Q) scan"
                ],
                "Treatment": [
                    "Anticoagulation (LMWH, DOACs, or unfractionated heparin)",
                    "Thrombolysis (in massive or submassive PE with instability)",
                    "Surgical embolectomy (rarely used)",
                    "IVC filter (if anticoagulation is contraindicated)"
                ],
                "Prognosis": [
                    "Pulmonary Embolism Severity Index (PESI)",
                    "sPESI (simplified PESI)"
                ]
            },
            "Heart_Failure": {
                "Diagnosis": [
                    "Echocardiogram (assessment of ejection fraction)",
                    "BNP or NT-proBNP levels",
                    "Cardiac MRI if needed",
                    "Stress test for ischemic workup"
                ],
                "Treatment": [
                    "ACE inhibitors (or ARBs/ARNIs)",
                    "Beta-blockers",
                    "Diuretics (loop or thiazide)",
                    "Aldosterone antagonists",
                    "SGLT2 inhibitors (newer guideline recommendations)",
                    "ICD/CRT devices if indicated"
                ],
                "Follow-up": [
                    "Regular monitoring of volume status, electrolytes, and renal function",
                    "Optimization of guideline-directed medical therapy (GDMT)",
                    "Cardiac rehabilitation in selected patients"
                ]
            }
        }
    },
    # Oncology guidelines remain under a dedicated key:
    "Oncology": {
        "NCCN": {
            "Breast_Cancer": {
                "Screening": [
                    "Annual mammography (age and risk dependent)",
                    "Clinical breast exam",
                    "MRI for high-risk individuals"
                ],
                "Treatment": [
                    "Surgery (lumpectomy or mastectomy)",
                    "Radiation therapy",
                    "Chemotherapy",
                    "Hormone therapy (e.g., Tamoxifen, Aromatase Inhibitors)",
                    "Targeted therapy (e.g., HER2 inhibitors)",
                    "Immunotherapy (in selected cases)"
                ]
            },
            "Lung_Cancer": {
                "Screening": [
                    "Low-dose CT for high-risk smokers",
                    "Sputum cytology (limited utility)",
                    "Smoking cessation programs"
                ],
                "Treatment": [
                    "Surgical resection (for early-stage NSCLC)",
                    "Radiation therapy (curative or palliative)",
                    "Chemotherapy (platinum-based regimens)",
                    "Targeted therapy (EGFR, ALK inhibitors)",
                    "Immunotherapy (PD-1/PD-L1 inhibitors)"
                ]
            },
            "Colorectal_Cancer": {
                "Screening": [
                    "Colonoscopy every 10 years starting at age 45–50",
                    "FIT or FOBT yearly if colonoscopy is not performed",
                    "CT Colonography (every 5 years)"
                ],
                "Treatment": [
                    "Surgical resection of the primary tumor",
                    "Adjuvant chemotherapy (stage-dependent)",
                    "Radiation therapy (in rectal cancer settings)",
                    "Targeted therapy (e.g., anti-VEGF or anti-EGFR agents)"
                ]
            }
        }
    }
}


def get_guideline(organization: str, guideline_type: str) -> Any:
    """
    Retrieve the guideline data for a given organization and guideline type.

    Args:
        organization (str): The guideline organization (e.g., "ACR", "ESC", "NCCN", "ChestXRay", "Mammogram").
        guideline_type (str): The specific guideline type (e.g., "BI-RADS", "PE", "Breast_Cancer", "ACR_ChestXRay").

    Returns:
        Any: The guideline data (dictionary, list, or str) for the specified organization and type.

    Raises:
        KeyError: If the organization or guideline type is not found.
    """
    try:
        return evidence_based_guidelines[organization][guideline_type]
    except KeyError as e:
        raise KeyError(
            f"Guideline not found for organization '{organization}' and type '{guideline_type}'."
        ) from e


def list_guidelines(organization: str) -> Dict[str, Any]:
    """
    List all guideline types for a given organization.

    Args:
        organization (str): The guideline organization (e.g., "ACR", "ESC", "NCCN", "ChestXRay", "Mammogram").

    Returns:
        Dict[str, Any]: A dictionary mapping each guideline type to its data.

    Raises:
        KeyError: If the organization is not found.
    """
    try:
        return evidence_based_guidelines[organization]
    except KeyError as e:
        raise KeyError(
            f"No guidelines found for organization '{organization}'."
        ) from e
