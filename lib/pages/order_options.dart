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
            Image.network('https://icons.veryicon.com/png/o/business/operation-and-maintenance-platform/create-order.png', width: 100, height: 100),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const CreateOption(title: 'Create an order', isCreatingOrder: true,)),
                );
              },
              child: const Text('Create an order'),
            ),
            const SizedBox(height: 100),
            Image.network('https://cdn2.iconfinder.com/data/icons/shopping-e-commerce-3-1/32/Preparing-Order-Ship-preparing-To-512.png', width: 100, height: 100),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const CreateOption(title: 'Prepare the order', isCreatingOrder: false,)),
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