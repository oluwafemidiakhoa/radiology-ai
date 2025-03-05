"""
Consolidated Differential Diagnosis and Guidelines for Medical Imaging

This module consolidates the advanced differential diagnosis dictionaries from Radiology,
Oncology, and Cardiology, along with evidence-based guidelines, into a single comprehensive
resource for use in AI diagnostic systems. The merged dictionary enables unified access to
diagnostic criteria and guidelines.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

def safe_import(module_name: str, attribute: str) -> Any:
    """
    Safely import an attribute from a module. If the import fails, log the error and return an empty dict.
    
    Args:
        module_name (str): The name of the module to import.
        attribute (str): The attribute to retrieve from the module.
    
    Returns:
        Any: The imported attribute or an empty dict if the import fails.
    """
    try:
        module = __import__(module_name, fromlist=[attribute])
        return getattr(module, attribute)
    except ImportError as e:
        logger.error(f"Error importing {attribute} from {module_name}: {e}")
        return {}

radiology_differentials = safe_import("radiology_differentials", "radiology_differentials")
oncology_differentials = safe_import("oncology_differentials", "oncology_differentials")
cardiology_differentials = safe_import("cardiology_differentials", "cardiology_differentials")
evidence_based_guidelines = safe_import("evidence_based_guidelines", "evidence_based_guidelines")

medical_differentials: Dict[str, Any] = {
    "Radiology": radiology_differentials,
    "Oncology": oncology_differentials,
    "Cardiology": cardiology_differentials,
    "Guidelines": evidence_based_guidelines,
}
