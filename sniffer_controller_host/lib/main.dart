import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';
import 'package:flutter_blue/flutter_blue.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: MyHomePage(title: 'SMS Sniffer Controller'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  MyHomePage({Key? key, required this.title}) : super(key: key);

  final String title;

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _terminalOutput = '';
  bool _buttonsEnabled = false;
  bool _deviceFlashed = false;
  bool _connected = false;
  String _selectedBaudRate = '9600';
  BluetoothDevice? _selectedDevice;
  TextEditingController _mergeIntervalController = TextEditingController(text: '80');

  final List<String> _baudRates = ['9600', '19200', '38400', '57600', '115200'];
  List<BluetoothDevice> _devices = [];
  FlutterBlue _flutterBlue = FlutterBlue.instance;

  final ScrollController _scrollController = ScrollController();
  BluetoothDevice? _connectedDevice;
  BluetoothCharacteristic? _characteristic;

  @override
  void initState() {
    super.initState();
    _scanDevices();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance?.addPostFrameCallback((_) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    });
  }

  void _updateTerminalOutput(String output) {
    setState(() {
      _terminalOutput += output;
    });
    _scrollToBottom();
  }

  void _scanDevices() async {
    try {
      List<BluetoothDevice> devices = await _flutterBlue.connectedDevices;
      setState(() {
        _devices = devices;
        if (_devices.isNotEmpty) {
          _selectedDevice = _devices[0];
        }
      });
    } catch (e) {
      print('Error scanning devices: $e');
    }
  }

  void _refreshDeviceList() {
    _updateTerminalOutput(' [FUNCTION] update_device_list calling…');

    if (_characteristic != null) {
      _characteristic!.write('update_device_list\n'.codeUnits);
    }
  }

  void _oneClickScanning() {
    _updateTerminalOutput('\n ~/cell_logger/osmocom-bb/src/host/layer23/src/misc/cell_log -O');

    if (_characteristic != null) {
      _characteristic!.write('scan\n'.codeUnits);
    }
  }

  void _oneClickFlashing() {
    _updateTerminalOutput('\nsudo /etc/Osmocom-BB/Bin/osmocon -s /tmp/osmocom_l2 -m c123xor -p /dev/ttyUSB0 -c /etc/Osmocom-BB/Firmware/e88/layer1.highram.bin');

    if (_characteristic != null) {
      _characteristic!.write('flash\n'.codeUnits);
    }
  }

  void _killAllProcesses() {
    _updateTerminalOutput(' [FUNCTION] close_session calling…');

    if (_characteristic != null) {
      _characteristic!.write('kill\n'.codeUnits);
    }
  }

  void _resetAllPower() {
    _updateTerminalOutput(' [FUNCTION] hard_restart calling…');

    if (_characteristic != null) {
      _characteristic!.write('reset\n'.codeUnits);
    }
  }

  void _connect() async {
    if (_selectedDevice != null) {
      try {
        await _selectedDevice!.connect();
        List<BluetoothService> services = await _selectedDevice!.discoverServices();
        for (BluetoothService service in services) {
          for (BluetoothCharacteristic characteristic in service.characteristics) {
            if (characteristic.uuid.toString() == '00001101-0000-1000-8000-00805F9B34FB') {
              _characteristic = characteristic;
              await _characteristic!.setNotifyValue(true);
              _characteristic!.value.listen((value) {
                String receivedData = String.fromCharCodes(value);
                _updateTerminalOutput(receivedData);
              });
              break;
            }
          }
        }

        setState(() {
          _connected = true;
          _buttonsEnabled = true;
          _mergeIntervalController.text = _mergeIntervalController.text;
          _updateTerminalOutput(' [INFO] Connected to Sniffer Slave {${DateTime.now().toString()}}\n>');
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Connected')),
          );
        });
      } catch (e) {
        print('Error connecting to device: $e');
        setState(() {
          _updateTerminalOutput(' [ERROR] Connection Failed\n>');
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Connection Failed')),
          );
        });
      }
    } else {
      setState(() {
        _updateTerminalOutput(' [ERROR] No device selected\n>');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('No device selected')),
        );
      });
    }
  }

  void _disconnect() async {
    if (_selectedDevice != null && _selectedDevice!.state == BluetoothDeviceState.connected) {
      await _selectedDevice!.disconnect();
      setState(() {
        _connected = false;
        _buttonsEnabled = false;
        _updateTerminalOutput(' [INFO] Disconnected from Sniffer Slave {${DateTime.now().toString()}}\n>');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Disconnected')),
        );
      });
    }
  }

  void _showAboutPage() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return Scaffold(
          backgroundColor: Colors.black,
          body: GestureDetector(
            onTap: () {
              Navigator.of(context).pop();
            },
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'This is an implementation of an SMS sniffer based on the osmocombb GSM protocol stack. It consists of a Linux-based sniffer server, an Android app, and a desktop QT application, responsible for running the SMS sniffer service, controlling the sniffer service, and monitoring and processing the sniffing process and results, respectively.\n\nThe initial version was written in April 2018. A tribute to that summer six years ago.',
                    textAlign: TextAlign.left,
                    style: TextStyle(color: Color.fromARGB(235, 255, 255, 255), fontSize: 18, fontFamily: 'Times New Roman'),
                  ),
                  SizedBox(height: 35),
                  Image.asset(
                    'assets/my2018.png',
                    width: 140,
                    height: 140,
                  ),
                  SizedBox(height: 35),
                  Text(
                    '                                      Bensen Wang\n                                            14/05/24',
                    textAlign: TextAlign.right,
                    style: TextStyle(color: Color.fromARGB(235, 255, 255, 255), fontSize: 18, fontFamily: 'Times New Roman'),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
      ),
      body: Column(
        children: [
          Expanded(
            child: Container(
              color: Colors.black,
              constraints: BoxConstraints(minWidth: MediaQuery.of(context).size.width),
              child: SingleChildScrollView(
                controller: _scrollController,
                child: Text(
                  _terminalOutput,
                  style: TextStyle(
                    color: Colors.green,
                    fontSize: 14,
                    fontFamily: 'CascadiaCode',
                    height: 1.2,
                  ),
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 8.0),
            child: Row(
              children: [
                Expanded(
                  flex: 3,
                  child: DropdownButton<BluetoothDevice>(
                    value: _selectedDevice,
                    onChanged: (BluetoothDevice? newValue) {
                      setState(() {
                        _selectedDevice = newValue;
                      });
                    },
                    items: _devices.map<DropdownMenuItem<BluetoothDevice>>((BluetoothDevice device) {
                      return DropdownMenuItem<BluetoothDevice>(
                        value: device,
                        child: Text(
                          device.name,
                          style: TextStyle(fontSize: 14),
                        ),
                      );
                    }).toList(),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: DropdownButton<String>(
                    value: _selectedBaudRate,
                    onChanged: (String? newValue) {
                      setState(() {
                        _selectedBaudRate = newValue!;
                      });
                    },
                    items: _baudRates.map<DropdownMenuItem<String>>((String value) {
                      return DropdownMenuItem<String>(
                        value: value,
                        child: Text(
                          value,
                          style: TextStyle(fontSize: 14),
                        ),
                      );
                    }).toList(),
                  ),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _connected ? null : _connect,
                  child: Text(
                    'Connect',
                    style: TextStyle(fontSize: 14),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4.0, horizontal: 8.0),
            child: Row(
              children: [
                Text(
                  'Merge interval (MS)',
                  style: TextStyle(fontSize: 14),
                ),
                SizedBox(width: 10),
                Expanded(
                  child: TextField(
                    controller: _mergeIntervalController,
                    enabled: !_connected,
                  ),
                ),
                SizedBox(width: 10),
                ElevatedButton(
                  onPressed: _connected ? _disconnect : null,
                  child: Text(
                    'Disconnect',
                    style: TextStyle(fontSize: 14),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: GridView.count(
              shrinkWrap: true,
              crossAxisCount: 2,
              childAspectRatio: 3,
              mainAxisSpacing: 8,
              crossAxisSpacing: 8,
              children: [
                ElevatedButton(
                  onPressed: _connected ? _refreshDeviceList : null,
                  child: Center(child: Text('Update Dev List')),
                ),
                ElevatedButton(
                  onPressed: _connected && _buttonsEnabled ? _oneClickFlashing : null,
                  child: Center(child: Text('Flash C118s')),
                ),
                ElevatedButton(
                  onPressed: _connected && _buttonsEnabled ? _oneClickScanning : null,
                  child: Center(child: Text('Start Sniffing')),
                ),
                ElevatedButton(
                  onPressed: _connected && _buttonsEnabled ? _killAllProcesses : null,
                  child: Center(child: Text('Kill All Processes')),
                ),
                ElevatedButton(
                  onPressed: _connected && _buttonsEnabled ? _resetAllPower : null,
                  child: Center(child: Text('Reset All Power')),
                ),
                ElevatedButton(
                  onPressed: _showAboutPage,
                  child: Center(child: Text('About')),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}