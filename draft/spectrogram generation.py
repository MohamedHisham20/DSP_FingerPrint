import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile
from scipy.signal import spectrogram


def generate_spectrogram(input_folder, output_folder):
    directories_names = os.listdir(input_folder)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for directory in directories_names:
        for file in os.listdir(os.path.join(input_folder, directory)):
            if file.endswith('.wav'):
                file_path = os.path.join(input_folder, file)
                samplerate, data = wavfile.read(file_path)

                # Ensure data is mono for simplicity
                if len(data.shape) > 1:
                    data = np.mean(data, axis=1)

                # Trim to first 30 seconds
                data = data[:samplerate * 20]

                # Generate spectrogram
                frequencies, times, Sxx = spectrogram(data, fs=samplerate)
                plt.pcolormesh(times, frequencies, 10 * np.log10(Sxx), shading='gouraud')
                plt.colorbar(label='Intensity [dB]')
                plt.title(f"Spectrogram: {file}")
                plt.xlabel('Time [s]')
                plt.ylabel('Frequency [Hz]')

                # Save the spectrogram
                output_file = os.path.join(output_folder, f"{file}_spectrogram.png")
                plt.savefig(output_file)
                plt.close()


input_folder = "Task 5 Data"
output_folder = "Task 5 Data/generated spectrogram"
generate_spectrogram(input_folder, output_folder)
print("Spectrograms generated successfully!")
