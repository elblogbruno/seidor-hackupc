import 'package:flutter/material.dart';
import 'dart:async';

class CreateOption extends StatefulWidget {
  const CreateOption({super.key});

  @override
  State<CreateOption> createState() => _CreateOptionState();
}

class _CreateOptionState extends State<CreateOption> {
  String _text = "Texto inicial" * 50;

  void updateText(String newText) {
    setState(() {
      _text = newText;
    });
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('List of products'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: <Widget>[
                  Flexible(
                    child: Container(
                      height: 300, // Altura fija del contenedor
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
                  ),
                  Flexible(
                    child: UpdateTextButton(onPressed: () => updateText("Texto actualizado: ${DateTime.now()}" * 50)),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class UpdateTextButton extends StatelessWidget {
  final VoidCallback onPressed;

  const UpdateTextButton({super.key, required this.onPressed});

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      child: const Text('Order'),
    );
  }
}


