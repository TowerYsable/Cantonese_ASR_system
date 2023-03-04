from matplotlib import mlab
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

def specgram3d(y, srate=44100, ax=None, title=None):
    if not ax:
        ax = plt.axes(projection='3d')
    ax.set_title(title, loc='center', wrap=True)
    spec, freqs, t = mlab.specgram(y, Fs=srate)
    #   X, Y, Z = t[None, :], freqs[:, None],  20.0 * np.log10(spec)
    X, Y, Z = t[None, :], freqs[:, None], 7.0 * np.log10(spec)
    ax.plot_surface(X, Y, Z, cmap='viridis')
    ax.set_xlabel('time (s)')
    ax.set_ylabel('frequencies (Hz)')
    ax.set_zlabel('amplitude (dB)')
    ax.set_zlim(-140, 0)
    return X, Y, Z

def specgram2d(y, srate=44100, ax=None, title=None):
    if not ax:
        ax = plt.axes()
    ax.set_title(title, loc='center', wrap=True)
    spec, freqs, t, im = ax.specgram(y, Fs=srate, scale='dB', vmax=0)
    ax.set_xlabel('time (s)')
    ax.set_ylabel('frequencies (Hz)')
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Amplitude (dB)')
    cbar.minorticks_on()
    return spec, freqs, t, im

def audio_vis(audio_path, audio_type):
    y, fs = sf.read(audio_path)
    fig1, ax1 = plt.subplots()
    title = audio_type + '2d spectogram'
    specgram2d(y, srate=fs, title=title, ax=ax1)
    plt.savefig('images/' + audio_type + '_2d.png')
    plt.close()

    title = audio_type + '3d spectogram'
    fig2, ax2 = plt.subplots(subplot_kw={'projection': '3d'})
    specgram3d(y, srate=fs, title=title, ax=ax2)
    plt.savefig('images/' + audio_type + '_3d.png')
    plt.close()