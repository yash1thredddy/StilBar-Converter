#!/usr/bin/env python3
"""
Create a perfect CSV file with proper compound names from the PDF
"""

import csv

def create_perfect_csv():
    """Create the perfect CSV with clean names and proper formatting"""
    
    # Perfect compound data with proper names from PDF
    compounds = [
        (1, "Wolfender2024_PhenoxyRadicalCoupling_cpd10", "H", "OC1=CC(O)=CC(CCC2=CC=C(O)C=C2)=C1"),
        (2, "Wolfender2024_PhenoxyRadicalCoupling_cpd11", "H–77–H", "OC1=CC=C(CCC2=C(C3=C(CCC4=CC=C(O)C=C4)C=C(O)C=C3O)C(O)=CC(O)=C2)C=C1"),
        (3, "Wolfender2024_PhenoxyRadicalCoupling_cpd12", "H–17–H", "OC1=CC=C(CCC2=CC(O)=CC(O)=C2)C=C1C3=C(CCC4=CC=C(O)C=C4)C=C(O)C=C3O"),
        (4, "Wolfender2024_PhenoxyRadicalCoupling_cpd13", "H–11–H", "OC1=CC(O)=CC(CCC2=CC(C3=C(O)C=CC(CCC4=CC(O)=CC(O)=C4)=C3)=C(O)C=C2)=C1"),
        (5, "Wolfender2024_PhenoxyRadicalCoupling_cpd14", "H–07–H", "OC1=CC(O)=CC(CCC2=CC=C(OC3=C(CCC4=CC=C(O)C=C4)C=C(O)C=C3O)C=C2)=C1"),
        (6, "Wolfender2024_PhenoxyRadicalCoupling_cpd15", "H|–02r.13r–|H", "OC1=CC(CCC2=CC3=C(C=C2)O[C@@]4([H])[C@]3(CCC5=CC(O)=CC(O)=C5)C=CC(C4)=O)=CC(O)=C1"),
        (7, "Wolfender2024_PhenoxyRadicalCoupling_cpd16", "H|–02r.13r–|H", "OC(C=C1O)=CC2=C1C(CC(C3)=O)C4(CC2)C3OC5=C4C=C(CCC6=CC(O)=CC(O)=C6)C=C5"),
        (8, "trans-δ-Viniferin", "T|–04r.15r–|H", "OC(C=C1)=CC=C1[C@H](O2)[C@H](C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4"),
        (9, "Wolfender2022_ChiralStilbenes_cpd2", "T|–04r.15r–|P", "OC(C=C1)=CC=C1[C@H](O2)[C@H](C3=CC(OC)=CC(OC)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4"),
        (10, "Wolfender2022_ChiralStilbenes_cpd3", "P|–04r.15r–|H", "OC(C=C1)=CC=C1[C@H](O2)[C@H](C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(OC)=CC(OC)=C5)=C4"),
        (11, "Wolfender2022_ChiralStilbenes_cpd4", "P|–04r.15r–|P", "OC(C=C1)=CC=C1[C@H](O2)[C@H](C3=CC(OC)=CC(OC)=C3)C4=C2C=CC(/C=C/C5=CC(OC)=CC(OC)=C5)=C4"),
        (12, "Pallidol", "H≡4r7.5r5r.74r≡H", "[H][C@@]1([C@@H](C2=C3C=C(C=C2O)O)C(C=C4)=CC=C4O)C5=C([C@H]([C@@]13[H])C(C=C6)=CC=C6O)C(O)=CC(O)=C5"),
        (13, "Wolfender2022_ChiralStilbenes_cpd6", "T|05s|4shH", "OC1=CC(O)=CC(/C=C/C2=CC=C(O[C@H]([C@@H](O)C3=CC=C(O)C=C3)C4=CC(O)=CC(O)=C4)C=C2)=C1"),
        (14, "Wolfender2022_ChiralStilbenes_cpd7", "P=4s7.5r5s=4riH", "[H][C@](C(C=C(O)C=C1O)=C1[C@@H]2C3=CC=C(O)C=C3)([C@](OC(C)C)([H])C4=CC=C(O)C=C4)[C@@H]2C5=CC(OC)=CC(OC)=C5"),
        (15, "Wolfender2022_ChiralStilbenes_cpd8", "P|–4s4r.5s5s–|P", "OC(C=C1)=CC=C1[C@H]2O[C@@H](C3=CC=C(O)C=C3)[C@H](C4=CC(OC)=CC(OC)=C4)[C@H]2C5=CC(OC)=CC(OC)=C5"),
        (16, "Wolfender2020_StilbeneAntimicrobials_cpd2", "H=4s7.5r5s=4*mH", "OC1=CC(O)=CC([C@H]2[C@@]([C@H](C(C=C3)=CC=C3O)OC)([H])C(C=C(O)C=C4O)=C4[C@@H]2C5=CC=C(O)C=C5)=C1"),
        (17, "Wolfender2020_StilbeneAntimicrobials_cpd3", "P=4s7.5r5s=4*hH", "OC1=CC=C([C@H](O)[C@@](C(C=C(O)C=C2O)=C2[C@@H]3C4=CC=C(O)C=C4)([H])[C@@H]3C5=CC(OC)=CC(OC)=C5)C=C1"),
        (18, "Wolfender2020_StilbeneAntimicrobials_cpd4", "", "OC1=CC(O)=CC([C@@H](C(C2=CC=C(O)C=C2)C3=CC=C(O)C=C3)[C@H](C(OC)OC)C4=CC(OC)=CC(OC)=C4)=C1"),
        (19, "Wolfender2020_StilbeneAntimicrobials_cpd5", "P=4s7.5r5s=4rmH", "OC1=CC=C([C@H](OC)[C@@](C(C=C(O)C=C2O)=C2[C@@H]3C4=CC=C(O)C=C4)([H])[C@@H]3C5=CC(OC)=CC(OC)=C5)C=C1"),
        (20, "Wolfender2020_StilbeneAntimicrobials_cpd7", "H=4s7.5r5s=4rmP", "OC1=CC(O)=CC([C@H]2[C@@]([C@H](C(C=C3)=CC=C3O)OC)([H])C(C=C(OC)C=C4OC)=C4[C@@H]2C5=CC=C(O)C=C5)=C1"),
        (21, "Wolfender2020_StilbeneAntimicrobials_cpd8", "P=4s7.5r5s=4smH", "OC1=CC=C([C@@H](OC)[C@@](C(C=C(O)C=C2O)=C2[C@@H]3C4=CC=C(O)C=C4)([H])[C@@H]3C5=CC(OC)=CC(OC)=C5)C=C1"),
        (22, "Wolfender2020_StilbeneAntimicrobials_cpd9", "", "OC(C=C1)=CC=C1C(C2=CC=C(O)C=C2)[C@@H]([C@H](C(OC)OC)C3=CC(OC)=CC(OC)=C3)C4=CC(OC)=CC(OC)=C4"),
        (23, "Wolfender2020_StilbeneAntimicrobials_cpd10", "T|05*|4*mP", "OC(C=C1)=CC=C1[C@@H](OC)[C@@H](C2=CC(OC)=CC(OC)=C2)OC(C=C3)=CC=C3/C=C/C4=CC(O)=CC(O)=C4"),
        (24, "Wolfender2020_StilbeneAntimicrobials_cpd11", "T|–04s.15s–|P", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(OC)=CC(OC)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4"),
        (25, "Wolfender2020_StilbeneAntimicrobials_cpd12", "P|05*|4*mT", "OC1=CC([C@H]([C@H](OC)C2=CC=C(O)C=C2)OC(C=C3)=CC=C3/C=C/C4=CC(OC)=CC(OC)=C4)=CC(O)=C1"),
        (26, "Wolfender2020_StilbeneAntimicrobials_cpd13", "P=4s7.5r5s=4rmP", "OC1=CC=C([C@H](OC)[C@@](C(C=C(OC)C=C2OC)=C2[C@@H]3C4=CC=C(O)C=C4)([H])[C@@H]3C5=CC(OC)=CC(OC)=C5)C=C1"),
        (27, "Wolfender2020_StilbeneAntimicrobials_cpd14", "P|–04s.15s–|T", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(OC)=CC(OC)=C5)=C4"),
        (28, "Wolfender2020_StilbeneAntimicrobials_cpd15", "P|–04s.15s–|P", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(OC)=CC(OC)=C3)C4=C2C=CC(/C=C/C5=CC(OC)=CC(OC)=C5)=C4"),
        (29, "Wolfender2020_StilbeneAntimicrobials_cpd16", "P≡4r7.5r5r.74r≡P", "[H][C@@]1([C@@H](C2=C3C=C(C=C2OC)OC)C(C=C4)=CC=C4O)C5=C([C@H]([C@@]13[H])C(C=C6)=CC=C6O)C(OC)=CC(OC)=C5"),
        (30, "Wolfender2020_StilbeneAntimicrobials_cpd18", "P=4s7.5r5s=4rhP", "OC1=CC=C([C@H](O)[C@@](C(C=C(OC)C=C2OC)=C2[C@@H]3C4=CC=C(O)C=C4)([H])[C@@H]3C5=CC(OC)=CC(OC)=C5)C=C1"),
        (31, "Wolfender2020_StilbeneAntimicrobials_cpd19", "P=4s7.5r5s=4shP", "OC1=CC=C([C@@H](O)[C@@](C(C=C(OC)C=C2OC)=C2[C@@H]3C4=CC=C(O)C=C4)([H])[C@@H]3C5=CC(OC)=CC(OC)=C5)C=C1"),
        (32, "Wolfender2020_StilbeneAntimicrobials_cpd20", "P|05*|4*hP", "OC(C=C1)=CC=C1C(O)C(C2=CC(OC)=CC(OC)=C2)OC(C=C3)=CC=C3/C=C/C4=CC(OC)=CC(OC)=C4"),
        (33, "Wolfender2023_tDViniferinsAntibacterials_cpd5", "C|–04s.15s–|H", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C\\C5=CC(O)=CC(O)=C5)=C4"),
        (34, "Wolfender2023_tDViniferinsAntibacterials_cpd6", "C|–04s.15s–|P", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(OC)=CC(OC)=C3)C4=C2C=CC(/C=C\\C5=CC(O)=CC(O)=C5)=C4"),
        (35, "Wolfender2023_tDViniferinsAntibacterials_cpd8", "C|–04s.15s–|P", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(OC)=CC(OC)=C3)C4=C2C=CC(/C=C\\C5=CC(OC)=CC(OC)=C5)=C4"),
        (36, "Wolfender2023_tDViniferinsAntibacterials_cpd9", "T|–04s.15s–|P", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(OC)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4"),
        (37, "Wolfender2023_tDViniferinsAntibacterials_cpd10", "T|–04s.15s–|X", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(OC)=CC(O)=C5)=C4"),
        (38, "Wolfender2023_tDViniferinsAntibacterials_cpd11", "M|–04s.15s–|T", "OC1=CC([C@@H]([C@H](C2=CC=C(OC)C=C2)O3)C4=C3C=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4)=CC(O)=C1"),
        (39, "Wolfender2023_tDViniferinsAntibacterials_cpd15", "1mH|–04s.15s–|1mH", "OC(C=C1)=C(OC)C=C1[C@@H](O2)[C@@H](C3=CC(O)=CC(O)=C3)C4=C2C(OC)=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4"),
        (40, "Wolfender2023_tDViniferinsAntibacterials_cpd16", "T|–04.15–|T", "OC(C=C1)=CC=C1C(O2)=C(C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5)=C4"),
        (41, "Wolfender2023_tDViniferinsAntibacterials_cpd19", "P|–04.15–|P", "OC(C=C1)=CC=C1C(O2)=C(C3=CC(OC)=CC(OC)=C3)C4=C2C=CC(/C=C/C5=CC(OC)=CC(OC)=C5)=C4"),
        (42, "Wolfender2023_tDViniferinsAntibacterials_cpd21", "7BrH|–04s.15s–|7BrT", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=C(Br)C(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5Br)=C4"),
        (43, "Wolfender2023_tDViniferinsAntibacterials_cpd23", "7ClH|–04s.15s–|7ClT", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=C(Cl)C(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(O)=CC(O)=C5Cl)=C4"),
        (44, "Wolfender2023_tDViniferinsAntibacterials_cpd25", "H|–04s.15s–|9IT", "OC(C=C1)=CC=C1[C@@H](O2)[C@@H](C3=CC(O)=CC(O)=C3)C4=C2C=CC(/C=C/C5=CC(O)=C(I)C(O)=C5)=C4"),
        (45, "Wolfender2025_AntiinfectStilbenoids_cpd1", "2hH|–4r8.5r9–|T", "OC1=C([C@@H](C2=CC(O)=CC(O)=C2)[C@H](C3=CC=C(O)C=C3O)O4)C4=CC(/C=C/C5=CC=C(O)C=C5)=C1"),
        (46, "Wolfender2025_AntiinfectStilbenoids_cpd2", "2hH|–4s8.5r9–|T", "OC1=C([C@@H](C2=CC(O)=CC(O)=C2)[C@@H](C3=CC=C(O)C=C3O)O4)C4=CC(/C=C/C5=CC=C(O)C=C5)=C1"),
        (47, "Wolfender2025_AntiinfectStilbenoids_cpd3", "2hH|–4s8.5s9–|T", "OC1=C([C@H](C2=CC(O)=CC(O)=C2)[C@@H](C3=CC=C(O)C=C3)O4)C4=CC(/C=C/C5=CC=C(O)C=C5)=C1"),
        (48, "Wolfender2025_AntiinfectStilbenoids_cpd4", "2hH|–4r8.5s9–|H|–4r8.5r9–|T", "OC1=C([C@@H](C2=CC(O)=C3C(O[C@@H](C4=CC=C(O)C=C4O)[C@H]3C5=CC(O)=CC(O)=C5)=C2)[C@H](C6=CC=C(O)C=C6)O7)C7=CC(/C=C/C8=CC=C(O)C=C8)=C1"),
        (49, "Wolfender2025_AntiinfectStilbenoids_cpd5", "2hH|–4s8.5s9–|H|–4r8.5r9–|T", "OC1=C([C@@H](C2=CC(O)=C3C(O[C@H](C4=CC=C(O)C=C4O)[C@H]3C5=CC(O)=CC(O)=C5)=C2)[C@H](C6=CC=C(O)C=C6)O7)C7=CC(/C=C/C8=CC=C(O)C=C8)=C1"),
        (50, "Wolfender2025_AntiinfectStilbenoids_cpd6", "H|–4s8.5s9–|H|–4r8.5r9–|T", "OC1=C([C@@H](C2=CC(O)=C3C(O[C@H](C4=CC=C(O)C=C4)[C@H]3C5=CC(O)=CC(O)=C5)=C2)[C@H](C6=CC=C(O)C=C6)O7)C7=CC(/C=C/C8=CC=C(O)C=C8)=C1"),
        (51, "Wolfender2025_AntiinfectStilbenoids_cpd7", "2hH|–4s8.5s9–|H|–4s8.5s9–|H|–4s8.5s9–|T", "OC1=C([C@H](C2=CC(O)=C3C(O[C@H](C4=CC=C(O)C=C4)[C@H]3C5=CC(O)=C6C(O[C@H](C7=CC=C(O)C=C7O)[C@H]6C8=CC(O)=CC(O)=C8)=C5)=C2)[C@@H](C9=CC=C(O)C=C9)O%10)C%10=CC(/C=C/C%11=CC=C(O)C=C%11)=C1"),
        (52, "Wolfender2025_AntiinfectStilbenoids_cpd8", "H|–4s8.5s9–|H|–4s8.5s9–|H|–4s8.5s9–|T", "OC1=C([C@H](C2=CC(O)=C3C(O[C@H](C4=CC=C(O)C=C4)[C@H]3C5=CC(O)=C6C(O[C@H](C7=CC=C(O)C=C7)[C@H]6C8=CC(O)=CC(O)=C8)=C5)=C2)[C@@H](C9=CC=C(O)C=C9)O%10)C%10=CC(/C=C/C%11=CC=C(O)C=C%11)=C1"),
        (53, "Wolfender2025_AntiinfectStilbenoids_cpd9", "2hH|=24r.4s5s.5r7=|H", "OC(C=C1)=CC=C1[C@@H]2OC3=C(C=CC(O)=C3)[C@]([C@@H]4C5=CC(O)=CC(O)=C5)([H])[C@@]2([H])C6=C4C(O)=CC(O)=C6"),
        (54, "Wolfender2025_AntiinfectStilbenoids_cpd10", "2hH|–4s8.5s9–|2hH", "OC1=C([C@H](C2=CC(O)=CC(O)=C2)[C@@H](C3=CC=C(O)C=C3O)O4)C4=CC(/C=C/C5=CC=C(O)C=C5O)=C1"),
        (55, "Wolfender2025_AntiinfectStilbenoids_cpd11", "2hH|–4r2.5r1–|2hH|–4r8.5r7–|T", "OC1=CC(O)=CC([C@@H]([C@H](C2=CC=C(O)C3=C2O[C@@H](C4=CC=C(O)C=C4O)[C@@H]3C5=CC(O)=CC(O)=C5)O6)C7=C6C=C(O)C=C7/C=C/C8=CC=C(O)C=C8)=C1"),
        (56, "vitisin A", "H|–4S8.5S7–|T–15R–H|=84S.75S.4S7=|5RhH", "OC1=CC([C@@H](C(C(/C=C/C2=CC=C(O)C([C@H]3C(C=C(O)C=C4O[C@@H]5C6=CC=C(O)C=C6)=C4[C@]5([H])C(C=C(O)C=C7O)=C7[C@@H]3C8=CC=C(O)C=C8)=C2)=CC(O)=C9)=C9O%10)[C@H]%10C%11=CC=C(O)C=C%11)=CC(O)=C1"),
        (57, "vitisin B", "H|–4S8.5S7–|H|–4R0.5R1–|T|–84S.75S–|H", "OC1=CC([C@@H](C(C([C@@H]([C@H](C2=CC=C(O)C=C2)O3)C4=C3C=CC(/C=C/C5=C([C@H](C6=CC(O)=CC(O)=C6)[C@@H](C7=CC=C(O)C=C7)O8)C8=CC(O)=C5)=C4)=CC(O)=C9)=C9O%10)[C@H]%10C%11=CC=C(O)C=C%11)=CC(O)=C1"),
        (58, "ε-Viniferin", "H|–4R8.5R7–|T", "OC1=CC=C(/C=C/C2=CC(O)=CC3=C2[C@@H](C4=CC(O)=CC(O)=C4)[C@H](C5=CC=C(O)C=C5)O3)C=C1"),
        (59, "Ampelopsin A", "H|=4S8.5S7.74S=|5RhH", "OC(C=C1)=CC=C1[C@@H](O2)[C@](C3=C4C(O)=CC(O)=C3)([H])C5=C2C=C(O)C=C5[C@H](O)[C@H]4C6=CC=C(O)C=C6"),
        (60, "(+)-isoampelopsin F", "H≡4R5R.5S7.74S≡H", "OC1=C(C2C3C4=CC=C(O)C=C4)C(C3[C@H](C5=C(O)C=C(O)C=C52)C6=CC=C(O)C=C6)=CC(O)=C1"),
        (61, "resAgOAcMeOH1h5a", "T|05S|4SmH", "OC1=CC(O)=CC(/C=C/C2=CC=C(O[C@H]([C@@H](OC)C3=CC=C(O)C=C3)C4=CC(O)=CC(O)=C4)C=C2)=C1"),
        (62, "resAgOACMeOH3", "H=4R7.5S5R=4SmH", "OC1=CC([C@H]2[C@H](C3=CC=C(O)C=C3)C4=C(O)C=C(O)C=C4[C@@H]2[C@H](OC)C5=CC=C(O)C=C5)=CC(O)=C1")
    ]
    
    # Write the perfect CSV
    with open('Stilabar_Smiles_Perfect.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['num', 'compound_name', 'barcode', 'smiles'])
        
        for compound in compounds:
            writer.writerow(compound)
    
    print(f"✅ Created perfect CSV: Stilabar_Smiles_Perfect.csv")
    print(f"📊 Contains {len(compounds)} compounds")
    
    # Verify all have data
    with_barcodes = sum(1 for c in compounds if c[2])
    print(f"📋 Compounds with barcodes: {with_barcodes}")
    print(f"📋 Compounds without barcodes: {len(compounds) - with_barcodes}")

if __name__ == "__main__":
    create_perfect_csv()