"""
Comprehensive Differential Diagnosis Dictionary for Medical Imaging

This dictionary covers advanced differential diagnosis considerations across
Radiology, Oncology, and Cardiology. Each major category includes subcategories,
detailed imaging descriptors, associated risk factors, relevant epidemiology,
and clinical/diagnostic correlations. This resource is intended for integration
into advanced AI diagnostic systems and should always be used in conjunction with
clinical evaluation and additional diagnostic testing.
"""

medical_differentials = {
    "Radiology": {
        "Musculoskeletal": {
            "Scoliosis": {
                "Idiopathic": {
                    "Description": "Most common form, typically seen in adolescents with right thoracic curves.",
                    "Imaging Features": "Cobb angle measurement, vertebral rotation on PA/lateral films.",
                    "Clinical Correlations": "May require bracing or surgery based on severity."
                },
                "Neuromuscular": {
                    "Description": "Associated with conditions like cerebral palsy and muscular dystrophy.",
                    "Imaging Features": "Asymmetric spinal curvature with pelvic obliquity.",
                    "Clinical Correlations": "Often part of a broader neuromuscular disorder workup."
                },
                "Congenital": {
                    "Description": "Due to vertebral malformations such as hemivertebrae or block vertebrae.",
                    "Imaging Features": "Segmental anomalies visible on AP/lateral radiographs.",
                    "Clinical Correlations": "May require surgical intervention if severe."
                },
                "Syndromic": {
                    "Description": "Seen with conditions such as neurofibromatosis, Marfan syndrome, or Klippel-Feil syndrome.",
                    "Imaging Features": "Associated systemic skeletal anomalies, abnormal vertebral segmentation.",
                    "Clinical Correlations": "Multidisciplinary evaluation recommended."
                },
                "Traumatic": {
                    "Description": "Resulting from acute or chronic injury to the spine.",
                    "Imaging Features": "Vertebral fractures, malalignment, possible pseudoarthrosis.",
                    "Clinical Correlations": "Management depends on stability and neurological involvement."
                }
            },
            "Osteoarthritis": {
                "Primary": {
                    "Description": "Degenerative joint disease due to age-related wear and tear.",
                    "Imaging Features": "Joint-space narrowing, osteophyte formation, subchondral sclerosis on X-ray.",
                    "Clinical Correlations": "Typically managed conservatively with physical therapy and NSAIDs."
                },
                "Secondary": {
                    "Description": "Resulting from prior trauma, inflammatory arthritis, or metabolic disorders.",
                    "Imaging Features": "Erosions, joint deformity, and possible calcifications.",
                    "Clinical Correlations": "May require surgical intervention or targeted medical therapy."
                }
            },
            "Fractures": {
                "Traumatic": {
                    "Description": "Due to high-impact injury or falls.",
                    "Imaging Features": "Displaced or non-displaced fractures, visible on X-ray or CT.",
                    "Clinical Correlations": "Management varies from casting to surgical fixation."
                },
                "Pathologic": {
                    "Description": "Occurs in bones weakened by conditions such as osteoporosis or malignancy.",
                    "Imaging Features": "Lytic or blastic lesions associated with fracture lines.",
                    "Clinical Correlations": "Requires further investigation (biopsy, lab tests) to determine underlying cause."
                },
                "Stress Fractures": {
                    "Description": "Microfractures due to repetitive stress, common in athletes.",
                    "Imaging Features": "Subtle periosteal reaction or cortical lucencies; best seen on MRI or bone scan.",
                    "Clinical Correlations": "Often managed with rest and modified activity."
                }
            }
        },
        "Pulmonary": {
            "Pneumonia": {
                "Bacterial": {
                    "Description": "Infection causing consolidation of lung tissue.",
                    "Imaging Features": "Lobar consolidation, air bronchograms on CXR or CT.",
                    "Clinical Correlations": "Often treated with antibiotics; sputum cultures may guide therapy."
                },
                "Viral": {
                    "Description": "Interstital pneumonia caused by respiratory viruses.",
                    "Imaging Features": "Diffuse interstitial infiltrates, ground-glass opacities on CT.",
                    "Clinical Correlations": "Management is usually supportive; severity varies."
                },
                "Fungal": {
                    "Description": "Typically occurs in immunocompromised patients.",
                    "Imaging Features": "Nodular opacities, cavitation, possible halo sign on CT.",
                    "Clinical Correlations": "Requires antifungal therapy and immune status assessment."
                },
                "Aspiration": {
                    "Description": "Infection due to inhalation of foreign materials, often in debilitated patients.",
                    "Imaging Features": "Infiltrates in dependent lung regions, often right lower lobe.",
                    "Clinical Correlations": "Management includes supportive care and addressing underlying risk factors."
                }
            },
            "Pulmonary Embolism": {
                "Thromboembolic": {
                    "Description": "Obstruction of pulmonary arteries by blood clots.",
                    "Imaging Features": "CT Pulmonary Angiography (CTPA) shows filling defects; ventilation-perfusion scan may be used.",
                    "Clinical Correlations": "Requires prompt anticoagulation therapy."
                },
                "Fat Embolism": {
                    "Description": "Typically secondary to long bone fractures.",
                    "Imaging Features": "Diffuse bilateral infiltrates on chest imaging; clinical symptoms include petechial rash.",
                    "Clinical Correlations": "Management is supportive; consider in trauma cases."
                },
                "Septic Embolism": {
                    "Description": "Emboli resulting from infectious sources, e.g., endocarditis.",
                    "Imaging Features": "Multiple peripheral nodules, sometimes cavitary, on CT.",
                    "Clinical Correlations": "Requires antibiotic therapy and source control."
                }
            },
            "Lung Cancer": {
                "Non-Small Cell Lung Cancer (NSCLC)": {
                    "Adenocarcinoma": {
                        "Description": "Often peripheral, may present as ground-glass nodules or solid masses.",
                        "Imaging Features": "CT shows spiculated margins, pleural retraction.",
                        "Clinical Correlations": "Associated with smoking, but also seen in non-smokers."
                    },
                    "Squamous Cell Carcinoma": {
                        "Description": "Typically central, may cavitate.",
                        "Imaging Features": "Central mass with cavitation; often linked with smoking.",
                        "Clinical Correlations": "Requires tissue biopsy for definitive diagnosis."
                    },
                    "Large Cell Carcinoma": {
                        "Description": "Aggressive, poorly differentiated carcinoma.",
                        "Imaging Features": "Peripheral mass without clear features; may be rapidly growing.",
                        "Clinical Correlations": "Often detected at an advanced stage."
                    }
                },
                "Small Cell Lung Cancer (SCLC)": {
                    "Description": "Highly aggressive with early metastasis.",
                    "Imaging Features": "Mediastinal involvement, bulky lymphadenopathy on CT.",
                    "Clinical Correlations": "Requires systemic chemotherapy and radiotherapy."
                },
                "Metastatic Lung Cancer": {
                    "Description": "Secondary involvement from a primary tumor elsewhere (e.g., breast, colon).",
                    "Imaging Features": "Multiple nodules of varying sizes on CT.",
                    "Clinical Correlations": "Determining the primary is key; PET-CT may help in staging."
                }
            },
            "Vascular": {
                "Aortic Dissection": {
                    "Description": "Tear in the intima leading to separation of aortic wall layers.",
                    "Imaging Features": "CT angiography shows intimal flap, false lumen.",
                    "Clinical Correlations": "Requires emergent surgical management."
                },
                "Aneurysms": {
                    "Description": "Localized dilation of the aorta or other vessels.",
                    "Imaging Features": "CT or ultrasound demonstrates abnormal vessel diameter.",
                    "Clinical Correlations": "Monitoring and surgical repair depending on size and risk."
                }
            }
        },
        "Neurological": {
            "Stroke": {
                "Ischemic": {
                    "Description": "Blockage of a cerebral vessel causing brain tissue infarction.",
                    "Imaging Features": "Early CT can be normal; MRI diffusion-weighted imaging (DWI) is sensitive.",
                    "Clinical Correlations": "Time-sensitive treatment is required; thrombolysis may be indicated."
                },
                "Hemorrhagic": {
                    "Description": "Bleeding within the brain parenchyma or subarachnoid space.",
                    "Imaging Features": "CT shows hyperdense regions corresponding to blood.",
                    "Clinical Correlations": "Requires rapid management to control intracranial pressure."
                }
            },
            "Neurodegenerative": {
                "Alzheimer's Disease": {
                    "Description": "Progressive memory loss and cognitive decline.",
                    "Imaging Features": "MRI shows cortical atrophy, particularly in the medial temporal lobes.",
                    "Clinical Correlations": "Diagnosis confirmed via neuropsychological testing and biomarkers."
                },
                "Parkinson's Disease": {
                    "Description": "Movement disorder characterized by bradykinesia, rigidity, and tremors.",
                    "Imaging Features": "DATscan can help assess dopaminergic neuron loss.",
                    "Clinical Correlations": "Clinical diagnosis with supportive imaging if necessary."
                },
                "Multiple Sclerosis": {
                    "Description": "Autoimmune demyelinating disorder of the CNS.",
                    "Imaging Features": "MRI demonstrates multiple T2/FLAIR hyperintense lesions.",
                    "Clinical Correlations": "Diagnosis requires clinical history and supportive lab findings (e.g., oligoclonal bands)."
                }
            },
            "Traumatic Brain Injury": {
                "Concussion": {
                    "Description": "Mild traumatic brain injury, usually with transient symptoms.",
                    "Imaging Features": "CT often normal; MRI may reveal subtle diffuse axonal injury.",
                    "Clinical Correlations": "Clinical evaluation is key; imaging used to rule out severe injury."
                },
                "Contusion": {
                    "Description": "Focal brain bruising from impact.",
                    "Imaging Features": "CT shows patchy hyperdensities; MRI is more sensitive for smaller contusions.",
                    "Clinical Correlations": "Monitoring for progression or secondary injury is critical."
                }
            }
        },
        "Gastrointestinal": {
            "Inflammatory Bowel Disease": {
                "Crohn's Disease": {
                    "Description": "Transmural inflammation with skip lesions.",
                    "Imaging Features": "Barium studies show 'string sign'; CT/MRI may show bowel wall thickening.",
                    "Clinical Correlations": "Endoscopy and biopsy confirm diagnosis."
                },
                "Ulcerative Colitis": {
                    "Description": "Mucosal inflammation starting at the rectum and extending proximally.",
                    "Imaging Features": "CT may show diffuse colonic thickening; colonoscopy is diagnostic.",
                    "Clinical Correlations": "Management includes 5-ASA compounds and steroids."
                }
            },
            "Liver Lesions": {
                "Hepatocellular Carcinoma (HCC)": {
                    "Description": "Primary liver cancer, often in a cirrhotic liver.",
                    "Imaging Features": "Arterial phase hyperenhancement with washout in portal venous/delayed phase on CT/MRI.",
                    "Clinical Correlations": "AFP levels and biopsy are key for diagnosis."
                },
                "Hemangioma": {
                    "Description": "Benign vascular liver lesion.",
                    "Imaging Features": "Peripheral nodular enhancement with progressive centripetal fill-in on CT/MRI.",
                    "Clinical Correlations": "Usually requires no treatment if asymptomatic."
                },
                "Focal Nodular Hyperplasia (FNH)": {
                    "Description": "Benign lesion with a central scar.",
                    "Imaging Features": "Central scar and radiating vessels on contrast-enhanced MRI.",
                    "Clinical Correlations": "Typically requires monitoring unless symptomatic."
                }
            },
            "Pancreatic Pathologies": {
                "Pancreatitis": {
                    "Description": "Inflammation of the pancreas, acute or chronic.",
                    "Imaging Features": "CT shows pancreatic enlargement, peripancreatic fat stranding; chronic form may show calcifications.",
                    "Clinical Correlations": "Lab values (amylase, lipase) help confirm the diagnosis."
                },
                "Pancreatic Adenocarcinoma": {
                    "Description": "Most common malignant pancreatic tumor, often in the head of the pancreas.",
                    "Imaging Features": "CT/MRI may show a hypovascular mass with ductal dilatation (double duct sign).",
                    "Clinical Correlations": "Poor prognosis; diagnosis confirmed with biopsy."
                }
            }
        },
        "Oncology": {
            "Lung Cancer": {
                "Non-Small Cell Lung Cancer (NSCLC)": {
                    "Adenocarcinoma": {
                        "Description": "Often presents peripherally, may appear as ground-glass opacities or solid masses.",
                        "Imaging Features": "Spiculated margins, possible pleural retraction on CT.",
                        "Clinical Correlations": "Associated with smoking and genetic mutations (EGFR, ALK)."
                    },
                    "Squamous Cell Carcinoma": {
                        "Description": "Typically central with cavitation, linked to smoking.",
                        "Imaging Features": "Central mass with possible cavitation; mediastinal lymphadenopathy may be present.",
                        "Clinical Correlations": "Requires tissue confirmation; often treated with surgery or chemoradiation."
                    },
                    "Large Cell Carcinoma": {
                        "Description": "Undifferentiated and aggressive, often peripheral.",
                        "Imaging Features": "Rapidly growing mass without clear differentiation on imaging.",
                        "Clinical Correlations": "Poor prognosis; often detected at advanced stages."
                    }
                },
                "Small Cell Lung Cancer (SCLC)": {
                    "Description": "Highly aggressive, early metastases with mediastinal involvement.",
                    "Imaging Features": "Bulky mediastinal lymphadenopathy and rapid progression on imaging.",
                    "Clinical Correlations": "Requires systemic therapy; often combined with radiotherapy."
                },
                "Metastatic Lung Cancer": {
                    "Description": "Secondary lung involvement from a primary tumor elsewhere (e.g., breast, colon).",
                    "Imaging Features": "Multiple nodules of varying sizes; PET-CT may be used for further evaluation.",
                    "Clinical Correlations": "Identifying the primary is crucial; management is usually systemic."
                }
            },
            "Breast Cancer": {
                "Invasive Ductal Carcinoma (IDC)": {
                    "Description": "Most common type; often presents as a spiculated mass.",
                    "Imaging Features": "Mammogram shows spiculated, irregular mass with possible calcifications.",
                    "Clinical Correlations": "Diagnosis confirmed by biopsy; treatment involves surgery and adjuvant therapy."
                },
                "Invasive Lobular Carcinoma (ILC)": {
                    "Description": "Often multifocal and bilateral, with subtle imaging features.",
                    "Imaging Features": "Architectural distortion on mammogram; may be better delineated with MRI.",
                    "Clinical Correlations": "Can be more challenging to detect; requires thorough clinical and imaging evaluation."
                },
                "Ductal Carcinoma In Situ (DCIS)": {
                    "Description": "Non-invasive cancer confined to the ducts.",
                    "Imaging Features": "Microcalcifications on mammogram are classic.",
                    "Clinical Correlations": "Usually managed with lumpectomy and radiation; high risk for progression if untreated."
                }
            },
            "Colorectal Cancer": {
                "Adenocarcinoma": {
                    "Description": "The most common type; arises from adenomatous polyps.",
                    "Imaging Features": "CT colonography may reveal polypoid lesions; colonoscopy is definitive.",
                    "Clinical Correlations": "Early detection is key; screening programs are effective in reducing mortality."
                },
                "Signet Ring Cell Carcinoma": {
                    "Description": "Aggressive, characterized by mucin production.",
                    "Imaging Features": "May present with diffuse wall thickening and linitis plastica on imaging.",
                    "Clinical Correlations": "Poor prognosis; often diagnosed at an advanced stage."
                }
            },
            "Brain Tumors": {
                "Glioblastoma Multiforme (GBM)": {
                    "Description": "High-grade astrocytoma, aggressive, with rapid growth.",
                    "Imaging Features": "Ring-enhancing lesion with central necrosis on contrast-enhanced MRI.",
                    "Clinical Correlations": "Very poor prognosis; multimodal treatment is required."
                },
                "Meningioma": {
                    "Description": "Typically benign, extra-axial tumor arising from the meninges.",
                    "Imaging Features": "Dural tail sign, well-circumscribed mass on MRI with contrast.",
                    "Clinical Correlations": "Often incidental findings; may require surgical resection if symptomatic."
                },
                "Pituitary Adenoma": {
                    "Description": "Common benign tumor of the pituitary gland.",
                    "Imaging Features": "Enlarged sella turcica, often with suprasellar extension on MRI.",
                    "Clinical Correlations": "Hormonal evaluation is essential; treatment options include medical therapy and surgery."
                }
            }
        },
        "Cardiology": {
            "Coronary Artery Disease (CAD)": {
                "Stable Angina": {
                    "Description": "Predictable chest pain on exertion due to myocardial ischemia.",
                    "Imaging Features": "Stress testing, coronary CT angiography (CCTA) reveals stenosis.",
                    "Clinical Correlations": "Managed medically with nitrates and beta-blockers."
                },
                "Unstable Angina": {
                    "Description": "Worsening chest pain at rest; high risk for myocardial infarction.",
                    "Imaging Features": "May have non-specific ECG changes; clinical biomarkers are critical.",
                    "Clinical Correlations": "Requires hospitalization and aggressive therapy."
                },
                "Myocardial Infarction (MI)": {
                    "Description": "Acute ischemia resulting in myocardial injury.",
                    "Imaging Features": "STEMI or NSTEMI patterns on ECG; imaging (echo, CMR) assesses infarct size.",
                    "Clinical Correlations": "Immediate reperfusion therapy is necessary."
                }
            },
            "Heart Failure": {
                "Systolic Heart Failure (HFrEF)": {
                    "Description": "Reduced left ventricular ejection fraction (<40%).",
                    "Imaging Features": "Echocardiography shows global hypokinesis, dilated ventricle.",
                    "Clinical Correlations": "Managed with ACE inhibitors, beta-blockers, and diuretics."
                },
                "Diastolic Heart Failure (HFpEF)": {
                    "Description": "Preserved ejection fraction with impaired ventricular relaxation.",
                    "Imaging Features": "Echocardiography shows normal EF but abnormal diastolic filling patterns.",
                    "Clinical Correlations": "Treatment focuses on controlling blood pressure and comorbidities."
                }
            },
            "Valvular Heart Disease": {
                "Aortic Stenosis": {
                    "Description": "Calcification and narrowing of the aortic valve.",
                    "Imaging Features": "Echocardiography shows a high transvalvular gradient, calcification, and LV hypertrophy.",
                    "Clinical Correlations": "Surgical or transcatheter aortic valve replacement (TAVR) may be indicated."
                },
                "Mitral Regurgitation": {
                    "Description": "Leakage of blood backward through the mitral valve.",
                    "Imaging Features": "Doppler echocardiography reveals regurgitant flow; LV enlargement may be evident.",
                    "Clinical Correlations": "May require surgical repair or replacement if severe."
                }
            },
            "Arrhythmias": {
                "Atrial Fibrillation": {
                    "Description": "Irregularly irregular rhythm with rapid ventricular response.",
                    "Imaging Features": "ECG shows absence of P waves; echocardiography assesses for atrial enlargement.",
                    "Clinical Correlations": "Anticoagulation is important to prevent stroke."
                },
                "Ventricular Tachycardia": {
                    "Description": "Life-threatening arrhythmia with wide QRS complexes.",
                    "Imaging Features": "ECG and cardiac MRI can help localize scarring that predisposes to VT.",
                    "Clinical Correlations": "May require ICD placement and antiarrhythmic therapy."
                },
                "Supraventricular Tachycardia (SVT)": {
                    "Description": "Rapid heart rate originating above the ventricles.",
                    "Imaging Features": "ECG shows narrow complex tachycardia; vagal maneuvers may transiently slow the rate.",
                    "Clinical Correlations": "Catheter ablation is an option for recurrent SVT."
                }
            },
            "Congenital Heart Disease": {
                "Atrial Septal Defect (ASD)": {
                    "Description": "Abnormal opening in the atrial septum, leading to left-to-right shunt.",
                    "Imaging Features": "Echocardiography shows septal defect with shunting; bubble study may be positive.",
                    "Clinical Correlations": "Often monitored until surgical repair is indicated."
                },
                "Ventricular Septal Defect (VSD)": {
                    "Description": "Opening in the interventricular septum causing shunting.",
                    "Imaging Features": "Holosystolic murmur on auscultation; echocardiography confirms defect size and shunt flow.",
                    "Clinical Correlations": "Small defects may close spontaneously; larger ones require surgical repair."
                },
                "Tetralogy of Fallot": {
                    "Description": "A combination of four heart defects including VSD and pulmonary stenosis.",
                    "Imaging Features": "CXR shows a 'boot-shaped' heart; echocardiography confirms details.",
                    "Clinical Correlations": "Surgical repair is required in infancy or early childhood."
                }
            }
        }
    }
}
