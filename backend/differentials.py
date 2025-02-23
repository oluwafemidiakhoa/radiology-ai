# differentials.py
"""
Consolidated Differential Diagnosis Dictionary for Medical Imaging

This module imports and merges the advanced differential diagnosis dictionaries from Radiology,
Oncology, and Cardiology, along with evidence-based guidelines, into a single comprehensive resource.
"""

try:
    from radiology_differentials import radiology_differentials
except ImportError:
    radiology_differentials = {}

try:
    from oncology_differentials import oncology_differentials
except ImportError:
    oncology_differentials = {}

try:
    from cardiology_differentials import cardiology_differentials
except ImportError:
    cardiology_differentials = {}

try:
    from evidence_based_guidelines import evidence_based_guidelines
except ImportError:
    evidence_based_guidelines = {}

medical_differentials = {
    "Radiology": radiology_differentials,
    "Oncology": oncology_differentials,
    "Cardiology": cardiology_differentials,
}
