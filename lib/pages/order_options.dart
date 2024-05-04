import 'dart:ui';

import 'package:flutter/material.dart';
import 'package:seidor_hackupc/pages/create_option.dart';
import 'package:seidor_hackupc/pages/prepare_option.dart';


class OrderOptions extends StatelessWidget {
  const OrderOptions({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
            'Segunda Pantalla',
            style: TextStyle(
              color: Colors.white,
              fontSize:18,
              fontWeight: FontWeight.bold
            ),
        ),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const CreateOption()),
                );
              },
              child: const Text('Create an order'),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const PrepareOption()),
                );
              },
              child: const Text('Prepare the order'),
            ),
          ],
        ),
      ),
    );
  }
}