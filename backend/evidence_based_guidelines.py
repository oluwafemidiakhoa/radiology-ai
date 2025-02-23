# evidence_based_guidelines.py
"""
Evidence-based Clinical Guidelines for Medical Imaging

This module provides concise summaries of key clinical guidelines from ACR, ESC, and NCCN.
These guidelines support evidence-based decision making in AI diagnostic systems.
Always refer to the latest published guidelines for clinical practice.
"""

evidence_based_guidelines = {
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
