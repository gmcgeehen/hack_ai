import pyttsx3

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set properties (optional)
engine.setProperty("rate", 150)  # Speed of speech
engine.setProperty("volume", 1.0)  # Volume (0.0 to 1.0)

# Get available voices (optional debug)
voices = engine.getProperty("voices")
for index, voice in enumerate(voices):
    print(f"Voice {index}: {voice.name} - {voice.id}")

# Set a specific voice (optional, change index if needed)
if voices:
    engine.setProperty("voice", voices[120].id)

# Speak some text
engine.say("Hello Grant, this is a test of the text-to-speech engine.")
engine.runAndWait()