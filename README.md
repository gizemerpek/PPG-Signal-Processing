# PPG-Signal-Processing
This code processes a PPG (Photoplethysmogram) signal to analyze its features using a sliding window approach and  visualizes the results interactively.
1.1 Data Loading and Preparation :  
  Purpose: Load a CSV file containing the PPG signal and prepare it for analysis. 
 Steps: 
 Checks if the file contains a PPG column. 
 Fills any missing values in the PPG column with the mean value. 
1.2 Signal Filtering: 
 Purpose: Clean the signal by removing noise and irrelevant frequencies. 
 Filters Used: 
 Low-Pass Filter: Removes high-frequency noise above 3 Hz. 
 High-Pass Filter: Removes low-frequency drift below 0.8 Hz. 
1.3  Sliding Window Analysis: 
  Purpose: Analyze smaller segments of the signal for detailed feature extraction. 
 Parameters: 
 Window Size: 5 seconds (1800 data points at a sampling frequency fs=360fs=360). 
 Window Step: 1 second (360 data points) 
1.4 Feature Extraction: 
For each sliding window, the following features are calculated: 
1. PWSP (Pulse Wave Systolic Peak): The highest point of the pulse wave. 
2. PWDP (Pulse Wave Diastolic Peak): The lowest point of the pulse wave. 
3. PWA (Pulse Wave Amplitude): Difference between PWSP and PWDP . 
4. Dicrotic Notch: Average of the systolic and diastolic peaks. 
5. Systolic Phase: Time of the systolic peak within the window. 
6. Diastolic Phase: Time of the diastolic peak within the window. 
7. PPT (Pulse Transit Time): Time difference between the first and last peaks in the window. 
8. PWD (Pulse Wave Duration): Total duration of the pulse wave. 
9. Heart Rate (BPM): Calculated as Heart Rate=60/Average Peak IntervalHeart Rate=60/Average Peak Interval. 
1.5 Visualization: 
 Top Plot (Raw Signal): 
 Displays the entire PPG signal with a highlighted sliding window. 
 Bottom Plot (Window Analysis): 
 Shows the original and processed signals within the window. 
 Marks peaks and displays their calculated features (e.g., PWSP, PWDP, etc.).
