"""
Advanced Radiology Differential Diagnosis Module

This module defines a structured representation of radiology differential diagnoses 
using Python dataclasses. It covers advanced diagnostic considerations for pulmonary,
neurological, and musculoskeletal conditions encountered in radiology. For each condition,
the module provides detailed imaging descriptors, risk factors, epidemiology, clinical correlations, 
recommendations, recent research findings, and machine learning insights.

Helper functions allow retrieval of specific differentials or listing of all available entries.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict

@dataclass
class RadiologyDifferential:
    imaging_descriptors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    epidemiology: str = ""
    clinical_diagnostic_correlations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    recent_research: str = ""
    ml_insights: str = ""

    def to_dict(self) -> Dict:
        """Convert the radiology differential entry into a dictionary."""
        return asdict(self)

    def formatted_summary(self) -> str:
        """Return a formatted multi-line summary of the differential diagnosis."""
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


# Define the radiology differentials organized by category.
radiology_differentials: Dict[str, Dict[str, RadiologyDifferential]] = {
    "Pulmonary": {
        "Pneumonia": RadiologyDifferential(
            imaging_descriptors=[
                "Lobar consolidation",
                "Multifocal infiltrates",
                "Air bronchograms",
                "Ground-glass opacity",
                "Interstitial thickening"  # Advanced descriptor for atypical/viral pneumonia
            ],
            risk_factors=[
                "Advanced age",
                "Immunocompromise",
                "Chronic lung disease",
                "Smoking",
                "Aspiration",
                "Recent viral infection"  # Post-COVID-19 observations
            ],
            epidemiology="High prevalence during winter; emerging data indicate increased incidence in post-viral settings.",
            clinical_diagnostic_correlations=[
                "Fever",
                "Cough",
                "Purulent sputum",
                "Elevated WBC count",
                "Positive sputum culture",
                "CRP elevation",
                "Procalcitonin levels"  # Laboratory marker for bacterial infection
            ],
            recommendations=[
                "Chest X-ray",
                "CT Chest (if X-ray is inconclusive or for suspected viral pneumonia)",
                "Sputum culture",
                "Blood cultures",
                "Empiric then targeted antibiotic therapy",
                "Supportive care (oxygen, hydration)",
                "Consider viral panel or PCR testing for influenza/COVID-19"
            ],
            recent_research="Recent studies indicate the utility of AI-enhanced CT imaging to differentiate bacterial from viral pneumonia.",
            ml_insights="Integration of deep learning models has improved classification accuracy by up to 15% in recent trials."
        ),
        "Pulmonary Embolism": RadiologyDifferential(
            imaging_descriptors=[
                "Wedge-shaped opacity (Hampton's hump)",
                "Vascular cutoff",
                "Enlarged pulmonary artery",
                "Right heart strain (RV/LV ratio > 1)",
                "Pleural effusion",
                "Mosaic attenuation pattern",
                "Filling defects on CT Pulmonary Angiography"
            ],
            risk_factors=[
                "Immobility",
                "Recent surgery",
                "Trauma",
                "Cancer",
                "Oral contraceptives",
                "Hormone replacement therapy",
                "Pregnancy",
                "Inherited thrombophilia"
            ],
            epidemiology="Moderate prevalence; a leading cause of preventable mortality in hospitalized patients.",
            clinical_diagnostic_correlations=[
                "Sudden onset dyspnea",
                "Pleuritic chest pain",
                "Tachycardia",
                "Hypoxia",
                "D-dimer elevation",
                "Wells score assessment"
            ],
            recommendations=[
                "CT Pulmonary Angiography (CTPA)",
                "Ventilation/Perfusion (V/Q) scan (if CTPA is contraindicated)",
                "Pulmonary angiography (rarely used)",
                "ECG",
                "Echocardiogram (to assess right heart strain)",
                "Anticoagulation (LMWH, unfractionated heparin, DOACs)",
                "Thrombolysis (in severe cases)",
                "Embolectomy (rarely used)"
            ],
            recent_research="AI-driven analysis of CTPA images has shown promising results in early PE detection.",
            ml_insights="Deep learning segmentation algorithms have improved clot detection and quantification."
        ),
        "Lung Cancer": RadiologyDifferential(
            imaging_descriptors=[
                "Solitary pulmonary nodule",
                "Mass with irregular borders",
                "Hilar or mediastinal lymphadenopathy",
                "Pleural effusion",
                "Atelectasis",
                "Rib destruction",
                "Ground-glass opacity with spiculation"  # Indicative of early adenocarcinoma
            ],
            risk_factors=[
                "Smoking",
                "Radon exposure",
                "Asbestos exposure",
                "Family history",
                "Air pollution",
                "Previous lung infections"
            ],
            epidemiology="Leading cause of cancer death worldwide; molecular subtyping now guides management.",
            clinical_diagnostic_correlations=[
                "Chronic cough",
                "Hemoptysis",
                "Weight loss",
                "Shortness of breath",
                "Chest pain",
                "Fatigue"
            ],
            recommendations=[
                "Chest CT scan",
                "PET/CT scan",
                "Bronchoscopy with biopsy",
                "CT-guided biopsy",
                "Surgical resection",
                "Chemotherapy",
                "Radiation therapy",
                "Immunotherapy",
                "Molecular profiling"
            ],
            recent_research="Recent advances in liquid biopsy and AI-based image analysis are revolutionizing early lung cancer detection.",
            ml_insights="Hybrid CNN architectures have achieved significant improvements in nodule classification accuracy."
        ),
        "COPD (Chronic Obstructive Pulmonary Disease)": RadiologyDifferential(
            imaging_descriptors=[
                "Hyperinflation",
                "Flattened diaphragm",
                "Increased retrosternal air space",
                "Bullae",
                "Thickened bronchial walls",
                "Centrilobular emphysema"
            ],
            risk_factors=[
                "Smoking",
                "Alpha-1 antitrypsin deficiency",
                "Air pollution",
                "Occupational exposures"
            ],
            epidemiology="Common chronic respiratory disease with increasing prevalence worldwide.",
            clinical_diagnostic_correlations=[
                "Chronic cough",
                "Sputum production",
                "Shortness of breath",
                "Wheezing",
                "Decreased FEV1/FVC ratio on spirometry"
            ],
            recommendations=[
                "Pulmonary function tests (spirometry)",
                "Chest X-ray",
                "CT scan for detailed assessment of emphysema and bronchiectasis",
                "Bronchodilator therapy",
                "Inhaled corticosteroids",
                "Pulmonary rehabilitation",
                "Oxygen therapy (if hypoxemic)"
            ],
            recent_research="Integration of AI with spirometry data has enhanced early detection and monitoring of COPD progression.",
            ml_insights="Predictive models now provide personalized risk assessments based on imaging and clinical data."
        )
    },
    "Neurological": {
        "Stroke": RadiologyDifferential(
            imaging_descriptors=[
                "Hyperdense vessel sign (acute thrombus)",
                "Loss of gray-white differentiation",
                "Sulcal effacement, cytotoxic edema",
                "Diffusion restriction on MRI",
                "Hemorrhagic transformation"
            ],
            risk_factors=[
                "Hypertension",
                "Hyperlipidemia",
                "Diabetes mellitus",
                "Smoking",
                "Atrial fibrillation",
                "Carotid artery stenosis",
                "Family history"
            ],
            epidemiology="Very high prevalence; one of the leading causes of long-term disability and death.",
            clinical_diagnostic_correlations=[
                "Sudden onset neurological deficits",
                "NIH Stroke Scale assessment",
                "FAST exam (Face, Arms, Speech, Time)"
            ],
            recommendations=[
                "Non-contrast CT of the brain",
                "CT Angiography (CTA) for vascular assessment",
                "MRI with DWI for early ischemic changes",
                "ECG to detect atrial fibrillation",
                "Blood glucose monitoring",
                "Thrombolytic therapy if within the treatment window",
                "Mechanical thrombectomy for large vessel occlusion",
                "Antiplatelet therapy and blood pressure management"
            ],
            recent_research="Recent trials emphasize the benefits of endovascular thrombectomy in select patient populations.",
            ml_insights="AI algorithms can now rapidly quantify infarct volume and predict functional outcomes."
        ),
        "Brain Tumor": RadiologyDifferential(
            imaging_descriptors=[
                "Mass lesion with surrounding edema",
                "Contrast enhancement",
                "Midline shift",
                "Hydrocephalus",
                "Intracranial hemorrhage"
            ],
            risk_factors=[
                "Genetic syndromes (e.g., Neurofibromatosis, Tuberous sclerosis)",
                "Exposure to ionizing radiation"
            ],
            epidemiology="Relatively rare but with high clinical impact when present.",
            clinical_diagnostic_correlations=[
                "Headaches",
                "Seizures",
                "Focal neurological deficits",
                "Papilledema",
                "Cognitive changes"
            ],
            recommendations=[
                "MRI of the brain with and without contrast",
                "Surgical biopsy or resection",
                "Radiation therapy",
                "Chemotherapy",
                "Adjunctive steroid therapy to reduce edema"
            ],
            recent_research="Advanced imaging biomarkers are emerging to predict tumor aggressiveness.",
            ml_insights="Deep learning models have improved segmentation accuracy for brain tumors, aiding in surgical planning."
        ),
        "Multiple Sclerosis (MS)": RadiologyDifferential(
            imaging_descriptors=[
                "Ovoid periventricular lesions",
                "Dawson's fingers (lesions perpendicular to ventricles)",
                "Enhancing lesions indicating active inflammation",
                "Spinal cord lesions"
            ],
            risk_factors=[
                "Genetic predisposition",
                "Vitamin D deficiency",
                "Epstein-Barr virus infection",
                "Smoking"
            ],
            epidemiology="More common in women and in temperate climates.",
            clinical_diagnostic_correlations=[
                "Optic neuritis",
                "Transverse myelitis",
                "Lhermitte's sign",
                "Chronic fatigue",
                "Sensory and motor deficits"
            ],
            recommendations=[
                "MRI of the brain and spinal cord with and without contrast",
                "Lumbar puncture for oligoclonal bands",
                "Visual evoked potentials (VEPs)",
                "Initiate disease-modifying therapies (DMTs)",
                "Symptomatic treatment"
            ],
            recent_research="Novel biomarkers and advanced MRI sequences are being integrated for earlier diagnosis.",
            ml_insights="Machine learning has enabled automated lesion segmentation and volumetric analysis in MS patients."
        )
    },
    "Musculoskeletal": {
        "Fracture": RadiologyDifferential(
            imaging_descriptors=[
                "Discontinuity of the bone cortex",
                "Visible fracture line",
                "Displacement of bone fragments",
                "Associated soft tissue swelling"
            ],
            risk_factors=[
                "Trauma",
                "Osteoporosis",
                "Age-related degeneration",
                "Repetitive stress",
                "Underlying bone pathology"
            ],
            epidemiology="Very common in elderly populations and athletes.",
            clinical_diagnostic_correlations=[
                "Localized pain",
                "Swelling",
                "Deformity",
                "Limited range of motion",
                "Tenderness"
            ],
            recommendations=[
                "Plain X-ray for initial evaluation",
                "CT scan for detailed fracture assessment",
                "MRI if soft tissue injury is suspected",
                "Immobilization (casting or splinting)",
                "Analgesia and pain management",
                "Surgical fixation for unstable fractures"
            ],
            recent_research="Innovative 3D imaging and AI-driven fracture detection are improving diagnostic accuracy.",
            ml_insights="Deep neural networks now assist radiologists by highlighting subtle fracture lines that may be missed on plain films."
        )
    }
}

def get_radiology_differential(category: str, condition: str) -> RadiologyDifferential:
    """
    Retrieve the radiology differential for a given category and condition.

    Args:
        category (str): The radiology category (e.g., "Pulmonary").
        condition (str): The specific condition (e.g., "Pneumonia").

    Returns:
        RadiologyDifferential: The differential diagnosis data for the specified condition.

    Raises:
        KeyError: If the category or condition is not available.
    """
    try:
        return radiology_differentials[category][condition]
    except KeyError as e:
        raise KeyError(f"No radiology differential found for category '{category}' and condition '{condition}'.") from e

def list_radiology_differentials() -> Dict[str, Dict[str, RadiologyDifferential]]:
    """
    List all available radiology differentials organized by category.

    Returns:
        Dict[str, Dict[str, RadiologyDifferential]]: A nested dictionary mapping categories
        to condition names and their corresponding differential data.
    """
    # Return a shallow copy to prevent accidental mutation.
    return {cat: diff.copy() for cat, diff in radiology_differentials.items()}
