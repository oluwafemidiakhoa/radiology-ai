"""
Advanced Oncology Differential Diagnosis Module

This module defines a structured representation of advanced oncology differential diagnoses
using Python dataclasses. It encapsulates detailed imaging descriptors, risk factors,
epidemiology, clinical correlations, treatment recommendations, recent research insights,
and machine learning observations for key cancers. The design ensures type safety, easy
maintenance, and flexible usage (e.g., converting entries to dictionaries or formatted
summaries).

Usage:
    from oncology_differentials import get_oncology_differential, list_oncology_differentials

    # Retrieve a differential for Breast Cancer:
    differential = get_oncology_differential("Breast Cancer")
    print(differential.formatted_summary())

    # Iterate through all known oncology differentials:
    all_differentials = list_oncology_differentials()
    for cancer_name, diff_data in all_differentials.items():
        print(f"{cancer_name}: {diff_data.epidemiology}")
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict

@dataclass
class OncologyDifferential:
    """
    Encapsulates the diagnostic profile of a specific cancer type, including:
      - Imaging Descriptors
      - Risk Factors
      - Epidemiology
      - Clinical Diagnostic Correlations
      - Core Recommendations
      - Recent Research Highlights
      - ML (Machine Learning) Insights

    Structured for maximum clarity, this dataclass allows easy serialization,
    straightforward integration with ML pipelines, and user-friendly summary generation.
    """
    imaging_descriptors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    epidemiology: str = ""
    clinical_diagnostic_correlations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    recent_research: str = ""
    ml_insights: str = ""

    def to_dict(self) -> Dict:
        """
        Converts the instance into a dictionary, facilitating easy export to APIs,
        databases, or JSON-based pipelines.
        """
        return asdict(self)

    def formatted_summary(self) -> str:
        """
        Produces a multi-line string summarizing each aspect of the differential.
        Ideal for logging, CLI tools, or display in web interfaces.
        """
        parts = []
        if self.imaging_descriptors:
            parts.append("Imaging Descriptors:\n  - " + "\n  - ".join(self.imaging_descriptors))
        if self.risk_factors:
            parts.append("Risk Factors:\n  - " + "\n  - ".join(self.risk_factors))
        if self.epidemiology:
            parts.append(f"Epidemiology:\n  {self.epidemiology}")
        if self.clinical_diagnostic_correlations:
            parts.append("Clinical Diagnostic Correlations:\n  - " 
                         + "\n  - ".join(self.clinical_diagnostic_correlations))
        if self.recommendations:
            parts.append("Recommendations:\n  - " + "\n  - ".join(self.recommendations))
        if self.recent_research:
            parts.append(f"Recent Research:\n  {self.recent_research}")
        if self.ml_insights:
            parts.append(f"ML Insights:\n  {self.ml_insights}")
        return "\n\n".join(parts)


###############################################################################
# Dictionary of Oncology Differentials
###############################################################################
oncology_differentials: Dict[str, OncologyDifferential] = {
    "Breast Cancer": OncologyDifferential(
        imaging_descriptors=[
            "Spiculated mass margins",
            "Microcalcifications",
            "Architectural distortion",
            "Nipple retraction",
            "Skin thickening",
            "Lymphadenopathy",
            "Irregular ductal changes"
        ],
        risk_factors=[
            "Advancing age",
            "Family history",
            "Genetic predisposition (BRCA1, BRCA2)",
            "Early menarche / Late menopause",
            "Nulliparity or late first pregnancy",
            "Hormone replacement therapy",
            "Obesity",
            "Regular alcohol intake"
        ],
        epidemiology=(
            "Most prevalent cancer in women worldwide; incidence is elevated in high-risk populations, "
            "underscoring the value of screening."
        ),
        clinical_diagnostic_correlations=[
            "Palpable breast mass",
            "Nipple discharge (serous or bloody)",
            "Skin erythema or dimpling",
            "Lymph node enlargement",
            "Breast or axillary pain"
        ],
        recommendations=[
            "Mammography and digital tomosynthesis",
            "Targeted breast ultrasound",
            "MRI for high-risk screening",
            "Core needle biopsy with image guidance",
            "Sentinel lymph node mapping",
            "Surgical resection (lumpectomy vs. mastectomy)",
            "Adjuvant radiation therapy",
            "Chemotherapy regimens (anthracycline- or taxane-based)",
            "Endocrine therapy if hormone receptor-positive",
            "HER2-targeted therapy if HER2-positive",
            "Immunotherapy for PD-L1-positive subtypes",
            "Consider molecular subtyping"
        ],
        recent_research=(
            "Liquid biopsy techniques and AI-driven mammography solutions are shifting paradigms "
            "toward earlier detection and individualized treatments."
        ),
        ml_insights=(
            "Deep learning models can classify tumor receptor status and predict response to neoadjuvant "
            "therapy, promoting precision medicine."
        )
    ),

    "Prostate Cancer": OncologyDifferential(
        imaging_descriptors=[
            "Peripheral zone lesion",
            "Low ADC values on DWI MRI",
            "Elevated choline/citrate ratio (MR spectroscopy)",
            "Osteoblastic bone metastases",
            "Heterogeneous signal on T2-weighted MRI"
        ],
        risk_factors=[
            "Increasing age",
            "Genetic predisposition",
            "Family history",
            "African American ethnicity",
            "High-fat diet",
            "Obesity"
        ],
        epidemiology=(
            "Most frequently diagnosed cancer in men; the risk increases substantially post-50, "
            "with a notable mortality impact if untreated."
        ),
        clinical_diagnostic_correlations=[
            "Elevated PSA (Prostate-Specific Antigen)",
            "Urinary frequency or urgency",
            "Nocturia",
            "Dysuria",
            "Metastatic bone pain",
            "Erectile dysfunction in advanced stages"
        ],
        recommendations=[
            "PSA screening (with age and risk considerations)",
            "Digital rectal exam (DRE)",
            "Transrectal ultrasound (TRUS)-guided biopsy",
            "Multiparametric MRI of the prostate",
            "Gleason score determination",
            "Active surveillance for low-risk disease",
            "Radical prostatectomy",
            "External beam radiation therapy",
            "Androgen deprivation therapy",
            "Chemotherapy (advanced cases)",
            "Genomic profiling for novel targets"
        ],
        recent_research=(
            "Innovations in MRI-targeted biopsy and genomic classifiers refine risk stratification, "
            "reducing over-treatment of indolent disease."
        ),
        ml_insights=(
            "Computer vision algorithms excel at segmenting prostate lesions and guiding precise biopsy, "
            "improving diagnostic yield."
        )
    ),

    "Colorectal Cancer": OncologyDifferential(
        imaging_descriptors=[
            "Polypoid lesion in the colon",
            "Annular constricting lesion (napkin-ring appearance)",
            "Thickened bowel wall",
            "Lymph node enlargement",
            "Hepatic metastases",
            "Peritoneal implants",
            "Irregular mucosal surface"
        ],
        risk_factors=[
            "Older age (>50)",
            "Family history of colorectal cancer",
            "Chronic inflammatory bowel disease (Ulcerative Colitis, Crohn's)",
            "Diets high in red/processed meats",
            "Tobacco use",
            "Excessive alcohol intake",
            "Obesity"
        ],
        epidemiology=(
            "Among the top three most prevalent cancers globally; screening colonoscopy and fecal tests "
            "have significantly reduced mortality in many regions."
        ),
        clinical_diagnostic_correlations=[
            "Changes in bowel habits (constipation or diarrhea)",
            "Occult or overt rectal bleeding",
            "Abdominal discomfort or cramping",
            "Unexplained weight loss",
            "Iron deficiency anemia"
        ],
        recommendations=[
            "Colonoscopy (gold standard)",
            "Fecal occult blood tests (FOBT) or fecal immunochemical tests (FIT)",
            "CT colonography as a less invasive alternative",
            "Biopsy for histopathological confirmation",
            "Surgical resection with clear margins",
            "Adjuvant or neoadjuvant chemotherapy",
            "Radiation therapy (especially for rectal cancers)",
            "Targeted therapies (e.g., EGFR or VEGF inhibitors)",
            "Immunotherapy in select molecular subtypes"
        ],
        recent_research=(
            "AI-aided polyp detection is enhancing adenoma detection rates, potentially lowering intervals "
            "between screening and diagnosis."
        ),
        ml_insights=(
            "Multi-modal machine learning frameworks integrate endoscopic imaging, genomics, and clinical "
            "metadata to project recurrence and survival probabilities."
        )
    ),
}

def get_oncology_differential(cancer_type: str) -> OncologyDifferential:
    """
    Retrieves the oncology differential data object for a given cancer type.

    Args:
        cancer_type (str): e.g. "Breast Cancer"

    Returns:
        OncologyDifferential: Contains imaging descriptors, risk factors, 
        and additional context for the requested cancer.

    Raises:
        KeyError: If the specified cancer type is not recognized or unavailable.
    """
    try:
        return oncology_differentials[cancer_type]
    except KeyError as e:
        raise KeyError(f"No oncology differential found for '{cancer_type}'.") from e

def list_oncology_differentials() -> Dict[str, OncologyDifferential]:
    """
    Enumerates all available oncology differentials in a shallow copy of the underlying dictionary.
    Useful for auto-generating menus, dynamic UI elements, or advanced analytics tasks.

    Returns:
        Dict[str, OncologyDifferential]: Mapping from cancer names to their respective differentials.
    """
    return oncology_differentials.copy()
