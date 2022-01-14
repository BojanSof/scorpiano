![Scorpiano](<./images/logo.png>)


Scorpiano is a system for automatic music transcription (AMT) for monophonic
piano music, based on digital signal processing techniques.

The system is implemented using Python 3.

## System Architecture

The system consists of five modules for: 
- *onset detection* - determining the starting times of musical notes, using
the energy novelty function
- *tempo estimation* - using <code>beat.tempo</code> function from librosa, 
- *beat detection* - assuming no breaks, multiplying the difference between
two subsequent onset moments with the tempo, 
- *pitch detection* - using the YIN algorithm, and
- *music score generation*.

For more details about the system, refer to the [paper](paper/ANT.pdf).

## Prerequisites

The application is developed on Linux, and there may be problems on Windows.

- [Python 3](https://www.python.org/downloads/)
- [Numpy](https://numpy.org/)
- [Scipy](https://www.scipy.org/) - for loading wav files
- [Librosa](https://librosa.org/) - for tempo estimation
- [Music21](https://web.mit.edu/music21/) - for music score generation (Important: install version 6.7.1)
- [MIDIUtil](https://github.com/MarkCWirt/MIDIUtil) - for MIDI file generation
- [Lilypond](http://lilypond.org/) - for rendering the music score in PNG format

For the GUI:
- [GTK3](https://www.gtk.org/)
- [pygobject](https://pygobject.readthedocs.io/en/latest/)

Optional:
- [MuseScore](https://musescore.org/en) - free open-source music notation
software, perfect for editing MusicXML files generated using Scorpiano

After installing the required packages, inside the python interpreter, run the following commands:
```
from music21 import *
environment.UserSettings()['lilypondPath'] = 'path/to/lilypond executable'
```

## Usage

To run the GUI, execute <code>python gui.py</code>.

![Scorpiano GUI](<./images/gui_screenshot.png>)

After loading the GUI:
1. Load audio file (wav file)
2. Modify the parameters if needed
3. Click on the Transcribe button
4. Export the generated score as PNG or MusicXML format, or export MIDI file, via File menu.

The samples folder contains 10 monophonic piano melodies, generated using MuseScore and played on digital piano.
