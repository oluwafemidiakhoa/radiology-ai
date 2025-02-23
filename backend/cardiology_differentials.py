# cardiology_differentials.py
# Advanced Cardiology Differential Diagnosis Dictionary
# Detailed diagnostic criteria, imaging features, and recommendations for key cardiac conditions.

cardiology_differentials = {
    "Myocardial Infarction (MI)": {
        "imaging_descriptors": [
            "Regional wall motion abnormality",
            "Reduced ejection fraction",
            "Late gadolinium enhancement (scarring)",
            "Coronary artery stenosis or occlusion",
            "Microvascular obstruction"  # Advanced descriptor
        ],
        "risk_factors": [
            "Hypertension",
            "Hyperlipidemia",
            "Diabetes mellitus",
            "Smoking",
            "Family history",
            "Obesity",
            "Sedentary lifestyle"
        ],
        "epidemiology": "A leading cause of morbidity and mortality worldwide; early detection is essential for improved outcomes.",
        "clinical_diagnostic_correlations": [
            "Chest pain",
            "Shortness of breath",
            "Diaphoresis",
            "Nausea",
            "ECG changes (ST-segment elevation or depression, T-wave inversion)",
            "Elevated cardiac biomarkers (troponin)",
            "Killip classification for risk stratification"
        ],
        "recommendations": [
            "Electrocardiogram (ECG) immediately",
            "Cardiac biomarkers (troponin, CK-MB)",
            "Coronary angiography",
            "Percutaneous coronary intervention (PCI) if indicated",
            "Thrombolytic therapy (if PCI unavailable)",
            "Dual antiplatelet therapy (aspirin, clopidogrel)",
            "Beta-blockers, ACE inhibitors, and statins",
            "Oxygen supplementation",
            "Consider cardiac MRI for viability and scar assessment"
        ],
        "recent_research": "Emerging imaging biomarkers and AI-driven analysis are enhancing early MI detection and risk stratification.",
        "ml_insights": "Hybrid deep learning models are now used to predict infarct size and potential recovery based on imaging features."
    },
    "Heart Failure": {
        "imaging_descriptors": [
            "Cardiomegaly",
            "Pulmonary edema",
            "Pleural effusion",
            "Left ventricular dilation",
            "Reduced ejection fraction",
            "Mitral regurgitation",
            "Tricuspid regurgitation",
            "Diastolic dysfunction"  # New descriptor for HFpEF
        ],
        "risk_factors": [
            "Hypertension",
            "Coronary artery disease",
            "Valvular heart disease",
            "Cardiomyopathy",
            "Diabetes mellitus",
            "Alcohol abuse",
            "Family history"
        ],
        "epidemiology": "Increasing prevalence in aging populations; major cause of hospitalization and reduced quality of life.",
        "clinical_diagnostic_correlations": [
            "Dyspnea on exertion",
            "Fatigue",
            "Peripheral edema",
            "Orthopnea",
            "Paroxysmal nocturnal dyspnea",
            "Elevated BNP/NT-proBNP"
        ],
        "recommendations": [
            "Echocardiogram for structural assessment",
            "ECG and chest X-ray",
            "BNP or NT-proBNP testing",
            "Medical management with ACE inhibitors/ARBs, beta-blockers, and diuretics",
            "Aldosterone antagonists and digoxin in select cases",
            "SGLT2 inhibitors as emerging therapy",
            "Consider cardiac MRI for detailed tissue characterization"
        ],
        "recent_research": "Recent trials support the use of SGLT2 inhibitors in heart failure patients irrespective of diabetes status.",
        "ml_insights": "Predictive analytics using multi-modal imaging data are being integrated to forecast heart failure progression."
    },
    "Arrhythmia": {
        "Atrial Fibrillation (AF)": {
            "imaging_descriptors": [
                "Absence of P waves",
                "Irregularly irregular rhythm"
            ],
            "risk_factors": [
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
            "epidemiology": "The most common sustained arrhythmia with significant stroke risk.",
            "clinical_diagnostic_correlations": [
                "Palpitations",
                "Shortness of breath",
                "Fatigue",
                "Dizziness",
                "Chest discomfort",
                "Increased risk of thromboembolism"
            ],
            "recommendations": [
                "Electrocardiogram (ECG)",
                "24-hour Holter monitoring",
                "Event recorder monitoring",
                "Anticoagulation therapy (warfarin or DOACs)",
                "Rate control (beta-blockers, calcium channel blockers, digoxin)",
                "Rhythm control strategies (antiarrhythmic drugs, cardioversion, catheter ablation)",
                "Consider left atrial appendage closure for stroke prevention in selected patients"
            ],
            "recent_research": "Novel wearable ECG devices and AI algorithms are improving AF detection in ambulatory settings.",
            "ml_insights": "Recent studies demonstrate that AI can predict AF onset from subtle ECG variations not visible to the human eye."
        }
    }
}
