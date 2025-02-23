# differentials.py
"""
Consolidated Differential Diagnosis Dictionary for Medical Imaging

This module consolidates differential diagnosis dictionaries from Radiology, Oncology, and Cardiology.
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

medical_differentials = {
    "Radiology": radiology_differentials,
    "Oncology": oncology_differentials,
    "Cardiology": cardiology_differentials,
}
