"""
Consolidated Differential Diagnosis Dictionary for Medical Imaging
"""

import logging

logger = logging.getLogger(__name__)

# Radiology
try:
    from radiology_differentials import radiology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Could not import 'radiology_differentials': {e}")
    radiology_differentials = {}

# Oncology
try:
    from oncology_differentials import oncology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Could not import 'oncology_differentials': {e}")
    oncology_differentials = {}

# Cardiology
try:
    from cardiology_differentials import cardiology_differentials
except (ImportError, AttributeError) as e:
    logger.error(f"Could not import 'cardiology_differentials': {e}")
    cardiology_differentials = {}

# Guidelines
try:
    from evidence_based_guidelines import evidence_based_guidelines
except (ImportError, AttributeError) as e:
    logger.error(f"Could not import 'evidence_based_guidelines': {e}")
    evidence_based_guidelines = {}

# Consolidate
medical_differentials = {
    "Radiology":  radiology_differentials,
    "Oncology":   oncology_differentials,
    "Cardiology": cardiology_differentials,
    "Guidelines": evidence_based_guidelines,
}
