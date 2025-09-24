import os
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

PORT = int(os.environ.get('PORT', 5000))
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'production.db')

def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SportsCRM - Corrida Construai</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .section { background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .btn { background: #667eea; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #5a6fd8; }
        .contact-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 15px; }
        .contact-card { background: #f8f9ff; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea; }
        .loading { text-align: center; padding: 20px; color: #666; }
        .success { color: #28a745; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏃‍♂️ SportsCRM - Corrida Construai</h1>
            <p>Sistema de Gestão da 1ª Corrida Construai - Guaranésia, MG</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="events-count">-</div>
                <div>Eventos Ativos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="participants-count">-</div>
                <div>Participantes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="satisfaction-rate">-</div>
                <div>Satisfação</div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Painel de Controle</h2>
            <button class="btn" onclick="loadContacts()">📋 Carregar Contatos</button>
            <button class="btn" onclick="loadEvents()">🏃‍♂️ Carregar Eventos</button>
            <button class="btn" onclick="loadStats()">📊 Atualizar Estatísticas</button>
            <button class="btn" onclick="testWASeller()">🚀 Testar WASeller</button>
        </div>

        <div class="section">
            <h2>👥 Participantes da Corrida</h2>
            <div id="contacts-container" class="loading">Clique em "Carregar Contatos" para ver os participantes</div>
        </div>

        <div class="section">
            <h2>🏃‍♂️ Eventos</h2>
            <div id="events-container" class="loading">Clique em "Carregar Eventos" para ver os eventos</div>
        </div>

        <div class="section">
            <h2>🔗 API WASeller</h2>
            <p><strong>Webhook:</strong> POST /api/waseller/webhook</p>
            <p><strong>Contatos:</strong> POST /api/waseller/contacts</p>
            <p><strong>Listar:</strong> GET /api/contacts</p>
            <div id="api-result"></div>
        </div>
    </div>

    <script>
        async function loadStats() {
            try {
                const response = await fetch('/api/dashboard/stats');
                const stats = await response.json();
                document.getElementById('events-count').textContent = stats.activeEvents || 0;
                document.getElementById('participants-count').textContent = stats.totalParticipants || 0;
                document.getElementById('satisfaction-rate').textContent = (stats.satisfactionRate || 0) + '%';
            } catch (error) {
                console.error('Erro:', error);
            }
        }

        async function loadContacts() {
            const container = document.getElementById('contacts-container');
            container.innerHTML = '<div class="loading">Carregando...</div>';
            
            try {
                const response = await fetch('/api/contacts');
                const contacts = await response.json();
                
                let html = '<div class="contact-grid">';
                contacts.slice(0, 12).forEach(contact => {
                    html += `
                        <div class="contact-card">
                            <strong>${contact.name}</strong><br>
                            📧 ${contact.email}<br>
                            📱 ${contact.phone}<br>
                            📍 ${contact.location}<br>
                            🏃‍♂️ ${contact.sport}
                        </div>
                    `;
                });
                html += '</div>';
                html += `<p class="success">✅ Total: ${contacts.length} participantes</p>`;
                container.innerHTML = html;
            } catch (error) {
                container.innerHTML = '<p>❌ Erro: ' + error.message + '</p>';
            }
        }

        async function loadEvents() {
            const container = document.getElementById('events-container');
            container.innerHTML = '<div class="loading">Carregando...</div>';
            
            try {
                const response = await fetch('/api/events');
                const events = await response.json();
                
                let html = '';
                events.forEach(event => {
                    html += `
                        <div class="contact-card">
                            <strong>${event.name}</strong><br>
                            📅 ${event.date} às ${event.time}<br>
                            📍 ${event.location}<br>
                            🏃‍♂️ ${event.sport}<br>
                            👥 ${event.current_participants}/${event.max_participants}<br>
                            🏢 ${event.organizer}
                        </div>
                    `;
                });
                html += `<p class="success">✅ Total: ${events.length} eventos</p>`;
                container.innerHTML = html;
            } catch (error) {
                container.innerHTML = '<p>❌ Erro: ' + error.message + '</p>';
            }
        }

        async function testWASeller() {
            try {
                const testData = {
                    name: "Teste WASeller",
                    email: "teste@waseller.com",
                    whatsappNumber: "+5535999888777",
                    sport: "Corrida",
                    location: "Guaranésia, MG"
                };
                
                const response = await fetch('/api/waseller/contacts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(testData)
                });
                
                const result = await response.json();
                document.getElementById('api-result').innerHTML = 
                    `<p class="success">✅ WASeller OK! ID: ${result.id}</p>`;
            } catch (error) {
                document.getElementById('api-result').innerHTML = 
                    `<p>❌ Erro: ${error.message}</p>`;
            }
        }

        window.onload = loadStats;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
    conn = get_db()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(contact) for contact in contacts])

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db()
    events = conn.execute('SELECT * FROM events ORDER BY date DESC').fetchall()
    conn.close()
    return jsonify([dict(event) for event in events])

@app.route('/api/dashboard/stats', methods=['GET'])
def dashboard_stats():
    conn = get_db()
    events_count = conn.execute('SELECT COUNT(*) FROM events WHERE status = "confirmed"').fetchone()[0]
    participants_count = conn.execute('SELECT COUNT(*) FROM contacts WHERE status = "active"').fetchone()[0]
    conn.close()
    
    return jsonify({
        'activeEvents': events_count,
        'totalParticipants': participants_count,
        'satisfactionRate': 95
    })

@app.route('/api/waseller/contacts', methods=['POST'])
def sync_waseller():
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    sql = "INSERT INTO contacts (name, email, phone, contact_type, sport, location, status) VALUES (?, ?, ?, ?, ?, ?, ?)"
    values = (data.get('name'), data.get('email'), data.get('whatsappNumber'), 'fan',
              data.get('sport', 'Geral'), data.get('location', 'Brasil'), 'active')
    
    cursor.execute(sql, values)
    contact_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({'id': contact_id, 'message': 'Contato sincronizado'})

@app.route('/api/waseller/webhook', methods=['POST'])
def waseller_webhook():
    data = request.get_json()
    return jsonify({'status': 'success', 'message': 'Webhook processado'})

@app.route('/api/info', methods=['GET'])
def api_info():
    return jsonify({
        'name': 'SportsCRM - Corrida Construai',
        'version': '1.0.0',
        'environment': 'production',
        'description': 'CRM da 1ª Corrida Construai - Guaranésia, MG'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
