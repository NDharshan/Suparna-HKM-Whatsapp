from flask import Flask, request, jsonify, render_template
import requests, os
import csv

# Initialize Flask app
app = Flask(__name__)

# Global Variables (Fill these in with your credentials and API details)
WHATSAPP_API_URL = "https://graph.facebook.com/v15.0/528076093712698/messages"
ACCESS_TOKEN = r"EAAbvTByDyZA0BO6t79PSuZCFzBEpFD1ohsl5431OLJ0gHzvDysrZAOBe1tlYo0x1ZCOR0JDjACkLO6bYZC408QYjzjYer3aIZAPZCFDQxhScrdUl0CxO0iDJRbZBOcbTaVpl0Ej57oXXVn8OtB1vlZAGmjSlS1WZCoMZAofAps9VpPj3K3DXZAXkAHVOK40dGLbmWiN9RCCn3uuQYdI2WfkWErKMyJM0EbOL7rxloegZD"
CSV_FILE_PATH = r"D:\CustomCode\suparna-flask\contacts.csv"  # Path to your contact list CSV
# Configuration
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Helper function to read contacts from the CSV
def get_contacts():
    contacts = []
    try:
        with open(CSV_FILE_PATH, mode='r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                contacts.append(row)
    except Exception as e:
        print(f"Error reading contacts file: {e}")
    return contacts

# Route to send messages to all contacts
@app.route('/send_messages', methods=['POST'])
def send_messages():
    message_body = request.json.get('message')  # Message text from the request
    if not message_body:
        return jsonify({"error": "Message body is required"}), 400

    contacts = get_contacts()
    if not contacts:
        return jsonify({"error": "No contacts found"}), 400

    responses = []
    for contact in contacts:
        phone_number = contact.get("phone")
        if phone_number:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message_body}
            }
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
                responses.append({
                    "phone": phone_number,
                    "status": response.status_code,
                    "response": response.json()
                })
            except Exception as e:
                responses.append({
                    "phone": phone_number,
                    "status": "failed",
                    "error": str(e)
                })

    return jsonify({"results": responses})

# Route to send media (image, video, pdf)
@app.route('/send_media', methods=['POST'])
def send_media():
    message = request.form.get('message')
    media = request.files.get('media')
    if not message and not media:
        return jsonify({"error": "Message or media file is required"}), 400
    
    contacts = get_contacts()
    if not contacts:
        return jsonify({"error": "No contacts found"}), 400
    
    # Save media locally
    media_filename = None
    if media:
        media_filename = os.path.join(app.config['UPLOAD_FOLDER'], media.filename)
        media.save(media_filename)

    responses = []
    for contact in contacts:
        phone_number = contact.get("phone")
        if phone_number:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "document" if media_filename else "text",
                "text": {"body": message} if message else None,
                "document": {"link": media_filename} if media_filename else None
            }
            headers = {
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
                responses.append({
                    "phone": phone_number,
                    "status": response.status_code,
                    "response": response.json()
                })
            except Exception as e:
                responses.append({
                    "phone": phone_number,
                    "status": "failed",
                    "error": str(e)
                })

    return jsonify({"results": responses})

# Serve the frontend HTML
@app.route('/')
def index():
    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)