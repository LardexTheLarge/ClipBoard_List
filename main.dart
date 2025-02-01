import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() {
  runApp(NoteTakerApp());
}

class NoteTakerApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Note Taker',
      home: NoteTakerHome(),
    );
  }
}

class NoteTakerHome extends StatefulWidget {
  @override
  _NoteTakerHomeState createState() => _NoteTakerHomeState();
}

class _NoteTakerHomeState extends State<NoteTakerHome> {
  final String serverUrl = "http://<your-computer-ip>:5000"; // Replace with your server's IP
  List<String> notes = [];
  String selectedNote = "";
  String noteContent = "";

  @override
  void initState() {
    super.initState();
    fetchNotes();
  }

  Future<void> fetchNotes() async {
    try {
      final response = await http.get(Uri.parse("$serverUrl/notes"));
      if (response.statusCode == 200) {
        setState(() {
          notes = List<String>.from(json.decode(response.body));
        });
      }
    } catch (e) {
      print("Failed to fetch notes: $e");
    }
  }

  Future<void> loadNote(String title) async {
    try {
      final response = await http.get(Uri.parse("$serverUrl/notes/$title"));
      if (response.statusCode == 200) {
        setState(() {
          noteContent = json.decode(response.body)["content"];
        });
      }
    } catch (e) {
      print("Failed to load note: $e");
    }
  }

  Future<void> saveNote(String title, String content) async {
    try {
      final response = await http.post(
        Uri.parse("$serverUrl/notes"),
        headers: {"Content-Type": "application/json"},
        body: json.encode({"title": title, "content": content}),
      );
      if (response.statusCode == 200) {
        fetchNotes(); // Refresh the notes list
      }
    } catch (e) {
      print("Failed to save note: $e");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("Note Taker")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            DropdownButton<String>(
              value: selectedNote.isEmpty ? null : selectedNote,
              hint: Text("Select a note"),
              items: notes.map((note) {
                return DropdownMenuItem(
                  value: note,
                  child: Text(note),
                );
              }).toList(),
              onChanged: (value) {
                setState(() {
                  selectedNote = value!;
                });
                loadNote(value!);
              },
            ),
            TextField(
              decoration: InputDecoration(labelText: "Title"),
              onChanged: (value) {
                setState(() {
                  selectedNote = value;
                });
              },
            ),
            Expanded(
              child: TextField(
                decoration: InputDecoration(labelText: "Content"),
                maxLines: null,
                onChanged: (value) {
                  setState(() {
                    noteContent = value;
                  });
                },
                controller: TextEditingController(text: noteContent),
              ),
            ),
            ElevatedButton(
              onPressed: () {
                saveNote(selectedNote, noteContent);
              },
              child: Text("Save Note"),
            ),
          ],
        ),
      ),
    );
  }
}