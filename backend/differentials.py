"""
Consolidated Differential Diagnosis Dictionary for Medical Imaging

This module imports and merges the advanced differential diagnosis dictionaries
from Radiology, Oncology, and Cardiology, along with evidence-based guidelines,
into a single comprehensive resource.
"""

import logging

logger = logging.getLogger(__name__)

# Import Radiology differentials
try:
    from radiology_differentials import radiology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Error importing 'radiology_differentials': {e}")
    radiology_differentials = {}

# Import Oncology differentials
try:
    from oncology_differentials import oncology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Error importing 'oncology_differentials': {e}")
    oncology_differentials = {}

# Import Cardiology differentials
try:
    from cardiology_differentials import cardiology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Error importing 'cardiology_differentials': {e}")
    cardiology_differentials = {}

# Import Evidence-based guidelines
try:
    from evidence_based_guidelines import evidence_based_guidelines
except (ImportError, AttributeError) as e:
    logger.error(f"Error importing 'evidence_based_guidelines': {e}")
    evidence_based_guidelines = {}

# Consolidate all into a single dictionary
medical_differentials = {
    "Radiology": radiology_differentials,
    "Oncology": oncology_differentials,
    "Cardiology": cardiology_differentials,
    "Guidelines": evidence_based_guidelines,
}
