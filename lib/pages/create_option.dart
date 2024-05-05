
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:file/local.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';

import 'package:just_audio/just_audio.dart';
import 'package:http/http.dart' as http;

String EL_API_KEY = "a6a428a35925ea229488128cb89ea838";

class CreateOption extends StatefulWidget {
  const CreateOption({super.key});

  @override
  State<CreateOption> createState() => _CreateOptionState();
}

class _CreateOptionState extends State<CreateOption> {
  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: Scaffold(
        body: SafeArea(
          child: RecorderExample(),
        ),
      ),
    );
  }
}

class RecorderExample extends StatefulWidget {
  final LocalFileSystem localFileSystem;

  const RecorderExample({super.key, localFileSystem}) : localFileSystem = localFileSystem ?? const LocalFileSystem();

  @override
  State<StatefulWidget> createState() => RecorderExampleState();
}

class RecorderExampleState extends State<RecorderExample> {
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

    pokeAi("w");
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
      playTextToSpeech(_lastWords);

      //callApi(_lastWords);
    });
  }

  Future<void> pokeAi(String clientType) async {
    // type - warehouse (almacén) o cliente
    //String url = "http://192.168.124.2:8000/poke?type=$clientType";
    String url = "http://192.168.124.203:8000/poke?type=$clientType";

    final response = await http.get(
      Uri.parse(url),
    );

    print(response);

    playTextToSpeech(response.body);
  }

  Future<void> query(String sentence) async {
    String url = "http://192.168.24.2:8000/query";
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Content-Type': 'application/json',
      },
      body: json.encode({
        "text": sentence,
      }),
    );
  }

  Future<void> queryWarehouse(String sentence) async {
      String url = "http://192.168.24.2:8000/query_warehouse";
      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode({
          "text": sentence,
        }),
      );
  }


//For the Text To Speech
  Future<void> playTextToSpeech(String text) async {
    //display the loading icon while we wait for request
    setState(() {
      _isLoadingVoice = true; //progress indicator turn on now
    });

    String voiceRachel =
        '21m00Tcm4TlvDq8ikWAM'; //Rachel voice - change if you know another Voice ID

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

    if (response.statusCode == 200) {
      final bytes = response.bodyBytes; //get the bytes ElevenLabs sent back
      await player.setAudioSource(MyCustomSource(
          bytes)); //send the bytes to be read from the JustAudio library
      player.play(); //play the audio
    } else {
      // throw Exception('Failed to load audio');
      return;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
        title: Text('Speech Demo'),
    ),
    body: Center(
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Column(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: <Widget>[
          Container(
            height: 450, // Altura fija del contenedor
            width: 260,
            decoration: BoxDecoration(
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
