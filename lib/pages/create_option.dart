import 'package:flutter/material.dart';
import 'dart:async';
import 'dart:io' as io;
import 'dart:convert';

import 'package:audioplayers/audioplayers.dart';
import 'package:file/file.dart';
import 'package:file/local.dart';
import 'package:another_audio_recorder/another_audio_recorder.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:whisper/scheme/transcribe.dart';
import 'package:whisper/scheme/version.dart';
import 'package:whisper/whisper_dart.dart';

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
  AnotherAudioRecorder? _recorder;
  Recording? _current;
  RecordingStatus _currentStatus = RecordingStatus.Unset;

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    _init();
  }

  String _text = "";
  void updateText(String newText) {
    setState(() {
      _text = newText;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Center(
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
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: <Widget>[
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: ElevatedButton(
                  onPressed: () {
                    switch (_currentStatus) {
                      case RecordingStatus.Initialized:
                        {
                          _start();
                          break;
                        }
                      case RecordingStatus.Recording:
                        {
                          _pause();
                          break;
                        }
                      case RecordingStatus.Paused:
                        {
                          _resume();
                          break;
                        }
                      case RecordingStatus.Stopped:
                        {
                          _init();
                          break;
                        }
                      default:
                        break;
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.lightBlue,
                  ),
                  child: _buildText(_currentStatus),
                ),
              ),
              ElevatedButton(
                onPressed: _currentStatus != RecordingStatus.Unset ? _stop : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent.withOpacity(0.5),
                ),
                child: const Text("Stop", style: TextStyle(color: Colors.white)),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: onPlayAudio,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueAccent.withOpacity(0.5),
                ),
                child: Text("Play", style: TextStyle(color: Colors.white)),
              ),
            ],
          ),

          Text("Audio recording duration : ${_current?.duration.toString()}")
        ]),
      ),
    );
  }

  _init() async {
    try {
      if (await AnotherAudioRecorder.hasPermissions) {
        String customPath = '/audio_temp';
        io.Directory appDocDirectory;
//        io.Directory appDocDirectory = await getApplicationDocumentsDirectory();
        if (io.Platform.isIOS) {
          appDocDirectory = await getApplicationDocumentsDirectory();
        } else {
          appDocDirectory = (await getExternalStorageDirectory())!;
        }

        // can add extension like ".mp4" ".wav" ".m4a" ".aac"
        customPath = appDocDirectory.path + customPath;

        // .wav <---> AudioFormat.WAV
        // .mp4 .m4a .aac <---> AudioFormat.AAC
        // AudioFormat is optional, if given value, will overwrite path extension when there is conflicts.
        io.File file = io.File("$customPath.WAV");
        if(await file.existsSync()) {
          //enviar al speach to text
          Future<io.File> _getFileFromAssets(String path) async {
            io.Directory tempDir = await getTemporaryDirectory();
            String tempPath = tempDir.path;
            var filePath = "$tempPath/$path";
            var file = io.File(filePath);
            if (file.existsSync()) {
              return file;
            } else {
              final byteData = await rootBundle.load('assets/$path');
              final buffer = byteData.buffer;
              await file.create(recursive: true);
              return file.writeAsBytes(buffer.asUint8List(byteData.offsetInBytes, byteData.lengthInBytes));
            }
          }

          String pathLibrary = (await _getFileFromAssets("libwhisper_android.so")).path;
          print(pathLibrary);
          Whisper whisper = Whisper(whisperLib: pathLibrary);

          String pathModel= (await _getFileFromAssets("for-tests-ggml-small.bin")).path;
          print(pathModel);
          try {
            var res = whisper.request(
              whisperRequest: WhisperRequest.fromWavFile(
                audio: io.File("$customPath.WAV"),
                model: io.File(pathModel),
              ),
            );
            print(res.toString());

          } catch (e) {
            print(e);
          }




          updateText(DateTime.timestamp().toString()*50);
          file.deleteSync();
        }
        _recorder = AnotherAudioRecorder(customPath, audioFormat: AudioFormat.WAV);

        await _recorder?.initialized;


        // after initialization
        var current = await _recorder?.current(channel: 0);
        print(current);
        // should be "Initialized", if all working fine
        setState(() {
          _current = current;
          _currentStatus = current!.status!;
          print(_currentStatus);
        });
      } else {
        return const SnackBar(content: Text("You must accept permissions"));
      }
    } catch (e) {
      print(e);
    }
  }

  _start() async {
    try {
      await _recorder?.start();
      var recording = await _recorder?.current(channel: 0);
      setState(() {
        _current = recording;
      });

      const tick = Duration(milliseconds: 50);
      Timer.periodic(tick, (Timer t) async {
        if (_currentStatus == RecordingStatus.Stopped) {
          t.cancel();
        }

        var current = await _recorder?.current(channel: 0);
        // print(current.status);
        setState(() {
          _current = current;
          _currentStatus = _current!.status!;
        });
      });
    } catch (e) {
      print(e);
    }
  }

  _resume() async {
    await _recorder?.resume();
    setState(() {});
  }

  _pause() async {
    await _recorder?.pause();
    setState(() {});
  }

  _stop() async {
    var result = await _recorder?.stop();
    print("Stop recording: ${result?.path}");
    print("Stop recording: ${result?.duration}");
    File file = widget.localFileSystem.file(result?.path);
    print("File length: ${await file.length()}");
    setState(() {
      _current = result;
      _currentStatus = _current!.status!;
    });
  }

  Widget _buildText(RecordingStatus status) {
    var text = "";
    switch (_currentStatus) {
      case RecordingStatus.Initialized:
        {
          text = 'Start';
          break;
        }
      case RecordingStatus.Recording:
        {
          text = 'Pause';
          break;
        }
      case RecordingStatus.Paused:
        {
          text = 'Resume';
          break;
        }
      case RecordingStatus.Stopped:
        {
          text = 'Init';
          break;
        }
      default:
        break;
    }
    return Text(text, style: const TextStyle(color: Colors.white));
  }

  //sustituir por llamar a whisper
  void onPlayAudio() async {
    AudioPlayer audioPlayer = AudioPlayer();
    Source source = DeviceFileSource(_current!.path!);
    await audioPlayer.play(source);
  }
}