# Project Title

## Overview
This project is a music matching and mixing application that allows users to upload songs, analyze their features, and find similar songs based on perceptual hashes. It also supports mixing two songs with adjustable weights.

https://github.com/user-attachments/assets/11d34a41-a448-4156-a2f9-2d8b49871383

## Key Features
- **Song Analysis**: Extracts and analyzes various features from songs, including spectral centroid, spectral contrast, MFCCs, and more.
- **Perceptual Hashing**: Generates perceptual hashes for songs to enable efficient similarity searches.
- **Database Management**: Creates and manages a database of song fingerprints, stored in JSON format.
- **Song Matching**: Searches the database to find songs similar to a given input based on perceptual hashes.
- **Song Mixing**: Mixes two songs with adjustable weights and plays the mixed audio.
- **Graphical User Interface**: Provides a user-friendly interface using PyQt5 for uploading songs, viewing matches, and playing audio.

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/MohamedHisham20/DSP_FingerPrint
   ```
2. Navigate to the project directory:
   ```sh
   cd DSP_FingerPrint
   ```
3. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage
1. Run the main application:
   ```sh
   python main.py
   ```
2. Use the GUI to upload songs, view matches, and mix songs.

## File Structure
- `main.py`: Main application file that initializes the GUI and handles user interactions.
- `database.py`: Handles the creation and management of the song fingerprint database.
- `processing_and_searching.py`: Contains functions for audio processing, feature extraction, and searching.
- `matchmaker.py`: Implements the logic for matching songs and mixing audio.
- `Audio_Fingerprint.py`: Defines the `Audio_Fingerprint` class for creating song fingerprints.
- `stylesheet.py`: Contains the stylesheet for the GUI.
- `json_ctrl.py`: Provides utility functions for reading and writing JSON files.
- `song_widget.py`: Defines the GUI components for displaying song information.

## Contributors

Special thanks to everyone who has contributed to this project!  

|              | GitHub Profile                     |
|------------------|-----------------------------------|
| [<img src="https://github.com/abdelrahman-alaa-10.png" width="20">](https://github.com/abdelrahman-alaa-10) | [Abdelrahman Alaa](https://github.com/abdelrahman-alaa-10) |
| [<img src="https://github.com/Ibrahim-Fateen.png" width="20">](https://github.com/Ibrahim-Fateen) | [Ibrahim Fateen](https://github.com/Ibrahim-Fateen) |
| [<img src="https://github.com/MohamedHisham20.png" width="20">](https://github.com/MohamedHisham20) | [Mohamed Hisham](https://github.com/MohamedHisham20) |
| [<img src="https://github.com/salahmohamed03.png" width="20">](https://github.com/salahmohamed03) | [Salah Mohamed](https://github.com/salahmohamed03) |

### Submitted to
Dr. Tamer Basha & Eng. Omar Aldaw
