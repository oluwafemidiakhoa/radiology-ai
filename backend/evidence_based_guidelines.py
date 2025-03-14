"""
Ultra-Advanced Evidence-based Clinical Guidelines for Medical Imaging, Cardiology, Oncology, and Histopathology (Updated)

This module provides concise, AI-ready guideline summaries sourced from:
  - ACR (radiology/imaging)
  - ESC (cardiology)
  - NCCN (oncology)
  - Histopathology (recently added)

Imaging guidelines are organized by modality for streamlined usage in AI-driven diagnostics. 
Additional domain-specific guidelines, such as Cardiology (ESC) and Oncology (NCCN), are 
embedded for end-to-end clinical coverage. 

Always consult the latest official publications for comprehensive practice recommendations.
"""

from typing import Dict, Any

###############################################################################
# Comprehensive Dictionary of Evidence-based Guidelines
###############################################################################
evidence_based_guidelines: Dict[str, Any] = {
    # Imaging guidelines by modality:
    "ChestXRay": {
        "ACR_ChestXRay": {
            "NormalChest": "Follow standard screening intervals unless clinical suspicion arises.",
            "AbnormalChest": "If suspicious lesions are present, further CT evaluation is recommended."
        }
    },
    "Mammogram": {
        "BI-RADS": {
            "Category 0": "Incomplete – additional imaging evaluation is required.",
            "Category 1": "Negative – routine screening is recommended.",
            "Category 2": "Benign findings – continue routine screening.",
            "Category 3": "Probably benign – short-interval follow-up (e.g., 6 months).",
            "Category 4A": "Low suspicion for malignancy – consider biopsy.",
            "Category 4B": "Intermediate suspicion for malignancy – biopsy recommended.",
            "Category 4C": "Moderate concern for malignancy – biopsy recommended.",
            "Category 5": "Highly suggestive of malignancy – prompt action required.",
            "Category 6": "Known biopsy-proven malignancy – manage appropriately."
        }
    },

    # Newly introduced Histopathology guidelines:
    "Histopathology": {
        "General_Pathology": {
            "Tissue_Processing": (
                "Standard formalin fixation and paraffin embedding. "
                "Adhere to CAP guidelines on specimen handling and labeling."
            ),
            "Microscopic_Evaluation": (
                "H&E-stained slides for cellular architecture, nuclear characteristics, "
                "and stromal alterations. Assess margins if applicable."
            ),
            "Immunohistochemistry": (
                "Employ ER, PR, HER2, Ki-67, or other markers based on suspected pathology. "
                "Incorporate molecular or genetic tests where indicated."
            ),
            "Reporting_Standards": (
                "Use standardized synoptic reporting for tumor type, grade, and stage. "
                "WHO classification and CAP protocols are recommended practice."
            )
        }
    },

    # General radiology protocols (trans-modality):
    "General_Radiology": {
        "CT_Protocols": [
            "Indications for contrast vs. non-contrast CT",
            "Dose optimization using ALARA principles",
            "Renal function screening if contrast is administered"
        ],
        "MRI_Protocols": [
            "Pre-scan screening for pacemakers or metallic implants",
            "Use gadolinium contrast with renal function assessment",
            "Customize pulse sequences for the suspected pathology"
        ]
    },

    # Cardiology (ESC) guidelines:
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
                    "CABG if indicated",
                    "Beta-blockers, ACE inhibitors, Statins"
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
                    "Thrombolysis in massive/submassive PE with instability",
                    "Surgical embolectomy (rare cases)",
                    "IVC filter (when anticoagulation is contraindicated)"
                ],
                "Prognosis": [
                    "Pulmonary Embolism Severity Index (PESI)",
                    "sPESI (simplified PESI)"
                ]
            },
            "Heart_Failure": {
                "Diagnosis": [
                    "Echocardiogram (determine ejection fraction)",
                    "BNP or NT-proBNP",
                    "Cardiac MRI if uncertain",
                    "Stress testing for ischemic evaluation"
                ],
                "Treatment": [
                    "ACE inhibitors (or ARBs/ARNIs)",
                    "Beta-blockers",
                    "Diuretics (loop or thiazide)",
                    "Aldosterone antagonists",
                    "SGLT2 inhibitors (newer guidelines)",
                    "ICD/CRT devices when indicated"
                ],
                "Follow-up": [
                    "Monitor volume status, electrolytes, renal function",
                    "Optimize guideline-directed medical therapy",
                    "Cardiac rehabilitation in select cases"
                ]
            }
        }
    },

    # Oncology (NCCN) guidelines:
    "Oncology": {
        "NCCN": {
            "Breast_Cancer": {
                "Screening": [
                    "Annual mammography (age- and risk-dependent)",
                    "Clinical breast exam",
                    "MRI for high-risk profiles"
                ],
                "Treatment": [
                    "Surgery (lumpectomy or mastectomy)",
                    "Radiation therapy",
                    "Chemotherapy",
                    "Hormone therapy (e.g., Tamoxifen, Aromatase Inhibitors)",
                    "Targeted therapy (e.g., HER2 inhibitors)",
                    "Immunotherapy (select cases)"
                ]
            },
            "Lung_Cancer": {
                "Screening": [
                    "Low-dose CT for high-risk smokers",
                    "Sputum cytology (limited utility)",
                    "Smoking cessation programs"
                ],
                "Treatment": [
                    "Surgical resection for early-stage NSCLC",
                    "Radiation (curative or palliative intent)",
                    "Chemotherapy (platinum-based regimens)",
                    "Targeted therapy (EGFR, ALK inhibitors)",
                    "Immunotherapy (PD-1/PD-L1 blockade)"
                ]
            },
            "Colorectal_Cancer": {
                "Screening": [
                    "Colonoscopy every 10 years (start age 45–50)",
                    "Fecal occult blood or FIT annually if colonoscopy not done",
                    "CT Colonography every 5 years"
                ],
                "Treatment": [
                    "Surgical resection of the primary lesion",
                    "Adjuvant chemotherapy (stage-specific)",
                    "Radiation therapy (especially rectal cancers)",
                    "Targeted therapy (e.g., anti-VEGF, anti-EGFR)"
                ]
            }
        }
    }
}


def get_guideline(organization: str, guideline_type: str) -> Any:
    """
    Retrieves guideline data (dictionary, list, or string) for a given organization and guideline type.

    Args:
        organization (str): Name of the guideline organization or imaging modality 
                           (e.g., "ACR", "ESC", "NCCN", "ChestXRay", "Mammogram", "Histopathology").
        guideline_type (str): Specific guideline type (e.g., "BI-RADS", "PE", "Breast_Cancer",
                              "ACR_ChestXRay", "General_Pathology").

    Returns:
        Any: Dictionary, list, or string containing the specified guideline data.

    Raises:
        KeyError: If the requested organization or guideline type is not recognized.
    """
    try:
        return evidence_based_guidelines[organization][guideline_type]
    except KeyError as e:
        raise KeyError(
            f"Guideline not found for organization '{organization}' and type '{guideline_type}'."
        ) from e


def list_guidelines(organization: str) -> Dict[str, Any]:
    """
    Lists all guideline types under a given organization or modality.

    Args:
        organization (str): The organization or modality key (e.g., "ACR", "ESC", "NCCN",
                           "ChestXRay", "Mammogram", "Histopathology").

    Returns:
        Dict[str, Any]: A dictionary mapping each guideline type to its data.

    Raises:
        KeyError: If the provided organization is not found.
    """
    try:
        return evidence_based_guidelines[organization]
    except KeyError as e:
        raise KeyError(
            f"No guidelines found for organization '{organization}'."
        ) from e
