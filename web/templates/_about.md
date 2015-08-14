# Neural Noise

Training Recurrent Neural Networks to generate music in text formats

## Overview

[This website](/) provides a glimpse into some of the results of an experiment using
Recurrent Neural Networks ([RNNs](https://en.wikipedia.org/wiki/Recurrent_neural_network))
to generate music in the textual abc format. The project was technically
interesting, involving XML processing, learning the abc format, compiling
programs that are 20 years old, asynchronously generating results, and playing
MIDI files in a web browser. Despite these intriguing challenges, the end
results are, I would say, only okay.

The render view of each song snippet provides the raw abc data, the ability to
play a pre-generated MIDI of the snippet ([abcmidi](http://abc.sourceforge.net/abcMIDI/)),
and a PNG rendering of sheet music ([abcm2ps](http://moinejf.free.fr/)).

As far as the neural network software, I used the
[char-rnn](https://github.com/karpathy/char-rnn) package provided by Andrej Karpathy. His original blog post on the
[unreasonable effectivness of recurrent neural networks](http://karpathy.github.io/2015/05/21/rnn-effectiveness/)
was the inspiration for this project, and the ultimate reason why abc notation
was used to represent the data, instead of say MIDI files or WAV audio data.
The networks were trained on a small corpus of pop songs which included harmony
information (chords) and melody. This musical data was converted into abc
notation before being fed to the networks.

## Basic results

Some song snippets are just a complete train wreck, like [this one](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595eaa5dff8de2c9234bffd) that has a bunch of fast melody notes and chords in the beginning, then a huge sequence of just chords.

Other song snippets frequently contain parts that are musically nonsensical, such as the triple-dotted whole notes featured prominently in [this horror show](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595eb77dff8de2c9234c024).

Song snippets can [start off promising](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595ecabdff8de2c9234c043), but in this case the notes go on forever.

Sometimes the program directly rips off an existing song, which seemed to be the case with some of the checkpoints generated in the middle that were overpowered (too many nodes), and thus overfitted the data. Those checkpoints have been subsequently removed from the site for simplicity (they weren't very good anyways).

Despite all this, some of the song snippets sound surprisingly good, like [this](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595e55fdff8de2c9234bf6d) and [this](http://nn.0-z-0.com/render/lm_lstm_epoch19.46_0.4127.t7/5595e4f8dff8de2c9234bf6a).

