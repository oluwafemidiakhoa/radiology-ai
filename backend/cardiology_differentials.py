from dataclasses import dataclass, asdict, field
from typing import List, Dict, Union, Optional

@dataclass
class CardiologyDifferential:
    """
    Represents the comprehensive diagnostic profile for a specific cardiac condition or subcondition.
    Each instance consolidates:
      - Imaging attributes (e.g., MRI, ultrasound, CT findings)
      - Known risk factors
      - Epidemiological context
      - Clinical correlations
      - Practice recommendations
      - Recent research highlights
      - Machine learning (ML) insights
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
        Converts this CardiologyDifferential instance into a dictionary, 
        offering easy serialization for web APIs or data pipelines.
        """
        return asdict(self)

    def formatted_summary(self) -> str:
        """
        Produces a multi-line string summarizing the differential diagnosis, 
        omitting any sections that are not populated. Suited for quick display 
        in CLI tools, UI dashboards, or PDF reports.
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


# Master Dictionary for Cardiology Differentials
# Supports both top-level and nested cardiac conditions (e.g., arrhythmias).
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
        epidemiology=(
            "A leading global cause of morbidity and mortality; "
            "early detection markedly improves survival and outcomes."
        ),
        clinical_diagnostic_correlations=[
            "Chest pain or pressure",
            "Shortness of breath",
            "Diaphoresis",
            "Nausea or vomiting",
            "ECG abnormalities (ST-segment elevation, T-wave inversion)",
            "Elevated troponin or other cardiac biomarkers",
            "Risk stratification via Killip classification"
        ],
        recommendations=[
            "Immediate 12-lead ECG",
            "Serial measurement of cardiac biomarkers",
            "Urgent coronary angiography (within appropriate time window)",
            "Percutaneous coronary intervention (PCI) if feasible",
            "Thrombolytic therapy if PCI is not available in time",
            "Dual antiplatelet therapy (aspirin + P2Y12 inhibitor)",
            "Beta-blockers, ACE inhibitors, statins",
            "Supplemental oxygen if hypoxic",
            "Consider cardiac MRI for viability assessment"
        ],
        recent_research=(
            "Cutting-edge imaging biomarkers and AI-based risk calculators are refining "
            "predictive accuracy and personalizing therapeutic decisions."
        ),
        ml_insights=(
            "Deep learning networks can forecast infarct size and assist in lesion "
            "classification, enhancing clinical triage."
        )
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
        epidemiology=(
            "Prevalence is rising with aging populations, significantly burdening global "
            "health systems. Multi-disciplinary management is crucial."
        ),
        clinical_diagnostic_correlations=[
            "Dyspnea (especially on exertion)",
            "Fatigue and reduced exercise tolerance",
            "Peripheral edema",
            "Orthopnea or paroxysmal nocturnal dyspnea",
            "Elevated BNP or NT-proBNP levels"
        ],
        recommendations=[
            "Echocardiography for structural/functional assessment",
            "Baseline ECG and chest X-ray",
            "BNP/NT-proBNP for diagnostic and prognostic purposes",
            "Neurohormonal blockade (ACE inhibitors/ARBs, beta-blockers, MRA)",
            "Diuretics for volume management",
            "SGLT2 inhibitors for HF with reduced EF",
            "Cardiac MRI when further tissue characterization is indicated"
        ],
        recent_research=(
            "Landmark trials endorse SGLT2 inhibitors in heart failure, reducing hospitalizations "
            "and improving quality of life even in non-diabetics."
        ),
        ml_insights=(
            "Predictive analytics using echocardiograms, labs, and wearable data can forecast "
            "acute decompensation, facilitating preventive interventions."
        )
    ),
    "Arrhythmia": {
        "Atrial Fibrillation (AF)": CardiologyDifferential(
            imaging_descriptors=[
                "Absent P waves on ECG",
                "Irregularly irregular rhythm"
            ],
            risk_factors=[
                "Advancing age",
                "Hypertension",
                "Coronary artery disease",
                "Valvular heart disease",
                "Heart failure",
                "Hyperthyroidism",
                "Alcohol abuse",
                "Obesity",
                "Obstructive sleep apnea"
            ],
            epidemiology=(
                "Atrial fibrillation ranks as the most common sustained arrhythmia worldwide, "
                "substantially elevating stroke risk."
            ),
            clinical_diagnostic_correlations=[
                "Palpitations and irregular pulse",
                "Dyspnea or reduced exercise capacity",
                "Fatigue and lightheadedness",
                "Chest discomfort",
                "Increased risk of systemic thromboembolism"
            ],
            recommendations=[
                "ECG confirmation with standard or extended monitoring",
                "Risk stratification for stroke (CHA₂DS₂-VASc score)",
                "Anticoagulation therapy (NOACs or warfarin)",
                "Rate control (beta-blockers, non-dihydropyridine CCBs) vs. rhythm control",
                "Elective cardioversion or AF ablation if indicated",
                "Consider left atrial appendage closure for select patients"
            ],
            recent_research=(
                "Innovative wearable ECG devices and AI-driven signal analysis detect subclinical AF, "
                "potentially preventing strokes through earlier intervention."
            ),
            ml_insights=(
                "Machine learning models can identify subtle ECG changes preceding AF onset, "
                "informing timely prophylactic care."
            )
        )
    }
}

def get_cardiology_differential(condition: str, subcondition: Optional[str] = None) -> CardiologyDifferential:
    """
    Fetches a specific cardiology differential based on the given 'condition' name.
    Optionally looks up a 'subcondition' within nested dictionaries (e.g., 'Atrial Fibrillation (AF)' under 'Arrhythmia').

    **Example Usage**:
        >>> diff = get_cardiology_differential("Myocardial Infarction (MI)")
        >>> print(diff.formatted_summary())

        >>> sub_diff = get_cardiology_differential("Arrhythmia", "Atrial Fibrillation (AF)")
        >>> print(sub_diff.formatted_summary())

    Raises:
        KeyError: If the requested condition or subcondition does not exist.
    """
    if subcondition is None:
        differential = cardiology_differentials.get(condition)
        if not isinstance(differential, CardiologyDifferential):
            raise KeyError(f"No differential found for '{condition}'. Check available conditions.")
        return differential
    else:
        nested_block = cardiology_differentials.get(condition)
        if not isinstance(nested_block, dict):
            raise KeyError(f"No nested conditions available for '{condition}'.")
        differential = nested_block.get(subcondition)
        if not differential:
            raise KeyError(f"Subcondition '{subcondition}' does not exist under '{condition}'.")
        return differential

def list_cardiology_differentials() -> Dict[str, Union[CardiologyDifferential, Dict[str, CardiologyDifferential]]]:
    """
    Provides a dictionary of all top-level cardiology conditions, potentially containing
    nested conditions (e.g., Arrhythmia -> Atrial Fibrillation). Useful for auto-generating
    navigable UIs or enumerating available differentials in APIs.

    **Example Usage**:
        >>> diffs = list_cardiology_differentials()
        >>> for name, diff in diffs.items():
        ...     print(name)
    """
    # Returns a shallow copy to prevent external mutation
    return cardiology_differentials.copy()
