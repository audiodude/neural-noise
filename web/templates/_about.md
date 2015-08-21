# Neural Noise

Training Recurrent Neural Networks to generate music in text formats

By Travis Briggs, June-August 2015

## Overview

[This website](/) provides a glimpse into some of the results of an experiment
using Recurrent Neural Networks
([RNNs](https://en.wikipedia.org/wiki/Recurrent_neural_network))
to generate music in the textual abc format. The project was technically
interesting, involving XML processing, learning the abc format, compiling
programs that are 20 years old, asynchronously generating results, and playing
MIDI files in a web browser. Despite these intriguing challenges, the end
results are, I would say, only okay.

The
[render view](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595e55fdff8de2c9234bf6d)
of each song snippet provides the raw abc data, the ability to
play a pre-generated MIDI of the snippet
([abcmidi](http://abc.sourceforge.net/abcMIDI/)),
and a PNG rendering of sheet music ([abcm2ps](http://moinejf.free.fr/)).

As far as the neural network software, I used the
[char-rnn](https://github.com/karpathy/char-rnn) package provided by Andrej
Karpathy. His original blog post on the
[unreasonable effectivness of recurrent neural networks](http://karpathy.github.io/2015/05/21/rnn-effectiveness/)
was the inspiration for this project, and the ultimate reason why abc notation
was used to represent the data, instead of say MIDI files or WAV audio data.
The networks were trained on a small corpus of pop songs which included harmony
information (chords) and melody. This musical data was converted into abc
notation before being fed to the networks.

The web interface allows users to browse random song snippets at a particular
checkpoint and temperature value.

## Basic results

Some song snippets are just a complete train wreck, like
[this one](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595eaa5dff8de2c9234bffd)
that has a bunch of fast melody notes and chords in the beginning, then a huge
sequence of just chords.

Other song snippets frequently contain parts that are musically nonsensical,
such as the triple-dotted whole notes featured prominently in
[this horror show](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595eb77dff8de2c9234c024).

Song snippets can
[start off promising](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595ecabdff8de2c9234c043),
but in this case the notes go on forever.

Sometimes the program directly rips off an existing song, which seemed to be the
case with some of the checkpoints generated in the middle that were overpowered 
(too many nodes), and thus overfitted the data. Those checkpoints have been
subsequently removed from the site for simplicity (they weren't very good
anyway).

Despite all this, some of the song snippets sound surprisingly good, like
[this](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595e55fdff8de2c9234bf6d)
and
[this](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595e4f8dff8de2c9234bf6a).

## Prior work

Also inspired by Karpathy, Bob L. Strum explored
["Recurrent Neural Networks for Folk Music Generation"](https://highnoongmt.wordpress.com/2015/05/22/lisls-stis-recurrent-neural-networks-for-folk-music-generation/).
This is the project that is most similar to Neural Noise, in that it used abc
notation as the format to represent music, and tools such as abc2midi (and
presumably abcm2ps) to generate visual and aural representations of the music.
As the author notes, abc notation generally represents music that is "monophonic
typically, but polyphony is possible too". It is this leap into the world of
polyphony (multiple notes sounding at once) that I have made for Neural Noise.

In ["A First Look at Music Composition using LSTM Recurrent Neural Networks"](http://people.idsia.ch/~juergen/blues/IDSIA-07-02.pdf),
Douglas Eck and Jürgen Schmidhuber fed a standard 12 bar blues progression to a
neural network and obtained fairly interesting results. They demonstrated that
a RNN can capture both the local structure of melody and the long-term structure
of a musical style by performing experiments with the input data. This work
featured custom designed Neural Networks and did not use the char-rnn software.

Finally Daniel Johnson has done work on ["Composing Music With Recurrent Neural Networks"](http://www.hexahedria.com/2015/08/03/composing-music-with-recurrent-neural-networks/).
In fact, Johnson provides links to the other references mentioned here. He has
implemented his own Neural Networks that operate on MIDI data and produce works
of "classical" sounding music in a stream without any reference to a beginning
or an end.

## Technical details

Neural Noise is a series of Python scripts that interact with external programs
in order to:

1. Generate a training set of music represented as character data, using
[ABC notation](http://abcnotation.com) or some variation thereof;
1. Train a Recurrent Neural Network (RNN) with the data, using the excellent
[char-rnn](https://github.com/karpathy/char-rnn) package;
1. Generate new music snippets using checkpoints output by char-rnn;
   1. Create companion MIDI files and sheet music PNGs for each of these
   snippets using [abcmidi](https://github.com/audiodude/abcmidi) and
   [abcm2ps](https://github.com/audiodude/abcm2ps);
   1. Store the snippets, MIDI files and metadata in a MongoDB instance; and
1. Finally, allow the user to randomly browse the new snippets using a [web interface](http://nn.0-z-0.com).

This is a complicated mish-mash (hack) of software, and getting it running is
not for the faint of heart. Still, in this README we will attempt to document
the complete set of steps that were used in installing char-rnn, massaging the
training data, running the training, generating the snippets, and finally
getting the web interface up and running.