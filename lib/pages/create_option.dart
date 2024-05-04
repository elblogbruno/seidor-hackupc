import 'package:flutter/material.dart';
import 'dart:async';

class CreateOption extends StatelessWidget {
  const CreateOption({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Option'),
      ),
      body: const Center(
        child: Text('Bienvenido a la Tercera Pantalla'),
      ),
    );
  }
}