"""
Consolidated Differential Diagnosis Dictionary for Medical Imaging

This module imports and merges the advanced differential diagnosis dictionaries
from Radiology, Oncology, and Cardiology, along with evidence-based guidelines,
into a single comprehensive resource. If a module or attribute is missing,
it falls back to an empty dictionary, ensuring the application can still start.
"""

import logging

logger = logging.getLogger(__name__)

# Attempt to import the radiology differentials
try:
    from radiology_differentials import radiology_differentials as radio_diff
except ImportError as e:
    logger.error(f"Could not import 'radiology_differentials': {e}")
    radio_diff = {}
except AttributeError as e:
    logger.error(f"'radiology_differentials' module does not define the expected attribute: {e}")
    radio_diff = {}

# Attempt to import the oncology differentials
try:
    from oncology_differentials import oncology_differentials
except ImportError as e:
    logger.error(f"Could not import 'oncology_differentials': {e}")
    oncology_differentials = {}
except AttributeError as e:
    logger.error(f"'oncology_differentials' module does not define the expected attribute: {e}")
    oncology_differentials = {}

# Attempt to import the cardiology differentials
try:
    from cardiology_differentials import cardiology_differentials
except ImportError as e:
    logger.error(f"Could not import 'cardiology_differentials': {e}")
    cardiology_differentials = {}
except AttributeError as e:
    logger.error(f"'cardiology_differentials' module does not define the expected attribute: {e}")
    cardiology_differentials = {}

# Attempt to import the evidence-based guidelines
try:
    from evidence_based_guidelines import evidence_based_guidelines
except ImportError as e:
    logger.error(f"Could not import 'evidence_based_guidelines': {e}")
    evidence_based_guidelines = {}
except AttributeError as e:
    logger.error(f"'evidence_based_guidelines' module does not define the expected attribute: {e}")
    evidence_based_guidelines = {}

# Consolidate all dictionaries into a single resource
medical_differentials = {
    "Radiology":  radiology_differentials,
    "Oncology": oncology_differentials,
    "Cardiology": cardiology_differentials,
    "Guidelines": evidence_based_guidelines,
}
