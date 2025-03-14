"""
Consolidated Differential Diagnosis Dictionary for Medical Imaging (Enterprise Version)

This module imports and merges advanced differential diagnosis dictionaries 
from Radiology, Oncology, and Cardiology, as well as evidence-based guidelines, 
into a cohesive resource that supports large-scale clinical analytics and AI-driven diagnostics.
"""

import logging

logger = logging.getLogger(__name__)

# Attempt to import Radiology differentials
try:
    from radiology_differentials import radiology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Failed to import 'radiology_differentials': {e}")
    radiology_differentials = {}

# Attempt to import Oncology differentials
try:
    from oncology_differentials import oncology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Failed to import 'oncology_differentials': {e}")
    oncology_differentials = {}

# Attempt to import Cardiology differentials
try:
    from cardiology_differentials import cardiology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Failed to import 'cardiology_differentials': {e}")
    cardiology_differentials = {}

# Attempt to import Evidence-based guidelines
try:
    from evidence_based_guidelines import evidence_based_guidelines
except (ImportError, AttributeError) as e:
    logger.error(f"Failed to import 'evidence_based_guidelines': {e}")
    evidence_based_guidelines = {}

# Consolidated medical differentials and guidelines
medical_differentials = {
    "Radiology": radiology_differentials,
    "Oncology": oncology_differentials,
    "Cardiology": cardiology_differentials,
    "Guidelines": evidence_based_guidelines,
}
