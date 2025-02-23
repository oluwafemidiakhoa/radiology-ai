# cardiology_differentials.py

cardiology_differentials = {
    "Myocardial Infarction (MI)": {
        "imaging_descriptors": [
            "Regional wall motion abnormality",
            "Reduced ejection fraction",
            "Late gadolinium enhancement (scarring)",
            "Coronary artery stenosis or occlusion",
            "Microvascular obstruction"  // New advanced descriptor
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
        "epidemiology": "Major cause of morbidity and mortality worldwide; early detection is critical",
        "clinical_diagnostic_correlations": [
            "Chest pain",
            "Shortness of breath",
            "Sweating",
            "Nausea",
            "ECG changes (ST-elevation, T-wave inversion)",
            "Elevated cardiac biomarkers (troponin)",
            "Killip classification"
        ],
        "recommendations": [
            "Electrocardiogram (ECG)",
            "Cardiac biomarkers (troponin)",
            "Coronary angiography",
            "Percutaneous coronary intervention (PCI)",
            "Thrombolysis (if PCI not available)",
            "Aspirin",
            "Clopidogrel",
            "Beta-blockers",
            "ACE inhibitors",
            "Statins",
            "Oxygen therapy",
            "Consider cardiac MRI for viability assessment"  // Additional advanced recommendation
        ]
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
            "Diastolic dysfunction"  // New descriptor for HFpEF
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
        "epidemiology": "Increasing prevalence with aging populations; major impact on quality of life",
        "clinical_diagnostic_correlations": [
            "Shortness of breath",
            "Fatigue",
            "Peripheral edema",
            "Orthopnea",
            "Paroxysmal nocturnal dyspnea",
            "Elevated BNP or NT-proBNP"
        ],
        "recommendations": [
            "Echocardiogram",
            "ECG",
            "Chest X-ray",
            "BNP or NT-proBNP measurement",
            "ACE inhibitors or ARBs",
            "Beta-blockers",
            "Diuretics",
            "Aldosterone antagonists",
            "Digoxin",
            "Sodium-glucose cotransporter 2 (SGLT2) inhibitors",
            "Cardiac MRI for further evaluation"  // Added advanced imaging recommendation
        ]
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
            "epidemiology": "Most common sustained arrhythmia; associated with significant stroke risk",
            "clinical_diagnostic_correlations": [
                "Palpitations",
                "Shortness of breath",
                "Fatigue",
                "Dizziness",
                "Chest pain",
                "Stroke"
            ],
            "recommendations": [
                "Electrocardiogram (ECG)",
                "Holter monitor",
                "Event monitor",
                "Anticoagulation (e.g., warfarin, DOACs)",
                "Rate control (beta-blockers, calcium channel blockers, digoxin)",
                "Rhythm control (antiarrhythmic drugs, cardioversion, catheter ablation)",
                "Consider left atrial appendage closure in selected patients"  // Advanced interventional option
            ]
        }
    }
}
