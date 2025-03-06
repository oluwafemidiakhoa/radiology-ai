"""
Advanced Cardiology Differential Diagnosis Module

This module defines a structured representation of cardiology differential diagnoses using Python dataclasses.
It encapsulates detailed diagnostic criteria, imaging features, risk factors, epidemiology, clinical correlations,
recommendations, recent research findings, and machine learning insights for key cardiac conditions.
The module supports both top-level conditions and nested conditions (e.g., arrhythmias) for flexible usage.

Usage Example:
    from cardiology_differentials import get_cardiology_differential, list_cardiology_differentials

    # Retrieve a top-level differential:
    mi_diff = get_cardiology_differential("Myocardial Infarction (MI)")
    print(mi_diff.formatted_summary())

    # Retrieve a nested differential:
    af_diff = get_cardiology_differential("Arrhythmia", "Atrial Fibrillation (AF)")
    print(af_diff.formatted_summary())
    
    # List all differentials:
    all_diffs = list_cardiology_differentials()
    for condition, diff in all_diffs.items():
        print(condition)
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Union, Optional

@dataclass
class CardiologyDifferential:
    imaging_descriptors: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    epidemiology: str = ""
    clinical_diagnostic_correlations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    recent_research: str = ""
    ml_insights: str = ""

    def to_dict(self) -> Dict:
        """Convert the differential entry into a dictionary."""
        return asdict(self)

    def formatted_summary(self) -> str:
        """
        Returns a formatted multi-line summary of the differential diagnosis.
        Fields that are empty will be omitted from the summary.
        """
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


# Define the cardiology differentials (top-level and nested) in a dictionary.
cardiology_differentials: Dict[str, Union[CardiologyDifferential, Dict[str, CardiologyDifferential]]] = {
    "Myocardial Infarction (MI)": CardiologyDifferential(
        imaging_descriptors=[
            "Regional wall motion abnormality",
            "Reduced ejection fraction",
            "Late gadolinium enhancement (scarring)",
            "Coronary artery stenosis or occlusion",
            "Microvascular obstruction"
        ],
        risk_factors=[
            "Hypertension",
            "Hyperlipidemia",
            "Diabetes mellitus",
            "Smoking",
            "Family history",
            "Obesity",
            "Sedentary lifestyle"
        ],
        epidemiology="A leading cause of morbidity and mortality worldwide; early detection is critical for improving outcomes.",
        clinical_diagnostic_correlations=[
            "Chest pain",
            "Shortness of breath",
            "Diaphoresis",
            "Nausea",
            "ECG changes (ST-segment elevation/depression, T-wave inversion)",
            "Elevated cardiac biomarkers (troponin)",
            "Killip classification for risk stratification"
        ],
        recommendations=[
            "Immediate ECG",
            "Cardiac biomarkers assessment",
            "Coronary angiography",
            "Percutaneous coronary intervention (PCI)",
            "Thrombolytic therapy if PCI is unavailable",
            "Dual antiplatelet therapy",
            "Beta-blockers, ACE inhibitors, and statins",
            "Oxygen supplementation",
            "Consider cardiac MRI for viability assessment"
        ],
        recent_research="Emerging imaging biomarkers and AI-driven analysis are enhancing early MI detection and risk stratification.",
        ml_insights="Hybrid deep learning models predict infarct size and potential recovery with high accuracy."
    ),
    "Heart Failure": CardiologyDifferential(
        imaging_descriptors=[
            "Cardiomegaly",
            "Pulmonary edema",
            "Pleural effusion",
            "Left ventricular dilation",
            "Reduced ejection fraction",
            "Mitral regurgitation",
            "Tricuspid regurgitation",
            "Diastolic dysfunction"
        ],
        risk_factors=[
            "Hypertension",
            "Coronary artery disease",
            "Valvular heart disease",
            "Cardiomyopathy",
            "Diabetes mellitus",
            "Alcohol abuse",
            "Family history"
        ],
        epidemiology="Increasing prevalence among aging populations with significant morbidity.",
        clinical_diagnostic_correlations=[
            "Dyspnea on exertion",
            "Fatigue",
            "Peripheral edema",
            "Orthopnea",
            "Paroxysmal nocturnal dyspnea",
            "Elevated BNP or NT-proBNP"
        ],
        recommendations=[
            "Echocardiogram for structural and functional assessment",
            "ECG and chest X-ray",
            "BNP/NT-proBNP measurement",
            "Pharmacologic management (ACE inhibitors/ARBs, beta-blockers, diuretics)",
            "Aldosterone antagonists and digoxin in select cases",
            "SGLT2 inhibitors",
            "Cardiac MRI for detailed tissue characterization"
        ],
        recent_research="Recent clinical trials support SGLT2 inhibitors in heart failure irrespective of diabetic status.",
        ml_insights="Predictive analytics using multi-modal imaging data now forecast heart failure progression."
    ),
    "Arrhythmia": {
        "Atrial Fibrillation (AF)": CardiologyDifferential(
            imaging_descriptors=[
                "Absence of P waves",
                "Irregularly irregular rhythm"
            ],
            risk_factors=[
                "Age",
                "Hypertension",
                "Coronary artery disease",
                "Valvular heart disease",
                "Heart failure",
                "Hyperthyroidism",
                "Alcohol abuse",
                "Obesity",
                "Sleep apnea"
            ],
            epidemiology="The most common sustained arrhythmia; significant risk for stroke.",
            clinical_diagnostic_correlations=[
                "Palpitations",
                "Shortness of breath",
                "Fatigue",
                "Dizziness",
                "Chest discomfort",
                "Thromboembolic events"
            ],
            recommendations=[
                "ECG for initial detection",
                "24-hour Holter monitoring",
                "Event recorder monitoring",
                "Anticoagulation therapy",
                "Rate control with beta-blockers or calcium channel blockers",
                "Rhythm control strategies (medications, cardioversion, ablation)",
                "Consider left atrial appendage closure in selected patients"
            ],
            recent_research="Emerging wearable ECG devices and AI algorithms are enhancing early AF detection.",
            ml_insights="Recent studies show AI can predict the onset of AF from subtle ECG variations."
        )
    }
}

def get_cardiology_differential(condition: str, subcondition: Optional[str] = None) -> CardiologyDifferential:
    """
    Retrieve the cardiology differential for a given condition.

    Args:
        condition (str): The top-level condition (e.g., "Myocardial Infarction (MI)", "Arrhythmia").
        subcondition (Optional[str]): For nested conditions (e.g., "Atrial Fibrillation (AF)" under "Arrhythmia").

    Returns:
        CardiologyDifferential: The differential diagnosis data for the specified condition.

    Raises:
        KeyError: If the specified condition or subcondition is not available.
    """
    if subcondition is None:
        differential = cardiology_differentials.get(condition)
        if differential is None or not isinstance(differential, CardiologyDifferential):
            raise KeyError(f"No cardiology differential found for '{condition}'.")
        return differential
    else:
        nested = cardiology_differentials.get(condition)
        if nested is None or not isinstance(nested, dict):
            raise KeyError(f"No nested cardiology differential found for category '{condition}'.")
        differential = nested.get(subcondition)
        if differential is None:
            raise KeyError(f"No cardiology differential found for '{subcondition}' in category '{condition}'.")
        return differential

def list_cardiology_differentials() -> Dict[str, Union[CardiologyDifferential, Dict[str, CardiologyDifferential]]]:
    """
    List all available cardiology differentials.

    Returns:
        A dictionary mapping condition names (or categories) to their differential data.
    """
    # Return a shallow copy to prevent accidental mutation.
    return cardiology_differentials.copy()
