import os
from jnius import autoclass, PythonJavaClass, java_method

# Define the Java class for the MethodChannel
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = autoclass('android.content.Context')
Environment = autoclass('android.os.Environment')

# Define the Python class that will handle the method calls
class MethodHandler(PythonJavaClass):
    __javacontext__ = 'app'

    @java_method('(Ljava/lang/String;)Ljava/lang/String;')
    def getNoteContent(self, title):
        """Fetch note content from local storage."""
        try:
            with open(f"notes/{title}.txt", "r") as file:
                return file.read()
        except FileNotFoundError:
            return f"Note '{title}' not found locally."
        except Exception as e:
            return f"Failed to load note content: {e}"

    @java_method('()Ljava/util/List;')
    def getNotes(self):
        """Fetch notes locally from device storage."""
        try:
            notes_dir = "notes"
            if not os.path.exists(notes_dir):
                os.makedirs(notes_dir)
            return [f[:-4] for f in os.listdir(notes_dir) if f.endswith(".txt")]
        except Exception as e:
            return [f"Failed to load notes: {e}"]

    @java_method('(Ljava/lang/String;Ljava/lang/String;)V')
    def saveNote(self, title, content):
        """Save the current note."""
        try:
            with open(f"notes/{title}.txt", "w") as file:
                file.write(content)
        except Exception as e:
            print(f"Failed to save note: {e}")

# Set up the MethodChannel
def setup_channel():
    activity = PythonActivity.mActivity
    context = activity.getApplicationContext()
    channel = autoclass('io.flutter.plugin.common.MethodChannel')
    method_channel = channel(context, 'com.example.notes_app/channel')
    handler = MethodHandler()
    method_channel.setMethodCallHandler(handler)

# Call the setup function to initialize the channel
setup_channel()