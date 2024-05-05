import 'package:flutter/material.dart';

import 'order_options.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Image.network('https://yt3.googleusercontent.com/DYLEnXuuXhxcX1F9woO8r-4C3IuiNM_Lb4PGxBiTEeLgG0XxY773Irm629Kz_klYMkiixXX2I88=s900-c-k-c0x00ffffff-no-rj'),
            const Text(
              'Welcome to SeiVoice!',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20), // Espacio entre el texto y el botón
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const OrderOptions()),
                );
              },
              child: const Text("Start!"),
            ),
          ],
        ),
      ),
    );
  }
}





