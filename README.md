# molecular-collision-data-analysis
This repository contains tools and scripts for processing and analyzing data from molecular collision calculations using MQCT method. It focuses on cross-section data analysis, identification of reversible transitions, and visualization of collision outcomes.
This Python script analyzes cross-section data obtained from MQCT calculations, identifies reversible transitions, and visualizes the reversibility of these transitions.

## Features
- Reads and parses cross-section data from “CS_op_J0_U170_all_trans_final.DAT”
- Processes user input data from 'UIP_op.DAT'
- Calculates various parameters including energy differences and angular momentum changes
- Identifies reversible transitions
- Generates a scatter plot to visualize the reversibility of transitions

## Requirements
- Python 3.x
- pandas
- matplotlib

## Usage
1. Ensure that the input files 'CS_op_J0_U170_all_trans_final.DAT' and 'UIP_op.DAT' are in the same directory as the script.
2. Run the script: python reversible_transition_analysis.py
3. The script will generate an Excel file  rev_transitions.xlsx' in the 'Rev_trans_excel’ directory.
4. A scatter plot will be displayed showing the reversibility of transitions for different ΔJ2 values.

## Output
- Excel file: 'Rev_trans_excel/rev_transitions.xlsx'
- Scatter plot: Displayed on screen, showing reversible transitions. User can save this figure.

## Note
This script is designed for specific input file formats. Make sure your input files match the expected format for proper functioning.

## Author
Carolin Anna Joy

