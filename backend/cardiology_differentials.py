# cardiology_differentials.py
# Advanced Cardiology Differential Diagnosis Dictionary
# This module contains detailed diagnostic criteria, imaging features, risk factors, and recommendations for key cardiac conditions.

cardiology_differentials = {
    "Myocardial Infarction (MI)": {
        "imaging_descriptors": [
            "Regional wall motion abnormality",
            "Reduced ejection fraction",
            "Late gadolinium enhancement (scarring)",
            "Coronary artery stenosis or occlusion",
            "Microvascular obstruction"
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
        "epidemiology": "A leading cause of morbidity and mortality worldwide; early detection is critical for improving outcomes.",
        "clinical_diagnostic_correlations": [
            "Chest pain",
            "Shortness of breath",
            "Diaphoresis",
            "Nausea",
            "ECG changes (ST-segment elevation/depression, T-wave inversion)",
            "Elevated cardiac biomarkers (troponin)",
            "Killip classification for risk stratification"
        ],
        "recommendations": [
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
        "recent_research": "Emerging imaging biomarkers and AI-driven analysis are enhancing early MI detection and risk stratification.",
        "ml_insights": "Hybrid deep learning models predict infarct size and potential recovery with high accuracy."
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
            "Diastolic dysfunction"
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
        "epidemiology": "Increasing prevalence among aging populations with significant morbidity.",
        "clinical_diagnostic_correlations": [
            "Dyspnea on exertion",
            "Fatigue",
            "Peripheral edema",
            "Orthopnea",
            "Paroxysmal nocturnal dyspnea",
            "Elevated BNP or NT-proBNP"
        ],
        "recommendations": [
            "Echocardiogram for structural and functional assessment",
            "ECG and chest X-ray",
            "BNP/NT-proBNP measurement",
            "Pharmacologic management (ACE inhibitors/ARBs, beta-blockers, diuretics)",
            "Aldosterone antagonists and digoxin in select cases",
            "SGLT2 inhibitors",
            "Cardiac MRI for detailed tissue characterization"
        ],
        "recent_research": "Recent clinical trials support SGLT2 inhibitors in heart failure irrespective of diabetic status.",
        "ml_insights": "Predictive analytics using multi-modal imaging data now forecast heart failure progression."
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
            "epidemiology": "The most common sustained arrhythmia; significant risk for stroke.",
            "clinical_diagnostic_correlations": [
                "Palpitations",
                "Shortness of breath",
                "Fatigue",
                "Dizziness",
                "Chest discomfort",
                "Thromboembolic events"
            ],
            "recommendations": [
                "ECG for initial detection",
                "24-hour Holter monitoring",
                "Event recorder monitoring",
                "Anticoagulation therapy",
                "Rate control with beta-blockers or calcium channel blockers",
                "Rhythm control strategies (medications, cardioversion, ablation)",
                "Consider left atrial appendage closure in selected patients"
            ],
            "recent_research": "Emerging wearable ECG devices and AI algorithms are enhancing early AF detection.",
            "ml_insights": "Recent studies show AI can predict the onset of AF from subtle ECG variations."
        }
    }
}
