# differentials.py
"""
Comprehensive differential diagnosis lists for Radiology, Oncology, and Cardiology.
Each category is organized with potential findings or associated image features (if applicable).
"""

medical_differentials = {
    "Radiology": {
        "Musculoskeletal": {
            "Scoliosis": {
                "Idiopathic": "Most common, adolescent onset",
                "Neuromuscular": "Associated with cerebral palsy, muscular dystrophy",
                "Congenital": "Vertebral malformations (hemivertebra, block vertebra)",
                "Syndromic": "Neurofibromatosis, Marfan syndrome",
                "Traumatic": "Vertebral fracture, spinal cord injury"
            },
            "Osteoarthritis": {
                "Primary": "Age-related wear and tear",
                "Secondary": "Trauma, infection, inflammatory conditions"
            },
            "Fractures": {
                "Traumatic": "High-energy impact, fall",
                "Pathologic": "Underlying bone disease (osteoporosis, cancer)"
            }
        },
        "Pulmonary": {
            "Pneumonia": {
                "Bacterial": "Lobar consolidation, air bronchograms",
                "Viral": "Interstitial infiltrates",
                "Fungal": "Nodules, cavitation",
                "Aspiration": "Infiltrates in dependent lung regions"
            },
            "Pulmonary Embolism": {
                "Thromboembolic": "DVT, Virchow's triad",
                "Fat Embolism": "Long bone fractures",
                "Septic Embolism": "Infection, IV drug use"
            },
            "Lung Cancer": {
                "Non-Small Cell Lung Cancer (NSCLC)": "Adenocarcinoma, squamous cell carcinoma",
                "Small Cell Lung Cancer (SCLC)": "Aggressive, often with mediastinal involvement"
            }
        },
        "Neurological": {
            "Stroke": {
                "Ischemic": "Blockage in blood vessel.",
                "Hemorrhagic": "bleeding in blood vessel"
            }
        }
    },
    "Oncology": {
        "Lung Cancer": {
            "Non-Small Cell Lung Cancer (NSCLC)": {
                "Adenocarcinoma": "Most common, often peripheral",
                "Squamous Cell Carcinoma": "Central, associated with smoking",
                "Large Cell Carcinoma": "Aggressive, poorly differentiated"
            },
            "Small Cell Lung Cancer (SCLC)": "Aggressive, often with mediastinal involvement",
            "Metastatic Lung Cancer": "Spread from other primary sites"
        },
        "Breast Cancer": {
            "Invasive Ductal Carcinoma (IDC)": "Most common type",
            "Invasive Lobular Carcinoma (ILC)": "Often multifocal and bilateral",
            "Ductal Carcinoma In Situ (DCIS)": "Non-invasive, confined to milk ducts"
        },
        "Colorectal Cancer": {
            "Adenocarcinoma": "Most common type",
            "Signet Ring Cell Carcinoma": "Aggressive, mucin production"
        }
    },
    "Cardiology": {
        "Coronary Artery Disease (CAD)": {
            "Stable Angina": "Predictable chest pain with exertion",
            "Unstable Angina": "New or worsening chest pain",
            "Myocardial Infarction (MI)": "Heart attack, ST-segment elevation or non-ST-segment elevation"
        },
        "Heart Failure": {
            "Systolic Heart Failure (HFrEF)": "Reduced ejection fraction",
            "Diastolic Heart Failure (HFpEF)": "Preserved ejection fraction, impaired relaxation"
        },
        "Valvular Heart Disease": {
            "Aortic Stenosis": "Narrowing of the aortic valve",
            "Mitral Regurgitation": "Leakage of blood backward through the mitral valve"
        }
    }
}