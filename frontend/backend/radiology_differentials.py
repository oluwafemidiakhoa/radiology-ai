"""
Ultra-Advanced Radiology Differential Diagnosis Module

Provides an enterprise-ready, dataclass-driven representation of differential diagnoses
for key radiological conditions across Pulmonary, Neurological, and Musculoskeletal domains.
Each entry details imaging descriptors, risk factors, epidemiology, clinical correlations,
recommendations, current research, and machine learning insights. 

Helper functions allow retrieval of specific differentials by category and condition,
or listing all available entries for broader usage.

Potential Use Cases:
    - Integration in hospital PACS/EHR systems for real-time AI-based decision support.
    - ML workflow enhancement with curated features and references (e.g., ground-glass opacities).
    - Academic or research platforms requiring standardized references on advanced radiological findings.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict

@dataclass
class RadiologyDifferential:
    """
    Encapsulates the complete diagnostic profile for a radiological condition, including:
      - Imaging Descriptors (key morphological or sign-based observations)
      - Risk Factors (lifestyle, genetic, environmental)
      - Epidemiology (prevalence, significant subgroups)
      - Clinical Diagnostic Correlations (signs, labs, physical exam clues)
      - Recommendations (diagnostic imaging steps, therapeutic pointers)
      - Recent Research (cutting-edge discoveries or trials)
      - ML Insights (emerging AI/ML trends relevant to diagnosis or classification)
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
        Serializes this differential entry into a dictionary, allowing seamless
        integration into JSON-based APIs, data pipelines, or logging systems.
        """
        return asdict(self)

    def formatted_summary(self) -> str:
        """
        Creates a multi-line string summarizing all non-empty fields, making it well-suited
        for human review in a CLI, web UI, or reporting utility.
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
# Radiology Differentials Organized by Category
###############################################################################
radiology_differentials: Dict[str, Dict[str, RadiologyDifferential]] = {
    "Pulmonary": {
        "Pneumonia": RadiologyDifferential(
            imaging_descriptors=[
                "Lobar consolidation",
                "Multifocal infiltrates",
                "Air bronchograms",
                "Ground-glass opacity",
                "Interstitial thickening"
            ],
            risk_factors=[
                "Advanced age",
                "Immunocompromise",
                "Chronic lung disease",
                "Smoking",
                "Aspiration",
                "Recent viral infection"
            ],
            epidemiology=(
                "High prevalence in winter months; notable post-viral occurrences, especially post-COVID-19."
            ),
            clinical_diagnostic_correlations=[
                "Fever",
                "Cough (often productive)",
                "Elevated WBC count",
                "Positive sputum culture",
                "CRP elevation",
                "Procalcitonin"
            ],
            recommendations=[
                "Chest X-ray as first-line imaging",
                "CT Chest for further evaluation of atypical cases",
                "Sputum culture & blood cultures",
                "Empiric or targeted antibiotic therapy",
                "Supportive care (oxygen, IV fluids)"
            ],
            recent_research=(
                "AI-augmented CT algorithms show promise in distinguishing bacterial from viral etiologies."
            ),
            ml_insights=(
                "Deep learning classification models can raise diagnostic accuracy by an additional 15%."
            )
        ),
        "Pulmonary Embolism": RadiologyDifferential(
            imaging_descriptors=[
                "Wedge-shaped opacity (Hampton's hump)",
                "Vascular cutoff",
                "Enlarged pulmonary artery",
                "Right heart strain on CT",
                "Pleural effusion",
                "Mosaic attenuation",
                "Filling defects on CT Pulmonary Angiography"
            ],
            risk_factors=[
                "Prolonged immobility",
                "Recent surgery/trauma",
                "Cancer or thrombophilia",
                "Hormone therapy (oral contraceptives/HRT)",
                "Pregnancy",
                "Obesity"
            ],
            epidemiology=(
                "Moderate prevalence and a top cause of preventable mortality in hospitalized patients."
            ),
            clinical_diagnostic_correlations=[
                "Acute dyspnea",
                "Pleuritic chest pain",
                "Tachycardia",
                "Hypoxia",
                "D-dimer elevation",
                "Wells score usage"
            ],
            recommendations=[
                "CT Pulmonary Angiography (CTPA)",
                "V/Q scan if CTPA contraindicated",
                "Anticoagulation (LMWH, heparin, DOACs)",
                "Thrombolysis in massive PE",
                "Mechanical embolectomy in critical scenarios"
            ],
            recent_research=(
                "AI-based detection on CTPA images reduces time to diagnosis, especially in high-volume centers."
            ),
            ml_insights=(
                "Deep learning segmentation tools enhance clot localization/quantification for risk stratification."
            )
        ),
        "Lung Cancer": RadiologyDifferential(
            imaging_descriptors=[
                "Solitary pulmonary nodule",
                "Irregular mass borders",
                "Hilar or mediastinal lymphadenopathy",
                "Pleural effusion",
                "Atelectasis",
                "Rib invasion/destruction",
                "Spiculated ground-glass opacity"
            ],
            risk_factors=[
                "Smoking",
                "Radon exposure",
                "Asbestos",
                "Occupational hazards",
                "Chronic lung infections",
                "Family history"
            ],
            epidemiology=(
                "Leading cause of cancer-related mortality worldwide; molecular profiling now shapes therapy."
            ),
            clinical_diagnostic_correlations=[
                "Chronic cough",
                "Hemoptysis",
                "Unintentional weight loss",
                "Dyspnea",
                "Chest pain"
            ],
            recommendations=[
                "High-resolution CT chest",
                "PET/CT for staging",
                "Bronchoscopy or CT-guided biopsy",
                "Surgical resection if localized",
                "Chemotherapy, radiation, or immunotherapy (advanced disease)",
                "Targeted therapy if actionable mutations"
            ],
            recent_research=(
                "Liquid biopsy and AI-based imaging analytics are pushing earlier detection and personalized protocols."
            ),
            ml_insights=(
                "Hybrid CNN architectures excel at classifying nodule malignancy, achieving high AUC scores."
            )
        ),
        "COPD (Chronic Obstructive Pulmonary Disease)": RadiologyDifferential(
            imaging_descriptors=[
                "Hyperinflated lungs",
                "Flattened diaphragms",
                "Increased retrosternal air space",
                "Bullae formation",
                "Thickened bronchial walls",
                "Centrilobular emphysema"
            ],
            risk_factors=[
                "Smoking",
                "Alpha-1 antitrypsin deficiency",
                "Industrial pollutants",
                "Chronic occupational exposure"
            ],
            epidemiology=(
                "Common chronic respiratory ailment globally, trending upward with aging demographics."
            ),
            clinical_diagnostic_correlations=[
                "Chronic cough with sputum",
                "Shortness of breath on exertion",
                "Decreased FEV1/FVC on spirometry"
            ],
            recommendations=[
                "Pulmonary function tests (spirometry)",
                "Chest X-ray or CT for structural damage",
                "Bronchodilators",
                "Inhaled corticosteroids",
                "Oxygen therapy (if hypoxic)"
            ],
            recent_research=(
                "AI-driven spirometry integration increases early detection rates, optimizing management."
            ),
            ml_insights=(
                "Predictive analytics fusing imaging & clinical data provide personalized risk/progression evaluations."
            )
        )
    },
    "Neurological": {
        "Stroke": RadiologyDifferential(
            imaging_descriptors=[
                "Hyperdense artery sign",
                "Loss of gray-white differentiation",
                "Sulcal effacement",
                "Diffusion restriction on DWI",
                "Hemorrhagic transformation"
            ],
            risk_factors=[
                "Hypertension",
                "Hyperlipidemia",
                "Diabetes",
                "Smoking",
                "Atrial fibrillation",
                "Carotid stenosis",
                "Family history"
            ],
            epidemiology=(
                "Extremely high incidence globally; top cause of serious long-term disability and mortality."
            ),
            clinical_diagnostic_correlations=[
                "Acute focal neurologic deficits",
                "NIH Stroke Scale for severity",
                "FAST exam"
            ],
            recommendations=[
                "Non-contrast CT brain for initial hemorrhage/ischemia",
                "CT/MR angiography for vessel patency",
                "MRI (DWI) for ischemic core detection",
                "Thrombolysis if within the therapeutic window",
                "Mechanical thrombectomy in large vessel occlusion"
            ],
            recent_research=(
                "Extended windows for endovascular therapy validated by recent clinical trials in specific patients."
            ),
            ml_insights=(
                "AI-driven perfusion imaging speeds triage and improves outcome predictions in acute strokes."
            )
        ),
        "Brain Tumor": RadiologyDifferential(
            imaging_descriptors=[
                "Intracranial mass with surrounding edema",
                "Irregular contrast enhancement",
                "Midline shift",
                "Hydrocephalus",
                "Possible hemorrhagic components"
            ],
            risk_factors=[
                "Genetic syndromes (Neurofibromatosis, Tuberous sclerosis)",
                "Ionizing radiation exposure"
            ],
            epidemiology="Less common than metastatic brain tumors but often higher impact when symptomatic.",
            clinical_diagnostic_correlations=[
                "Chronic headaches",
                "Seizures",
                "Neurological deficits",
                "Cognitive changes",
                "Papilledema"
            ],
            recommendations=[
                "MRI brain with and without contrast",
                "Stereotactic biopsy or resection",
                "Radiation therapy",
                "Chemotherapy",
                "Steroids to reduce intracranial pressure"
            ],
            recent_research=(
                "Molecular markers (e.g., IDH status, MGMT promoter methylation) increasingly guide therapy."
            ),
            ml_insights=(
                "Deep learning tumor segmentation tools enhance surgical planning and prognosis estimation."
            )
        ),
        "Multiple Sclerosis (MS)": RadiologyDifferential(
            imaging_descriptors=[
                "Periventricular ovoid lesions (Dawson's fingers)",
                "Active enhancing lesions",
                "Spinal cord plaques",
                "Occasional black holes on T1-weighted MRI"
            ],
            risk_factors=[
                "Autoimmune predisposition",
                "Vitamin D deficiency",
                "EBV exposure",
                "Smoking"
            ],
            epidemiology=(
                "More frequent in young adults, particularly females, with variable global distributions."
            ),
            clinical_diagnostic_correlations=[
                "Optic neuritis",
                "Transverse myelitis",
                "Fatigue",
                "Motor/sensory deficits"
            ],
            recommendations=[
                "MRI brain/spinal cord with Gadolinium",
                "Lumbar puncture for CSF oligoclonal bands",
                "Disease-modifying therapies (DMTs)",
                "Symptomatic treatments for spasticity, fatigue"
            ],
            recent_research=(
                "Advanced MRI sequences and biomarkers enhance early detection and refine treatment efficacy."
            ),
            ml_insights=(
                "AI-driven lesion segmentation and volumetric analysis accelerate management decisions."
            )
        )
    },
    "Musculoskeletal": {
        "Fracture": RadiologyDifferential(
            imaging_descriptors=[
                "Cortical discontinuity",
                "Fracture line (visible or occult)",
                "Displacement of fragments",
                "Associated soft tissue swelling"
            ],
            risk_factors=[
                "Trauma",
                "Osteoporosis",
                "High-impact sports",
                "Repetitive stress",
                "Pathologic process in bone"
            ],
            epidemiology=(
                "Very common in geriatric populations and in athletic or accident-prone contexts."
            ),
            clinical_diagnostic_correlations=[
                "Local pain/tenderness",
                "Swelling and deformity",
                "Reduced function or mobility"
            ],
            recommendations=[
                "Plain X-ray to confirm",
                "CT for complex fractures",
                "MRI if occult fracture suspected",
                "Immobilization (casting, bracing)",
                "Surgical fixation in unstable cases"
            ],
            recent_research=(
                "3D printing and AI-driven fracture detection are revolutionizing pre-surgical planning."
            ),
            ml_insights=(
                "Neural networks highlight subtle fractures often missed, substantially reducing diagnostic errors."
            )
        )
    }
}


def get_radiology_differential(category: str, condition: str) -> RadiologyDifferential:
    """
    Retrieves the corresponding radiology differential by specifying both a domain category (e.g., 'Pulmonary')
    and a condition (e.g., 'Pneumonia').

    Args:
        category (str): The radiology category (e.g., "Pulmonary").
        condition (str): The condition within that category (e.g., "Pneumonia").

    Returns:
        RadiologyDifferential: A comprehensive data object covering imaging descriptors, 
        risk factors, epidemiology, and more.

    Raises:
        KeyError: If the specified category or condition does not exist in the dataset.
    """
    try:
        return radiology_differentials[category][condition]
    except KeyError as e:
        raise KeyError(
            f"No radiology differential found for category '{category}' and condition '{condition}'."
        ) from e

def list_radiology_differentials() -> Dict[str, Dict[str, RadiologyDifferential]]:
    """
    Enumerates all defined radiology differentials, organized by category and condition,
    in a shallow-copied dictionary to prevent accidental external mutation.

    Returns:
        Dict[str, Dict[str, RadiologyDifferential]]: Nested dictionary reflecting categories
        and their specific condition-based differentials.
    """
    return {cat: diff.copy() for cat, diff in radiology_differentials.items()}
