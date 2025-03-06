"""
Advanced Oncology Differential Diagnosis Module

This module defines a structured representation of advanced oncology differential diagnoses
using Python dataclasses. It encapsulates detailed imaging descriptors, risk factors, epidemiology,
clinical correlations, recommendations, recent research insights, and machine learning observations
for major cancers. This design facilitates type safety, easy maintenance, and extended functionality
(e.g., converting entries to dicts or formatted summaries).

Usage:
    from oncology_differentials import get_oncology_differential, list_oncology_differentials

    differential = get_oncology_differential("Breast Cancer")
    print(differential.formatted_summary())

    all_differentials = list_oncology_differentials()
    for cancer, diff in all_differentials.items():
        print(f"{cancer}: {diff.epidemiology}")
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict

@dataclass
class OncologyDifferential:
    imaging_descriptors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    epidemiology: str = ""
    clinical_diagnostic_correlations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    recent_research: str = ""
    ml_insights: str = ""

    def to_dict(self) -> Dict:
        """Convert the oncology differential entry into a dictionary."""
        return asdict(self)

    def formatted_summary(self) -> str:
        """Returns a formatted multi-line summary of the differential diagnosis."""
        parts = []
        if self.imaging_descriptors:
            parts.append("Imaging Descriptors:\n  - " + "\n  - ".join(self.imaging_descriptors))
        if self.risk_factors:
            parts.append("Risk Factors:\n  - " + "\n  - ".join(self.risk_factors))
        if self.epidemiology:
            parts.append(f"Epidemiology:\n  {self.epidemiology}")
        if self.clinical_diagnostic_correlations:
            parts.append("Clinical Diagnostic Correlations:\n  - " + "\n  - ".join(self.clinical_diagnostic_correlations))
        if self.recommendations:
            parts.append("Recommendations:\n  - " + "\n  - ".join(self.recommendations))
        if self.recent_research:
            parts.append(f"Recent Research:\n  {self.recent_research}")
        if self.ml_insights:
            parts.append(f"ML Insights:\n  {self.ml_insights}")
        return "\n\n".join(parts)


# Define the oncology differentials using the dataclass structure.
oncology_differentials: Dict[str, OncologyDifferential] = {
    "Breast Cancer": OncologyDifferential(
        imaging_descriptors=[
            "Mass with spiculated margins",
            "Microcalcifications",
            "Architectural distortion",
            "Nipple retraction",
            "Skin thickening",
            "Lymphadenopathy",
            "Ductal irregularities"
        ],
        risk_factors=[
            "Age",
            "Family history",
            "Genetic mutations (BRCA1, BRCA2)",
            "Early menarche, late menopause",
            "Nulliparity or late first pregnancy",
            "Hormone replacement therapy",
            "Obesity",
            "Alcohol consumption"
        ],
        epidemiology="Most common cancer in women worldwide; incidence increases in high-risk populations.",
        clinical_diagnostic_correlations=[
            "Palpable breast mass",
            "Nipple discharge",
            "Skin changes",
            "Lymph node enlargement",
            "Breast pain"
        ],
        recommendations=[
            "Mammography and digital breast tomosynthesis",
            "Breast ultrasound",
            "MRI of the breast for high-risk screening",
            "Image-guided core needle biopsy",
            "Sentinel lymph node biopsy for staging",
            "Surgical resection (lumpectomy or mastectomy)",
            "Radiation therapy",
            "Chemotherapy",
            "Hormone therapy",
            "Targeted therapy",
            "Immunotherapy",
            "Molecular subtyping (HER2, ER, PR testing)"
        ],
        recent_research=(
            "Emerging liquid biopsy techniques and AI-enhanced imaging are revolutionizing early detection "
            "and personalized treatment."
        ),
        ml_insights="Machine learning models now accurately predict tumor receptor status from imaging alone."
    ),
    "Prostate Cancer": OncologyDifferential(
        imaging_descriptors=[
            "Peripheral zone lesion",
            "Reduced diffusion on MRI",
            "Elevated choline/citrate ratio on MR spectroscopy",
            "Bone metastases",
            "Heterogeneous signal intensity"
        ],
        risk_factors=[
            "Age",
            "Family history",
            "African American ethnicity",
            "High-fat diet",
            "Obesity"
        ],
        epidemiology="Most common cancer in men; risk increases significantly with age.",
        clinical_diagnostic_correlations=[
            "Elevated PSA levels",
            "Urinary symptoms (frequency, urgency, nocturia)",
            "Bone pain (in metastatic cases)",
            "Erectile dysfunction"
        ],
        recommendations=[
            "PSA testing",
            "Digital rectal exam (DRE)",
            "Transrectal ultrasound (TRUS) with biopsy",
            "MRI of the prostate",
            "Gleason scoring for risk stratification",
            "Active surveillance for low-risk disease",
            "Radical prostatectomy",
            "Radiation therapy",
            "Hormone therapy",
            "Chemotherapy",
            "Molecular profiling for targeted treatment"
        ],
        recent_research="Advances in multiparametric MRI and genomic classifiers are refining risk stratification.",
        ml_insights="Deep learning algorithms can now segment prostate lesions with high precision, aiding in biopsy targeting."
    ),
    "Colorectal Cancer": OncologyDifferential(
        imaging_descriptors=[
            "Polypoid lesion",
            "Annular constricting lesion",
            "Bowel wall thickening",
            "Lymph node metastases",
            "Liver metastases",
            "Peritoneal implants",
            "Mucosal irregularities"
        ],
        risk_factors=[
            "Age",
            "Family history",
            "Inflammatory bowel disease (IBD)",
            "Diet high in red and processed meat",
            "Smoking",
            "Obesity",
            "Alcohol consumption"
        ],
        epidemiology="Third most common cancer worldwide; effective screening programs significantly reduce mortality.",
        clinical_diagnostic_correlations=[
            "Altered bowel habits",
            "Rectal bleeding",
            "Abdominal pain",
            "Weight loss",
            "Iron deficiency anemia"
        ],
        recommendations=[
            "Colonoscopy",
            "Flexible sigmoidoscopy",
            "Fecal occult blood test (FOBT)",
            "Fecal immunochemical test (FIT)",
            "CT colonography",
            "Biopsy for histopathological confirmation",
            "Surgical resection",
            "Chemotherapy",
            "Radiation therapy",
            "Targeted therapy",
            "Immunotherapy"
        ],
        recent_research="AI-driven colonoscopy and molecular diagnostics are emerging to enhance early detection.",
        ml_insights="Advanced algorithms now assist in detecting subtle mucosal irregularities indicative of early neoplasia."
    ),
}

def get_oncology_differential(cancer_type: str) -> OncologyDifferential:
    """
    Retrieve the oncology differential for a given cancer type.

    Args:
        cancer_type (str): The cancer type (e.g., "Breast Cancer").

    Returns:
        OncologyDifferential: The differential diagnosis data for the specified cancer.

    Raises:
        KeyError: If the specified cancer type is not available.
    """
    try:
        return oncology_differentials[cancer_type]
    except KeyError as e:
        raise KeyError(f"No oncology differential found for '{cancer_type}'.") from e

def list_oncology_differentials() -> Dict[str, OncologyDifferential]:
    """
    List all available oncology differentials.

    Returns:
        Dict[str, OncologyDifferential]: A dictionary mapping cancer types to their differential data.
    """
    return oncology_differentials.copy()
