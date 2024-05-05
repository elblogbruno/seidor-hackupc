
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:file/local.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';

import 'package:just_audio/just_audio.dart';
import 'package:http/http.dart' as http;

String EL_API_KEY = "a6a428a35925ea229488128cb89ea838";

class CreateOption extends StatefulWidget {
  final String title;
  final bool isCreatingOrder;
  const CreateOption({super.key,  required this.title, required this.isCreatingOrder});

  @override
  State<CreateOption> createState() => _CreateOptionState();
}


class _CreateOptionState extends State<CreateOption> {
  final SpeechToText _speechToText = SpeechToText();
  bool _speechEnabled = false;
  String _lastWords = '';
  String _text = '';

  final player = AudioPlayer(); //audio player obj that will play audio
  bool _isLoadingVoice = false; //for the progress indicator

  @override
  void initState() {
    super.initState();
    _initSpeech();

    if (widget.isCreatingOrder) {
      pokeAi("c");
    } else {
      pokeAi("warehouse");
    }
  }

  @override
  void dispose() {
    player.dispose();
    super.dispose();
  }

  /// This has to happen only once per app
  void _initSpeech() async {
    _speechEnabled = await _speechToText.initialize(finalTimeout: Duration(seconds: 5));

    var locales = await _speechToText.locales();
    for (var locale in locales) {
      print(locale.localeId);
    }
    var selectedLocale = locales.first;
    setState(() {});
  }

  /// Each time to start a speech recognition session
  void _startListening() async {
    if (!_speechEnabled) {
      print('Speech recognition not available');
      return;
    }

    if (_isLoadingVoice) {
      return;
    }

    await _speechToText.listen(onResult: _onSpeechResult,
        localeId: "en_US",
        listenFor: Duration(seconds: 10), listenMode: ListenMode.search, onSoundLevelChange: (double level) {
          print('Sound level $level');

            if (level < 0.0)
            {
                print(_lastWords);
                print("ENVIAR AQUI A API");
            }
        });

    setState(() {});
  }

  /// Manually stop the active speech recognition session
  /// Note that there are also timeouts that each platform enforces
  /// and the SpeechToText plugin supports setting timeouts on the
  /// listen method.
  void _stopListening() async {
    await _speechToText.stop();
    setState(() {});
  }

  /// This is the callback that the SpeechToText plugin calls when
  /// the platform returns recognized words.
  void _onSpeechResult(SpeechRecognitionResult result) {
    setState(() {
      _lastWords = result.recognizedWords;
      _text =  _lastWords;
    });

    if (_speechToText.isListening == false) {
      print("ENVIANDO A API");
      query(_text);
    }
  }

  Future<void> pokeAi(String clientType) async {
    // type - warehouse (almacén) o cliente
    //String url = "http://192.168.124.2:8000/poke?type=$clientType";
    _speechToText.stop();
    String url = "http://192.168.124.203:8000/poke?type=$clientType";

    final response = await http.get(
      Uri.parse(url),
    );

    print(response.body);

    playTextToSpeech(response.body);
  }

  Future<void> query(String sentence) async {
    String url = "http://192.168.124.203:8000/query_warehouse?sentence=$sentence";

    if (widget.isCreatingOrder) {
      url = "http://192.168.124.203:8000/query?sentence=$sentence";
    }

    try {
      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
      );

      print("RESPONSE: " + response.body);

      playTextToSpeech(response.body);

      setState(() {
        _text = response.body.replaceAll('\\n', '\n');
      });

    } catch (e) {
      print(e);
    }
  }


//For the Text To Speech
  Future<void> playTextToSpeech(String text) async {
    //display the loading icon while we wait for request
    setState(() {
      _isLoadingVoice = true; //progress indicator turn on now
      _speechToText.stop();
    });

    String voiceRachel = '21m00Tcm4TlvDq8ikWAM'; //Rachel voice - change if you know another Voice ID

    String url = 'https://api.elevenlabs.io/v1/text-to-speech/$voiceRachel';
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'accept': 'audio/mpeg',
        'xi-api-key': EL_API_KEY,
        'Content-Type': 'application/json',
      },
      body: json.encode({
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": .15, "similarity_boost": .75}
      }),
    );

    setState(() {
      _isLoadingVoice = false; //progress indicator turn off now
    });
    print("AUDIO RESPONSE: " + response.body.toString());

    //_text = response.body.toString();

    if (response.statusCode == 200) {
      final bytes = response.bodyBytes; //get the bytes ElevenLabs sent back
      await player.setAudioSource(MyCustomSource(
          bytes)); //send the bytes to be read from the JustAudio library
      player.play(); //play the audio


      _startListening();

    } else {
      // throw Exception('Failed to load audio');
      print("Failed to load audio from ElevenLabs");

      FlutterTts flutterTts = FlutterTts();

      flutterTts.setLanguage("en-US");

      await flutterTts.speak(text);
      await flutterTts.awaitSpeakCompletion(true);

      _startListening();

      return;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        backgroundColor: _speechToText.isListening ? Colors.blue[100] : Colors.red[100],
        appBar: AppBar(
        title: Text(widget.title),
    ),
    body: Center(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: <Widget>[
          Container(
            height: 450, // Altura fija del contenedor
            width: 300,
            decoration: BoxDecoration(
              color: Colors.white, // Color de fondo del contenedor

              border: Border.all(color: Colors.blue, width: 2), // Borde del contenedor
              borderRadius: BorderRadius.circular(8), // Bordes redondeados
            ),
            child: SingleChildScrollView( // Permite desplazar el contenido
              padding: const EdgeInsets.all(16.0), // Relleno interior para el texto
              child: Text(
                _text,
                style: const TextStyle(fontSize: 20, color: Colors.black),
              ),
            ),
          ),
          // if is loading voice, show the progress indicator
          if (_isLoadingVoice) CircularProgressIndicator(),
          Expanded(
            child: Container(
              padding: EdgeInsets.all(16),
              child: Text(
                // If listening is active show the recognized words
                _speechToText.isListening
                    ? '$_lastWords'
                // If listening isn't active but could be tell the user
                // how to start it, otherwise indicate that speech
                // recognition is not yet ready or not supported on
                // the target device
                    : _speechEnabled
                    ? 'Tap the microphone to start listening...'
                    : 'Speech not available',
              ),
            ),
          ),

        ])
        ,
      ),

    ),
      floatingActionButton: FloatingActionButton(
    onPressed:
    // If not yet listening for speech start, otherwise stop
    _speechToText.isNotListening ? _startListening : _stopListening,
      tooltip: 'Listen',
      child: Icon(_speechToText.isNotListening ? Icons.mic_off : Icons.mic),
    ),
    );
  }




}

// Feed your own stream of bytes into the player
class MyCustomSource extends StreamAudioSource {
  final List<int> bytes;
  MyCustomSource(this.bytes);

  @override
  Future<StreamAudioResponse> request([int? start, int? end]) async {
    start ??= 0;
    end ??= bytes.length;
    return StreamAudioResponse(
      sourceLength: bytes.length,
      contentLength: end - start,
      offset: start,
      stream: Stream.value(bytes.sublist(start, end)),
      contentType: 'audio/mpeg',
    );
  }
}
