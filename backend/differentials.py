"""
Consolidated Differential Diagnosis Dictionary for Medical Imaging (Enterprise Version)

This module merges advanced differential diagnosis dictionaries from Radiology, Oncology,
and Cardiology, as well as evidence-based guidelines, into a cohesive resource.
It is specifically designed to support large-scale clinical analytics and AI-driven
diagnostics across the three primary specialties:
  - Radiology
  - Cardiology
  - Oncology

Usage:
- The main AI analysis pipeline imports and references `medical_differentials`
  to incorporate domain-specific differentials and guidelines.
- Each specialty’s dictionary can be extended or replaced with new or updated
  content as medical knowledge evolves.
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

# Consolidated medical differentials and guidelines dictionary.
# This is used by the main AI pipeline to provide specialty-specific
# differential diagnoses and reference guidelines.
medical_differentials = {
    "Radiology": radiology_differentials,
    "Oncology": oncology_differentials,
    "Cardiology": cardiology_differentials,
    "Guidelines": evidence_based_guidelines,
}
